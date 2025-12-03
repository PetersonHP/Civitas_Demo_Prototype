"""
Tests for ticket CRUD operations.
"""
import pytest
from uuid import uuid4


class TestGetTickets:
    """Tests for GET /api/tickets/"""

    def test_get_tickets_empty(self, client):
        """Test getting tickets when database is empty."""
        response = client.get("/api/tickets/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_tickets(self, client, multiple_tickets):
        """Test getting all tickets."""
        response = client.get("/api/tickets/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_get_tickets_pagination(self, client, multiple_tickets):
        """Test ticket pagination."""
        # Get first page
        response = client.get("/api/tickets/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Get second page
        response = client.get("/api/tickets/?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Get third page
        response = client.get("/api/tickets/?skip=4&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_tickets_max_limit(self, client, multiple_tickets):
        """Test that limit is capped at 100."""
        response = client.get("/api/tickets/?limit=1000")
        assert response.status_code == 200
        data = response.json()
        # Should return all 5 tickets since we only have 5
        assert len(data) == 5

    def test_get_tickets_filter_by_status(self, client, multiple_tickets):
        """Test filtering tickets by status."""
        response = client.get("/api/tickets/?status=awaiting+response")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for ticket in data:
            assert ticket["status"] == "awaiting response"

        response = client.get("/api/tickets/?status=resolved")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_tickets_filter_by_priority(self, client, multiple_tickets):
        """Test filtering tickets by priority."""
        response = client.get("/api/tickets/?priority=high")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for ticket in data:
            assert ticket["priority"] == "high"

    def test_get_tickets_filter_by_status_and_priority(self, client, multiple_tickets):
        """Test filtering tickets by both status and priority."""
        response = client.get("/api/tickets/?status=resolved&priority=high")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "resolved"
        assert data[0]["priority"] == "high"


class TestGetTicketById:
    """Tests for GET /api/tickets/{ticket_id}"""

    def test_get_ticket_by_id(self, client, sample_ticket):
        """Test getting a specific ticket by ID."""
        response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["ticket_id"] == str(sample_ticket.ticket_id)
        assert data["ticket_subject"] == sample_ticket.ticket_subject
        assert data["ticket_body"] == sample_ticket.ticket_body
        assert data["origin"] == sample_ticket.origin.value
        assert data["status"] == sample_ticket.status.value
        assert data["priority"] == sample_ticket.priority.value

    def test_get_ticket_with_relations(self, client, sample_ticket_with_relations):
        """Test getting a ticket with all relations populated."""
        response = client.get(f"/api/tickets/{sample_ticket_with_relations.ticket_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["user_assignees"]) == 1
        assert len(data["crew_assignees"]) == 1
        assert len(data["labels"]) == 1
        assert data["reporter"] is not None

    def test_get_ticket_not_found(self, client):
        """Test getting a non-existent ticket."""
        fake_id = uuid4()
        response = client.get(f"/api/tickets/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestCreateTicket:
    """Tests for POST /api/tickets/"""

    def test_create_ticket_minimal(self, client, sample_user):
        """Test creating a ticket with minimal required fields."""
        ticket_data = {
            "ticket_subject": "New Issue",
            "ticket_body": "Description of the issue",
            "origin": "web form",
            "reporter_id": str(sample_user.user_id),
        }
        response = client.post("/api/tickets/", json=ticket_data)
        assert response.status_code == 201
        data = response.json()
        assert data["ticket_subject"] == ticket_data["ticket_subject"]
        assert data["ticket_body"] == ticket_data["ticket_body"]
        assert data["origin"] == ticket_data["origin"]
        assert data["status"] == "awaiting response"  # default
        assert data["priority"] == "medium"  # default

    def test_create_ticket_full(self, client, sample_user, sample_dispatcher, sample_crew, sample_label):
        """Test creating a ticket with all fields."""
        ticket_data = {
            "ticket_subject": "Complex Issue",
            "ticket_body": "Detailed description",
            "origin": "phone",
            "status": "response in progress",
            "priority": "high",
            "reporter_id": str(sample_user.user_id),
            "user_assignee_ids": [str(sample_dispatcher.user_id)],
            "crew_assignee_ids": [str(sample_crew.team_id)],
            "label_ids": [str(sample_label.label_id)],
            "location_coordinates": {"lat": 40.7128, "lng": -74.0060},
            "meta_data": {"source": "call_center", "priority_reason": "safety"},
        }
        response = client.post("/api/tickets/", json=ticket_data)
        assert response.status_code == 201
        data = response.json()
        assert data["ticket_subject"] == ticket_data["ticket_subject"]
        assert data["priority"] == "high"
        assert data["location_coordinates"]["lat"] == 40.7128
        assert data["location_coordinates"]["lng"] == -74.0060

    def test_create_ticket_anonymous(self, client):
        """Test creating a ticket without a reporter (anonymous)."""
        ticket_data = {
            "ticket_subject": "Anonymous Report",
            "ticket_body": "Issue reported anonymously",
            "origin": "text",
            "reporter_id": None,
        }
        response = client.post("/api/tickets/", json=ticket_data)
        assert response.status_code == 201
        data = response.json()
        assert data["reporter_id"] is None

    def test_create_ticket_invalid_reporter(self, client):
        """Test creating a ticket with non-existent reporter."""
        fake_id = uuid4()
        ticket_data = {
            "ticket_subject": "Test",
            "ticket_body": "Test body",
            "origin": "web form",
            "reporter_id": str(fake_id),
        }
        response = client.post("/api/tickets/", json=ticket_data)
        assert response.status_code == 400
        assert "reporter" in response.json()["detail"].lower()

    def test_create_ticket_invalid_assignee(self, client, sample_user):
        """Test creating a ticket with non-existent assignee."""
        fake_id = uuid4()
        ticket_data = {
            "ticket_subject": "Test",
            "ticket_body": "Test body",
            "origin": "web form",
            "reporter_id": str(sample_user.user_id),
            "user_assignee_ids": [str(fake_id)],
        }
        response = client.post("/api/tickets/", json=ticket_data)
        assert response.status_code == 400
        assert "assignee" in response.json()["detail"].lower()

    def test_create_ticket_invalid_crew(self, client, sample_user):
        """Test creating a ticket with non-existent crew."""
        fake_id = uuid4()
        ticket_data = {
            "ticket_subject": "Test",
            "ticket_body": "Test body",
            "origin": "web form",
            "reporter_id": str(sample_user.user_id),
            "crew_assignee_ids": [str(fake_id)],
        }
        response = client.post("/api/tickets/", json=ticket_data)
        assert response.status_code == 400
        assert "crew" in response.json()["detail"].lower()

    def test_create_ticket_invalid_label(self, client, sample_user):
        """Test creating a ticket with non-existent label."""
        fake_id = uuid4()
        ticket_data = {
            "ticket_subject": "Test",
            "ticket_body": "Test body",
            "origin": "web form",
            "reporter_id": str(sample_user.user_id),
            "label_ids": [str(fake_id)],
        }
        response = client.post("/api/tickets/", json=ticket_data)
        assert response.status_code == 400
        assert "label" in response.json()["detail"].lower()


class TestUpdateTicket:
    """Tests for PATCH /api/tickets/{ticket_id}"""

    def test_update_ticket_subject(self, client, sample_ticket):
        """Test updating ticket subject."""
        update_data = {"ticket_subject": "Updated Subject"}
        response = client.patch(f"/api/tickets/{sample_ticket.ticket_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["ticket_subject"] == "Updated Subject"

    def test_update_ticket_status(self, client, sample_ticket):
        """Test updating ticket status."""
        update_data = {"status": "resolved"}
        response = client.patch(f"/api/tickets/{sample_ticket.ticket_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"

    def test_update_ticket_priority(self, client, sample_ticket):
        """Test updating ticket priority."""
        update_data = {"priority": "high"}
        response = client.patch(f"/api/tickets/{sample_ticket.ticket_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "high"

    def test_update_ticket_multiple_fields(self, client, sample_ticket):
        """Test updating multiple ticket fields."""
        update_data = {
            "ticket_subject": "New Subject",
            "ticket_body": "New Body",
            "status": "response in progress",
            "priority": "low",
        }
        response = client.patch(f"/api/tickets/{sample_ticket.ticket_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["ticket_subject"] == "New Subject"
        assert data["ticket_body"] == "New Body"
        assert data["status"] == "response in progress"
        assert data["priority"] == "low"

    def test_update_ticket_assignees(self, client, sample_ticket, sample_dispatcher):
        """Test updating ticket assignees."""
        update_data = {"user_assignee_ids": [str(sample_dispatcher.user_id)]}
        response = client.patch(f"/api/tickets/{sample_ticket.ticket_id}", json=update_data)
        assert response.status_code == 200

    def test_update_ticket_location(self, client, sample_ticket):
        """Test updating ticket location."""
        update_data = {"location_coordinates": {"lat": 34.0522, "lng": -118.2437}}
        response = client.patch(f"/api/tickets/{sample_ticket.ticket_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["location_coordinates"]["lat"] == 34.0522
        assert data["location_coordinates"]["lng"] == -118.2437

    def test_update_ticket_not_found(self, client):
        """Test updating a non-existent ticket."""
        fake_id = uuid4()
        update_data = {"ticket_subject": "Test"}
        response = client.patch(f"/api/tickets/{fake_id}", json=update_data)
        assert response.status_code == 404


class TestUpdateTicketStatus:
    """Tests for PATCH /api/tickets/{ticket_id}/status"""

    def test_update_status_quick(self, client, sample_ticket):
        """Test quick status update endpoint."""
        update_data = {"status": "resolved"}
        response = client.patch(f"/api/tickets/{sample_ticket.ticket_id}/status", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"

    def test_update_status_not_found(self, client):
        """Test status update on non-existent ticket."""
        fake_id = uuid4()
        update_data = {"status": "resolved"}
        response = client.patch(f"/api/tickets/{fake_id}/status", json=update_data)
        assert response.status_code == 404


class TestDeleteTicket:
    """Tests for DELETE /api/tickets/{ticket_id}"""

    def test_delete_ticket(self, client, sample_ticket):
        """Test deleting a ticket."""
        ticket_id = sample_ticket.ticket_id
        response = client.delete(f"/api/tickets/{ticket_id}")
        assert response.status_code == 204

        # Verify ticket is deleted
        get_response = client.get(f"/api/tickets/{ticket_id}")
        assert get_response.status_code == 404

    def test_delete_ticket_not_found(self, client):
        """Test deleting a non-existent ticket."""
        fake_id = uuid4()
        response = client.delete(f"/api/tickets/{fake_id}")
        assert response.status_code == 404
