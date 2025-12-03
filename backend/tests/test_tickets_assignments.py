"""
Tests for ticket assignment operations.
"""
import pytest
from uuid import uuid4


class TestAssignUsers:
    """Tests for POST /api/tickets/{ticket_id}/assign-users"""

    def test_assign_users_to_ticket(self, client, sample_ticket, sample_dispatcher):
        """Test assigning users to a ticket."""
        assign_data = {"user_ids": [str(sample_dispatcher.user_id)]}
        response = client.post(f"/api/tickets/{sample_ticket.ticket_id}/assign-users", json=assign_data)
        assert response.status_code == 200

        # Verify assignment by getting the ticket
        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        data = get_response.json()
        assert len(data["user_assignees"]) == 1
        assert data["user_assignees"][0]["user_id"] == str(sample_dispatcher.user_id)

    def test_assign_multiple_users(self, client, sample_ticket, sample_dispatcher, sample_user):
        """Test assigning multiple users to a ticket."""
        assign_data = {"user_ids": [str(sample_dispatcher.user_id), str(sample_user.user_id)]}
        response = client.post(f"/api/tickets/{sample_ticket.ticket_id}/assign-users", json=assign_data)
        assert response.status_code == 200

        # Verify assignments
        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        data = get_response.json()
        assert len(data["user_assignees"]) == 2

    def test_assign_users_replaces_existing(self, client, sample_ticket_with_relations, sample_user):
        """Test that assigning users replaces existing assignments."""
        # Verify initial assignment
        get_response = client.get(f"/api/tickets/{sample_ticket_with_relations.ticket_id}")
        initial_data = get_response.json()
        assert len(initial_data["user_assignees"]) == 1

        # Assign different user
        assign_data = {"user_ids": [str(sample_user.user_id)]}
        response = client.post(
            f"/api/tickets/{sample_ticket_with_relations.ticket_id}/assign-users",
            json=assign_data
        )
        assert response.status_code == 200

        # Verify replacement
        get_response = client.get(f"/api/tickets/{sample_ticket_with_relations.ticket_id}")
        data = get_response.json()
        assert len(data["user_assignees"]) == 1
        assert data["user_assignees"][0]["user_id"] == str(sample_user.user_id)

    def test_assign_users_empty_list(self, client, sample_ticket_with_relations):
        """Test assigning empty user list removes all assignments."""
        assign_data = {"user_ids": []}
        response = client.post(
            f"/api/tickets/{sample_ticket_with_relations.ticket_id}/assign-users",
            json=assign_data
        )
        assert response.status_code == 200

        # Verify all users removed
        get_response = client.get(f"/api/tickets/{sample_ticket_with_relations.ticket_id}")
        data = get_response.json()
        assert len(data["user_assignees"]) == 0

    def test_assign_users_ticket_not_found(self, client, sample_dispatcher):
        """Test assigning users to non-existent ticket."""
        fake_id = uuid4()
        assign_data = {"user_ids": [str(sample_dispatcher.user_id)]}
        response = client.post(f"/api/tickets/{fake_id}/assign-users", json=assign_data)
        assert response.status_code == 404

    def test_assign_users_invalid_user(self, client, sample_ticket):
        """Test assigning non-existent user."""
        fake_id = uuid4()
        assign_data = {"user_ids": [str(fake_id)]}
        response = client.post(f"/api/tickets/{sample_ticket.ticket_id}/assign-users", json=assign_data)
        assert response.status_code == 400
        assert "user" in response.json()["detail"].lower()


class TestAssignCrews:
    """Tests for POST /api/tickets/{ticket_id}/assign-crews"""

    def test_assign_crews_to_ticket(self, client, sample_ticket, sample_crew):
        """Test assigning crews to a ticket."""
        assign_data = {"crew_ids": [str(sample_crew.team_id)]}
        response = client.post(f"/api/tickets/{sample_ticket.ticket_id}/assign-crews", json=assign_data)
        assert response.status_code == 200

        # Verify assignment
        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        data = get_response.json()
        assert len(data["crew_assignees"]) == 1
        assert data["crew_assignees"][0]["team_id"] == str(sample_crew.team_id)

    def test_assign_crews_replaces_existing(self, client, sample_ticket_with_relations, db_session, sample_dispatcher):
        """Test that assigning crews replaces existing assignments."""
        from src.models.civitas import SupportCrew, SupportCrewType, SupportCrewStatus

        # Create a new crew
        new_crew = SupportCrew(
            team_id=uuid4(),
            team_name="Different Crew",
            crew_type=SupportCrewType.DRAIN_CREW,
            status=SupportCrewStatus.ACTIVE,
        )
        db_session.add(new_crew)
        db_session.commit()
        db_session.refresh(new_crew)

        # Assign new crew
        assign_data = {"crew_ids": [str(new_crew.team_id)]}
        response = client.post(
            f"/api/tickets/{sample_ticket_with_relations.ticket_id}/assign-crews",
            json=assign_data
        )
        assert response.status_code == 200

        # Verify replacement
        get_response = client.get(f"/api/tickets/{sample_ticket_with_relations.ticket_id}")
        data = get_response.json()
        assert len(data["crew_assignees"]) == 1
        assert data["crew_assignees"][0]["team_id"] == str(new_crew.team_id)

    def test_assign_crews_ticket_not_found(self, client, sample_crew):
        """Test assigning crews to non-existent ticket."""
        fake_id = uuid4()
        assign_data = {"crew_ids": [str(sample_crew.team_id)]}
        response = client.post(f"/api/tickets/{fake_id}/assign-crews", json=assign_data)
        assert response.status_code == 404

    def test_assign_crews_invalid_crew(self, client, sample_ticket):
        """Test assigning non-existent crew."""
        fake_id = uuid4()
        assign_data = {"crew_ids": [str(fake_id)]}
        response = client.post(f"/api/tickets/{sample_ticket.ticket_id}/assign-crews", json=assign_data)
        assert response.status_code == 400
        assert "crew" in response.json()["detail"].lower()


class TestUnassignUser:
    """Tests for DELETE /api/tickets/{ticket_id}/unassign-user/{user_id}"""

    def test_unassign_user(self, client, sample_ticket_with_relations, sample_dispatcher):
        """Test unassigning a user from a ticket."""
        response = client.delete(
            f"/api/tickets/{sample_ticket_with_relations.ticket_id}/unassign-user/{sample_dispatcher.user_id}"
        )
        assert response.status_code == 200

        # Verify unassignment
        get_response = client.get(f"/api/tickets/{sample_ticket_with_relations.ticket_id}")
        data = get_response.json()
        assert len(data["user_assignees"]) == 0

    def test_unassign_user_not_assigned(self, client, sample_ticket, sample_dispatcher):
        """Test unassigning a user that wasn't assigned."""
        response = client.delete(
            f"/api/tickets/{sample_ticket.ticket_id}/unassign-user/{sample_dispatcher.user_id}"
        )
        # Should succeed but not change anything
        assert response.status_code == 200

    def test_unassign_user_ticket_not_found(self, client, sample_dispatcher):
        """Test unassigning user from non-existent ticket."""
        fake_id = uuid4()
        response = client.delete(f"/api/tickets/{fake_id}/unassign-user/{sample_dispatcher.user_id}")
        assert response.status_code == 404

    def test_unassign_user_user_not_found(self, client, sample_ticket):
        """Test unassigning non-existent user."""
        fake_id = uuid4()
        response = client.delete(f"/api/tickets/{sample_ticket.ticket_id}/unassign-user/{fake_id}")
        assert response.status_code == 404


class TestUnassignCrew:
    """Tests for DELETE /api/tickets/{ticket_id}/unassign-crew/{crew_id}"""

    def test_unassign_crew(self, client, sample_ticket_with_relations, sample_crew):
        """Test unassigning a crew from a ticket."""
        response = client.delete(
            f"/api/tickets/{sample_ticket_with_relations.ticket_id}/unassign-crew/{sample_crew.team_id}"
        )
        assert response.status_code == 200

        # Verify unassignment
        get_response = client.get(f"/api/tickets/{sample_ticket_with_relations.ticket_id}")
        data = get_response.json()
        assert len(data["crew_assignees"]) == 0

    def test_unassign_crew_not_assigned(self, client, sample_ticket, sample_crew):
        """Test unassigning a crew that wasn't assigned."""
        response = client.delete(
            f"/api/tickets/{sample_ticket.ticket_id}/unassign-crew/{sample_crew.team_id}"
        )
        # Should succeed but not change anything
        assert response.status_code == 200

    def test_unassign_crew_ticket_not_found(self, client, sample_crew):
        """Test unassigning crew from non-existent ticket."""
        fake_id = uuid4()
        response = client.delete(f"/api/tickets/{fake_id}/unassign-crew/{sample_crew.team_id}")
        assert response.status_code == 404

    def test_unassign_crew_crew_not_found(self, client, sample_ticket):
        """Test unassigning non-existent crew."""
        fake_id = uuid4()
        response = client.delete(f"/api/tickets/{sample_ticket.ticket_id}/unassign-crew/{fake_id}")
        assert response.status_code == 404
