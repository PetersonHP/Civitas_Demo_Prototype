"""
Tests for the AI dispatcher agent service.
"""

import os
import pytest
from unittest.mock import Mock, patch

from src.services.dispatcher_agent import dispatch_ticket_with_ai


def test_dispatch_ticket_with_ai_missing_api_key():
    """Test that dispatch fails without API key."""
    ticket = {
        "ticket_subject": "Test",
        "ticket_body": "Test body",
        "location_coordinates": {"lat": 40.7128, "lng": -74.0060},
        "origin": "web form"
    }
    mock_db = Mock()

    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="API key is required"):
            dispatch_ticket_with_ai(ticket, mock_db)


def test_dispatch_ticket_with_ai_missing_fields():
    """Test that dispatch validates required ticket fields."""
    incomplete_ticket = {
        "ticket_subject": "Test"
        # Missing other required fields
    }
    mock_db = Mock()

    with pytest.raises(ValueError, match="Missing required ticket field"):
        dispatch_ticket_with_ai(incomplete_ticket, mock_db, api_key="test-key")


@pytest.mark.skipif(
    "ANTHROPIC_API_KEY" not in os.environ,
    reason="Requires ANTHROPIC_API_KEY environment variable"
)
def test_dispatch_ticket_integration():
    """
    Integration test with real API (requires ANTHROPIC_API_KEY).
    This test is skipped by default unless the API key is set.
    """
    from src.database import SessionLocal

    ticket = {
        "ticket_subject": "Pothole on Main Street",
        "ticket_body": "Large pothole at Main St and 5th Ave, approximately 12 inches wide",
        "location_coordinates": {"lat": 40.7580, "lng": -73.9855},
        "origin": "phone"
    }

    db = SessionLocal()
    try:
        result = dispatch_ticket_with_ai(ticket, db)

        # Validate output structure
        assert "status" in result
        assert "priority" in result
        assert "user_assignees" in result
        assert "crew_assignees" in result
        assert "labels" in result
        assert "comment" in result
        assert "comment_body" in result["comment"]

        # Validate field values
        assert result["status"] == "awaiting response"
        assert result["priority"] in ["high", "medium", "low"]
        assert isinstance(result["user_assignees"], list)
        assert isinstance(result["crew_assignees"], list)
        assert isinstance(result["labels"], list)

        print(f"✓ Dispatch successful - Priority: {result['priority']}")
        print(f"✓ Assigned {len(result['crew_assignees'])} crews")
        print(f"✓ Applied {len(result['labels'])} labels")

    finally:
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
