"""
AI-Powered Ticket Dispatcher Service

This module provides an AI agent that triages 311 service tickets using a reasoning model.
The agent analyzes ticket details, assesses priority, assigns crews and staff, categorizes
with labels, and provides responses to citizen reporters.

Dependencies:
    - anthropic: Required for Claude API integration
      Install with: pip install anthropic
"""

import json
import os
from typing import Dict, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from anthropic import Anthropic

# Import router functions that will be used as tools
from ..routers.labels import get_labels as router_get_labels
from ..routers.users import get_users as router_get_users
from ..routers.crews import get_nearest_crews as router_get_nearest_crews
from ..models.civitas import SupportCrewType


def load_dispatcher_system_prompt() -> str:
    """
    Load the dispatcher system prompt from the markdown file.

    Returns:
        str: The complete system prompt text
    """
    prompt_path = Path(__file__).parent.parent / "prompts" / "dispatcher_system.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Dispatcher system prompt not found at {prompt_path}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def create_tool_definitions() -> List[Dict[str, Any]]:
    """
    Create tool definitions for the AI agent following Anthropic's tool format.

    Returns:
        List[Dict]: Tool definitions for get_labels, get_users, and get_nearest_crews
    """
    return [
        {
            "name": "get_labels",
            "description": (
                "Find categorization labels for tickets. Search matches against label_name "
                "and label_description (case-insensitive, partial match). Query multiple times "
                "with different search terms to find all relevant labels."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": (
                            "String to search label names and descriptions. "
                            "Common NYC 311 categories: 'pothole', 'tree', 'sanitation', "
                            "'street sign', 'drainage', 'snow removal', 'hazard', "
                            "'infrastructure', 'safety', 'urgent'"
                        )
                    }
                },
                "required": ["search"]
            }
        },
        {
            "name": "get_users",
            "description": (
                "Find individual staff members for assignment. Search matches against user names, "
                "emails, and phone numbers (case-insensitive, partial match). "
                "Only returns users with status 'active'."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": (
                            "String to search user names, emails, and phone numbers. "
                            "Examples: 'supervisor', 'Hugh Peterson', 'PetersonHughP@gmail.com'"
                        )
                    }
                },
                "required": ["search"]
            }
        },
        {
            "name": "get_nearest_crews",
            "description": (
                "Find work crews near the incident location. Returns up to 5 nearest crews "
                "sorted by distance. Only assign crews with status 'active'. Prefer the closest "
                "available crew (first result)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "lat": {
                        "type": "number",
                        "description": "Latitude of the incident (use from ticket location_coordinates)"
                    },
                    "lng": {
                        "type": "number",
                        "description": "Longitude of the incident (use from ticket location_coordinates)"
                    },
                    "crew_type": {
                        "type": "string",
                        "enum": [
                            "pothole crew",
                            "drain crew",
                            "tree crew",
                            "sign crew",
                            "snow crew",
                            "sanitation crew"
                        ],
                        "description": (
                            "Type of crew needed. Choose based on issue type: "
                            "pothole crew (road damage), drain crew (flooding/drainage), "
                            "tree crew (trees/branches), sign crew (street signs), "
                            "snow crew (snow/ice), sanitation crew (trash/litter)"
                        )
                    }
                },
                "required": ["lat", "lng", "crew_type"]
            }
        }
    ]


def log_conversation_to_file(
    ticket: Dict[str, Any],
    messages: List[Dict[str, Any]],
    result: Dict[str, Any],
    log_dir: str = None
) -> None:
    """
    Log the AI conversation to a file for debugging and auditing.

    Args:
        ticket: Original ticket data
        messages: Full conversation history with the AI
        result: Final dispatcher result
        log_dir: Directory to save logs (defaults to backend/logs/dispatcher)
    """
    # Set default log directory
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / "logs" / "dispatcher"
    else:
        log_dir = Path(log_dir)

    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp and filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ticket_subject = ticket.get("ticket_subject", "unknown")[:50]  # Truncate to 50 chars
    # Clean filename (remove invalid characters)
    safe_subject = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in ticket_subject)
    filename = f"{timestamp}_{safe_subject}.json"
    log_path = log_dir / filename

    # Also maintain a "latest.json" file
    latest_path = log_dir / "latest.json"

    # Prepare log data
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "ticket": ticket,
        "conversation": [],
        "result": result
    }

    # Format conversation messages for readability
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", [])

        # Handle different content formats
        if isinstance(content, str):
            log_data["conversation"].append({
                "role": role,
                "content": content
            })
        elif isinstance(content, list):
            formatted_content = []
            for block in content:
                if isinstance(block, dict):
                    block_type = block.get("type", "unknown")

                    if block_type == "text":
                        formatted_content.append({
                            "type": "text",
                            "text": block.get("text", "")
                        })
                    elif block_type == "tool_use":
                        formatted_content.append({
                            "type": "tool_use",
                            "name": block.get("name", ""),
                            "input": block.get("input", {})
                        })
                    elif block_type == "tool_result":
                        formatted_content.append({
                            "type": "tool_result",
                            "tool_use_id": block.get("tool_use_id", ""),
                            "content": block.get("content", "")
                        })
                    else:
                        # Handle Anthropic API response blocks
                        formatted_content.append({
                            "type": str(block_type),
                            "data": str(block)
                        })
                else:
                    formatted_content.append({"raw": str(block)})

            log_data["conversation"].append({
                "role": role,
                "content": formatted_content
            })

    # Write to timestamped file
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

    # Write to latest.json (overwrite)
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)


def execute_tool(tool_name: str, tool_input: Dict[str, Any], db: Session) -> Any:
    """
    Execute a tool function and return its result.

    Args:
        tool_name: Name of the tool to execute
        tool_input: Input parameters for the tool
        db: Database session

    Returns:
        Tool execution result

    Note:
        If a database error occurs, the transaction is rolled back to allow
        subsequent queries to execute.
    """
    try:
        return _execute_tool_internal(tool_name, tool_input, db)
    except Exception as e:
        # Rollback transaction on error to allow subsequent queries
        db.rollback()
        raise


def _execute_tool_internal(tool_name: str, tool_input: Dict[str, Any], db: Session) -> Any:
    """Internal tool execution logic."""
    if tool_name == "get_labels":
        labels = router_get_labels(
            search=tool_input.get("search"),
            db=db
        )
        # Convert to dict format for JSON serialization
        return [
            {
                "label_id": str(label.label_id),
                "label_name": label.label_name,
                "label_description": label.label_description,
                "color_hex": label.color_hex
            }
            for label in labels
        ]

    elif tool_name == "get_users":
        users = router_get_users(
            search=tool_input.get("search"),
            db=db
        )
        # Filter only active users and convert to dict
        return [
            {
                "user_id": str(user.user_id),
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "phone_number": user.phone_number,
                "status": user.status.value
            }
            for user in users
            if user.status.value == "active"
        ]

    elif tool_name == "get_nearest_crews":
        # Convert crew_type string to enum
        crew_type_str = tool_input.get("crew_type")
        try:
            crew_type_enum = SupportCrewType(crew_type_str)
        except ValueError:
            return {"error": f"Invalid crew_type: {crew_type_str}"}

        crews = router_get_nearest_crews(
            lat=tool_input.get("lat"),
            lng=tool_input.get("lng"),
            crew_type=crew_type_enum,
            db=db
        )
        # Convert to dict format
        return [
            {
                "team_id": str(crew.get("team_id")),
                "team_name": crew.get("team_name"),
                "crew_type": crew.get("crew_type"),
                "status": crew.get("status"),
                "location_coordinates": crew.get("location_coordinates"),
                "distance": crew.get("distance")
            }
            for crew in crews
        ]

    else:
        return {"error": f"Unknown tool: {tool_name}"}


def dispatch_ticket_with_ai(
    ticket: Dict[str, Any],
    db: Session,
    api_key: str = None,
    model: str = "claude-haiku-4-5-20251001"
) -> Dict[str, Any]:
    """
    Process a ticket using the AI dispatcher agent.

    This function takes a ticket as input, uses Claude with the dispatcher system prompt,
    provides tools for querying labels, users, and crews, and returns the JSON output
    specified in the system prompt.

    Args:
        ticket: Dictionary containing ticket information with fields:
            - ticket_subject (str): Brief title/summary
            - ticket_body (str): Detailed description
            - location_coordinates (dict): {lat: float, lng: float}
            - origin (str): "phone", "web form", or "text"
            - reporter_id (UUID, optional): UUID of reporting citizen
        db: SQLAlchemy database session for tool queries
        api_key: Anthropic API key (if not provided, reads from ANTHROPIC_API_KEY env var)
        model: Claude model to use (default: claude-3-7-sonnet-20250219)

    Returns:
        Dict containing:
            - status (str): "awaiting response"
            - priority (str): "high", "medium", or "low"
            - user_assignees (List[str]): List of user UUIDs
            - crew_assignees (List[str]): List of crew UUIDs
            - labels (List[str]): List of label UUIDs
            - comment (dict): {"comment_body": str}

    Raises:
        ValueError: If API key is missing or ticket format is invalid
        Exception: If AI agent fails to produce valid output
    """
    # Get API key
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError(
            "Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable "
            "or pass api_key parameter."
        )

    # Validate ticket input
    required_fields = ["ticket_subject", "ticket_body", "location_coordinates", "origin"]
    for field in required_fields:
        if field not in ticket:
            raise ValueError(f"Missing required ticket field: {field}")

    # Initialize Anthropic client
    client = Anthropic(api_key=api_key)

    # Load system prompt
    system_prompt = load_dispatcher_system_prompt()

    # Create tool definitions
    tools = create_tool_definitions()

    # Format the ticket data for the agent
    ticket_message = f"""Please process the following ticket:

**Ticket Subject**: {ticket['ticket_subject']}

**Ticket Body**: {ticket['ticket_body']}

**Location Coordinates**: {ticket['location_coordinates']}

**Origin**: {ticket['origin']}

**Reporter ID**: {ticket.get('reporter_id', 'N/A')}
"""

    # Initialize conversation
    messages = [{"role": "user", "content": ticket_message}]

    # Agent loop - handle tool calls iteratively
    max_iterations = 20  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Call Claude API
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            tools=tools,
            messages=messages
        )

        # Check if we have a final response
        if response.stop_reason == "end_turn":
            # Extract the final text response (should be JSON)
            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text

            # Try to parse as JSON
            try:
                # First, try parsing the entire response as JSON
                result = json.loads(final_text)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from markdown code blocks or mixed text
                import re

                # Try to find JSON within markdown code blocks
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', final_text, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        pass
                else:
                    # Try to find a JSON object in the text (look for { ... })
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', final_text, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group(0))
                        except json.JSONDecodeError:
                            pass

                # If we still don't have a result, raise the original error
                if 'result' not in locals():
                    raise Exception(f"AI agent did not return valid JSON: {final_text}")

            # Validate the output structure
            required_output_fields = [
                "status", "priority", "user_assignees",
                "crew_assignees", "labels", "comment", "justification"
            ]
            for field in required_output_fields:
                if field not in result:
                    raise ValueError(f"Missing required output field: {field}")

            # Log the conversation to file
            try:
                log_conversation_to_file(ticket, messages, result)
            except Exception as log_error:
                # Don't fail the entire operation if logging fails
                print(f"Warning: Failed to log conversation: {log_error}")

            return result

        # Handle tool use
        elif response.stop_reason == "tool_use":
            # Add assistant's response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Execute tools and collect results
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    # Execute the tool
                    try:
                        tool_result = execute_tool(tool_name, tool_input, db)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps(tool_result)
                        })
                    except Exception as e:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps({"error": str(e)}),
                            "is_error": True
                        })

            # Add tool results to messages
            messages.append({"role": "user", "content": tool_results})

        else:
            raise Exception(f"Unexpected stop reason: {response.stop_reason}")

    raise Exception(f"Agent exceeded maximum iterations ({max_iterations})")


# Convenience function for direct ticket model usage
def dispatch_ticket_model(ticket_model, db: Session, api_key: str = None) -> Dict[str, Any]:
    """
    Dispatch a ticket using its SQLAlchemy model object.

    Args:
        ticket_model: SQLAlchemy Ticket model instance
        db: Database session
        api_key: Optional Anthropic API key

    Returns:
        Dispatcher agent output dictionary
    """
    # Convert ticket model to dictionary format
    ticket_dict = {
        "ticket_subject": ticket_model.ticket_subject,
        "ticket_body": ticket_model.ticket_body,
        "origin": ticket_model.origin.value,
        "reporter_id": str(ticket_model.reporter_id) if ticket_model.reporter_id else None,
    }

    # Handle location coordinates
    if ticket_model.location_coordinates:
        from ..routers.tickets import serialize_location
        ticket_dict["location_coordinates"] = serialize_location(ticket_model.location_coordinates)
    else:
        ticket_dict["location_coordinates"] = None

    return dispatch_ticket_with_ai(ticket_dict, db, api_key)
