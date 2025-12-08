#!/usr/bin/env python3
"""
Transform NYC 311 data to match the sample_tickets.csv schema.
Uses free Groq API to generate ticket subjects and bodies.
"""

import csv
import os
import time
from typing import Dict, Any
from groq import Groq
from dotenv import load_dotenv


def map_origin(channel_type: str) -> str:
    """Map NYC 311 channel type to origin."""
    channel_map = {
        'PHONE': 'phone',
        'ONLINE': 'web form',
        'MOBILE': 'text',
        'OTHER': 'phone'
    }
    return channel_map.get(channel_type.upper(), 'web form')


def map_status(nyc_status: str) -> str:
    """Map NYC 311 status to ticket status."""
    # status = nyc_status.lower()
    # if 'progress' in status or 'assigned' in status or 'open' in status:
    #     return 'response in progress'
    # elif 'closed' in status or 'completed' in status:
    #     return 'resolved'
    # else:
    #     return 'awaiting response'
    return 'awaiting response'


def determine_priority(complaint_type: str, descriptor: str) -> str:
    """Determine priority based on complaint type and descriptor."""
    complaint_lower = complaint_type.lower()
    descriptor_lower = descriptor.lower()

    # High priority keywords
    high_priority = [
        'water main', 'broken', 'emergency', 'dangerous', 'hazard',
        'flooding', 'fire', 'gas', 'blocked', 'traffic signal',
        'street condition', 'failed', 'sidewalk condition'
    ]

    # Low priority keywords
    low_priority = [
        'graffiti', 'noise', 'permit', 'license', 'certificate',
        'restaurant status', 'smoking', 'vaping', 'cone'
    ]

    combined = complaint_lower + ' ' + descriptor_lower

    if any(keyword in combined for keyword in high_priority):
        return 'high'
    elif any(keyword in combined for keyword in low_priority):
        return 'low'
    else:
        return 'medium'


def generate_ticket_with_llm(client: Groq, row: Dict[str, str], unique_key: str, max_retries: int = 3) -> Dict[str, str]:
    """Generate ticket subject and body using Groq LLM API with retry logic."""
    # Prepare context for the LLM
    complaint_type = row.get('complaint_type', 'Unknown')
    descriptor = row.get('descriptor', 'No descriptor')
    borough = row.get('borough', 'NYC')
    address = row.get('incident_address', '')
    street_name = row.get('street_name', '')
    cross_street_1 = row.get('cross_street_1', '')
    cross_street_2 = row.get('cross_street_2', '')
    location_type = row.get('location_type', '')
    incident_zip = row.get('incident_zip', '')

    # Build location string
    location_parts = []
    if address:
        location_parts.append(f"Address: {address}")
        if incident_zip:
            location_parts.append(f"ZIP: {incident_zip}")
    elif street_name:
        location_parts.append(f"Street: {street_name}")
        if cross_street_1 and cross_street_2:
            location_parts.append(f"between {cross_street_1} and {cross_street_2}")
    if borough:
        location_parts.append(f"Borough: {borough}")
    if location_type:
        location_parts.append(f"Location Type: {location_type}")

    location_str = ", ".join(location_parts) if location_parts else "Location not specified"

    # Create prompt for LLM
    prompt = f"""Generate a realistic 311 service request ticket based on the following information:

Complaint Type: {complaint_type}
Description: {descriptor}
Location: {location_str}

Generate:
1. A concise ticket subject line (one line, professional, do NOT include any ticket numbers or IDs)
2. A detailed ticket body (2-4 sentences describing the issue from a concerned citizen's perspective, natural language)

Format your response as:
SUBJECT: [your subject here]
BODY: [your body here]"""

    # Retry logic for rate limiting
    for attempt in range(max_retries):
        try:
            # Call Groq API
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates realistic 311 service request tickets. Keep subjects concise and bodies informative but brief."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",  # Free, fast model
                temperature=0.7,
                max_tokens=300
            )

            response = chat_completion.choices[0].message.content

            # Parse response
            subject = ""
            body = ""

            lines = response.strip().split('\n')
            for line in lines:
                if line.startswith('SUBJECT:'):
                    subject = line.replace('SUBJECT:', '').strip()
                elif line.startswith('BODY:'):
                    body = line.replace('BODY:', '').strip()

            # Fallback if parsing fails
            if not subject:
                subject = f"{complaint_type}: {descriptor} in {borough}"
            if not body:
                body = f"A {complaint_type.lower()} complaint regarding {descriptor.lower()} at {location_str}."

            # Explicitly add unique_key to subject
            subject = f"{subject} (unique_key: {unique_key})"

            return {"subject": subject, "body": body}

        except Exception as e:
            error_msg = str(e).lower()
            # Check if it's a rate limit error
            if 'rate' in error_msg or 'limit' in error_msg or '429' in error_msg:
                if attempt < max_retries - 1:
                    # Exponential backoff: 5s, 10s, 20s
                    wait_time = 5 * (2 ** attempt)
                    print(f"Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Rate limit exceeded after {max_retries} retries. Using fallback.")
            else:
                print(f"Error generating with LLM: {e}. Using fallback.")

            # Fallback to original logic (unique_key added explicitly)
            subject = f"{complaint_type}: {descriptor} in {borough} (unique_key: {unique_key})"
            body = create_ticket_body(row)
            return {"subject": subject, "body": body}

    # Should not reach here, but just in case (unique_key added explicitly)
    subject = f"{complaint_type}: {descriptor} in {borough} (unique_key: {unique_key})"
    body = create_ticket_body(row)
    return {"subject": subject, "body": body}


def create_ticket_subject(complaint_type: str, descriptor: str, borough: str, unique_key: str) -> str:
    """Create a ticket subject line."""
    return f"{complaint_type}: {descriptor} in {borough} (unique_key: {unique_key})"


def create_ticket_body(row: Dict[str, str]) -> str:
    """Create a detailed ticket body from NYC 311 data."""
    parts = []

    # Add main complaint description
    parts.append(f"A {row['complaint_type'].lower()} complaint has been filed regarding {row['descriptor'].lower()}.")

    # Add location details
    if row['incident_address']:
        location = f"Location: {row['incident_address']}"
        if row['incident_zip']:
            location += f", {row['incident_zip']}"
        if row['borough']:
            location += f" ({row['borough']})"
        parts.append(location)
    elif row['street_name']:
        location = f"Location: {row['street_name']}"
        if row['cross_street_1'] and row['cross_street_2']:
            location += f" between {row['cross_street_1']} and {row['cross_street_2']}"
        parts.append(location)

    # Add location type if available
    if row['location_type']:
        parts.append(f"Location type: {row['location_type']}")

    # # Add agency information
    # if row['agency_name']:
    #     parts.append(f"Assigned to: {row['agency_name']}")

    # # Add created date
    # if row['created_date']:
    #     parts.append(f"Reported: {row['created_date']}")

    return ' '.join(parts)


def transform_nyc_311_to_tickets(
    input_file: str,
    output_file: str,
    reporter_id: str = 'b3cdcf8f-3c7a-4001-b7fb-646e909d2fa9',
    use_llm: bool = True,
    groq_api_key: str = None
):
    """
    Transform NYC 311 data to sample tickets schema.

    Args:
        input_file: Path to NYC 311 CSV file
        output_file: Path to output CSV file
        reporter_id: Default reporter ID to use for all tickets
        use_llm: Whether to use LLM for generating subjects and bodies
        groq_api_key: Groq API key (if not provided, will use GROQ_API_KEY env var)
    """

    # Initialize Groq client if using LLM
    client = None
    if use_llm:
        api_key = groq_api_key or os.environ.get('GROQ_API_KEY')
        if not api_key:
            print("WARNING: No Groq API key found. Set GROQ_API_KEY environment variable or pass groq_api_key parameter.")
            print("Falling back to non-LLM generation.")
            use_llm = False
        else:
            client = Groq(api_key=api_key)
            print("Using Groq LLM for ticket generation...")

    # Read input file and transform
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        # Prepare output data
        output_rows = []
        row_count = 0

        for row in reader:
            # Skip rows without coordinates
            if not row.get('latitude') or not row.get('longitude'):
                continue

            # Skip rows with invalid coordinates
            try:
                lat = float(row['latitude'])
                lng = float(row['longitude'])
            except (ValueError, TypeError):
                continue

            unique_key = row.get('unique_key', 'N/A')

            # Generate subject and body with LLM or fallback
            if use_llm and client:
                generated = generate_ticket_with_llm(client, row, unique_key)
                ticket_subject = generated['subject']
                ticket_body = generated['body']

                row_count += 1
                if row_count % 10 == 0:
                    print(f"Processed {row_count} rows...")

                # Rate limiting: 30 requests per minute = 1 request every 2 seconds
                # Using 2.5 seconds to be safe and avoid hitting the limit
                time.sleep(2.5)
            else:
                ticket_subject = create_ticket_subject(
                    row.get('complaint_type', 'Unknown'),
                    row.get('descriptor', 'No descriptor'),
                    row.get('borough', 'NYC'),
                    unique_key
                )
                ticket_body = create_ticket_body(row)

            # Transform to target schema
            transformed = {
                'ticket_subject': ticket_subject,
                'ticket_body': ticket_body,
                'origin': map_origin(row.get('open_data_channel_type', '')),
                'status': map_status(row.get('status', '')),
                'priority': determine_priority(
                    row.get('complaint_type', ''),
                    row.get('descriptor', '')
                ),
                'reporter_id': reporter_id,
                'lat': lat,
                'lng': lng
            }

            output_rows.append(transformed)

    # Write output file
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        fieldnames = [
            'ticket_subject',
            'ticket_body',
            'origin',
            'status',
            'priority',
            'reporter_id',
            'lat',
            'lng'
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Transformation complete!")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"Rows processed: {len(output_rows)}")


if __name__ == '__main__':
    # Get paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(backend_dir, 'data')

    # Load environment variables from backend/.env
    env_path = os.path.join(backend_dir, '.env')
    load_dotenv(env_path)

    input_file = os.path.join(data_dir, 'nyc_311_data.csv')
    output_file = os.path.join(data_dir, 'nyc_311_transformed_tickets.csv')

    transform_nyc_311_to_tickets(input_file, output_file)
