"""
Tests for ticket comment operations.
"""
import pytest
from uuid import uuid4


class TestGetTicketComments:
    """Tests for GET /api/tickets/{ticket_id}/comments"""

    def test_get_comments_empty(self, client, sample_ticket):
        """Test getting comments when there are none."""
        response = client.get(f"/api/tickets/{sample_ticket.ticket_id}/comments")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_comments(self, client, sample_ticket, sample_user, db_session):
        """Test getting comments for a ticket."""
        from src.models.civitas import TicketComment

        # Create some comments
        comment1 = TicketComment(
            comment_id=uuid4(),
            comment_body="First comment",
            commenter=sample_user.user_id,
            ticket_id=sample_ticket.ticket_id,
        )
        comment2 = TicketComment(
            comment_id=uuid4(),
            comment_body="Second comment",
            commenter=sample_user.user_id,
            ticket_id=sample_ticket.ticket_id,
        )
        db_session.add(comment1)
        db_session.add(comment2)
        db_session.commit()

        response = client.get(f"/api/tickets/{sample_ticket.ticket_id}/comments")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["comment_body"] == "First comment"
        assert data[1]["comment_body"] == "Second comment"

    def test_get_comments_with_user_details(self, client, sample_ticket, sample_user, db_session):
        """Test that comments include commenter user details."""
        from src.models.civitas import TicketComment

        comment = TicketComment(
            comment_id=uuid4(),
            comment_body="Test comment",
            commenter=sample_user.user_id,
            ticket_id=sample_ticket.ticket_id,
        )
        db_session.add(comment)
        db_session.commit()

        response = client.get(f"/api/tickets/{sample_ticket.ticket_id}/comments")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["commenter_user"]["user_id"] == str(sample_user.user_id)
        assert data[0]["commenter_user"]["firstname"] == sample_user.firstname
        assert data[0]["commenter_user"]["lastname"] == sample_user.lastname

    def test_get_comments_ticket_not_found(self, client):
        """Test getting comments for non-existent ticket."""
        fake_id = uuid4()
        response = client.get(f"/api/tickets/{fake_id}/comments")
        assert response.status_code == 404


class TestCreateTicketComment:
    """Tests for POST /api/tickets/{ticket_id}/comments"""

    def test_create_comment(self, client, sample_ticket, sample_user):
        """Test creating a comment on a ticket."""
        comment_data = {
            "comment_body": "This is a test comment",
            "commenter": str(sample_user.user_id),
            "ticket_id": str(sample_ticket.ticket_id),
        }
        response = client.post(f"/api/tickets/{sample_ticket.ticket_id}/comments", json=comment_data)
        assert response.status_code == 201
        data = response.json()
        assert data["comment_body"] == comment_data["comment_body"]
        assert data["commenter"] == comment_data["commenter"]
        assert data["ticket_id"] == str(sample_ticket.ticket_id)
        assert data["is_edited"] is False
        assert "comment_id" in data
        assert "time_created" in data

    def test_create_comment_with_user_details(self, client, sample_ticket, sample_user):
        """Test that created comment includes commenter details."""
        comment_data = {
            "comment_body": "Test comment",
            "commenter": str(sample_user.user_id),
            "ticket_id": str(sample_ticket.ticket_id),
        }
        response = client.post(f"/api/tickets/{sample_ticket.ticket_id}/comments", json=comment_data)
        assert response.status_code == 201
        data = response.json()
        assert data["commenter_user"]["user_id"] == str(sample_user.user_id)

    def test_create_comment_ticket_not_found(self, client, sample_user):
        """Test creating comment on non-existent ticket."""
        fake_id = uuid4()
        comment_data = {
            "comment_body": "Test",
            "commenter": str(sample_user.user_id),
            "ticket_id": str(fake_id),
        }
        response = client.post(f"/api/tickets/{fake_id}/comments", json=comment_data)
        assert response.status_code == 404

    def test_create_comment_invalid_commenter(self, client, sample_ticket):
        """Test creating comment with non-existent commenter."""
        fake_id = uuid4()
        comment_data = {
            "comment_body": "Test",
            "commenter": str(fake_id),
            "ticket_id": str(sample_ticket.ticket_id),
        }
        response = client.post(f"/api/tickets/{sample_ticket.ticket_id}/comments", json=comment_data)
        assert response.status_code == 400
        assert "commenter" in response.json()["detail"].lower()

    def test_create_multiple_comments(self, client, sample_ticket, sample_user, sample_dispatcher):
        """Test creating multiple comments from different users."""
        comment1_data = {
            "comment_body": "First comment",
            "commenter": str(sample_user.user_id),
            "ticket_id": str(sample_ticket.ticket_id),
        }
        response1 = client.post(f"/api/tickets/{sample_ticket.ticket_id}/comments", json=comment1_data)
        assert response1.status_code == 201

        comment2_data = {
            "comment_body": "Second comment",
            "commenter": str(sample_dispatcher.user_id),
            "ticket_id": str(sample_ticket.ticket_id),
        }
        response2 = client.post(f"/api/tickets/{sample_ticket.ticket_id}/comments", json=comment2_data)
        assert response2.status_code == 201

        # Verify both comments exist
        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}/comments")
        data = get_response.json()
        assert len(data) == 2


class TestUpdateTicketComment:
    """Tests for PATCH /api/tickets/comments/{comment_id}"""

    def test_update_comment(self, client, sample_ticket, sample_user, db_session):
        """Test updating a comment."""
        from src.models.civitas import TicketComment

        comment = TicketComment(
            comment_id=uuid4(),
            comment_body="Original comment",
            commenter=sample_user.user_id,
            ticket_id=sample_ticket.ticket_id,
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)

        update_data = {"comment_body": "Updated comment"}
        response = client.patch(f"/api/tickets/comments/{comment.comment_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["comment_body"] == "Updated comment"
        assert data["is_edited"] is True
        assert data["time_edited"] is not None

    def test_update_comment_preserves_other_fields(self, client, sample_ticket, sample_user, db_session):
        """Test that updating a comment preserves other fields."""
        from src.models.civitas import TicketComment

        comment = TicketComment(
            comment_id=uuid4(),
            comment_body="Original comment",
            commenter=sample_user.user_id,
            ticket_id=sample_ticket.ticket_id,
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)

        original_time_created = comment.time_created
        original_commenter = comment.commenter

        update_data = {"comment_body": "Updated comment"}
        response = client.patch(f"/api/tickets/comments/{comment.comment_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["commenter"] == str(original_commenter)
        assert data["ticket_id"] == str(sample_ticket.ticket_id)

    def test_update_comment_not_found(self, client):
        """Test updating non-existent comment."""
        fake_id = uuid4()
        update_data = {"comment_body": "Test"}
        response = client.patch(f"/api/tickets/comments/{fake_id}", json=update_data)
        assert response.status_code == 404


class TestDeleteTicketComment:
    """Tests for DELETE /api/tickets/comments/{comment_id}"""

    def test_delete_comment(self, client, sample_ticket, sample_user, db_session):
        """Test deleting a comment."""
        from src.models.civitas import TicketComment

        comment = TicketComment(
            comment_id=uuid4(),
            comment_body="Comment to delete",
            commenter=sample_user.user_id,
            ticket_id=sample_ticket.ticket_id,
        )
        db_session.add(comment)
        db_session.commit()
        comment_id = comment.comment_id

        response = client.delete(f"/api/tickets/comments/{comment_id}")
        assert response.status_code == 204

        # Verify comment is deleted
        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}/comments")
        data = get_response.json()
        assert len(data) == 0

    def test_delete_comment_not_found(self, client):
        """Test deleting non-existent comment."""
        fake_id = uuid4()
        response = client.delete(f"/api/tickets/comments/{fake_id}")
        assert response.status_code == 404

    def test_delete_one_of_many_comments(self, client, sample_ticket, sample_user, db_session):
        """Test deleting one comment when multiple exist."""
        from src.models.civitas import TicketComment

        comment1 = TicketComment(
            comment_id=uuid4(),
            comment_body="First comment",
            commenter=sample_user.user_id,
            ticket_id=sample_ticket.ticket_id,
        )
        comment2 = TicketComment(
            comment_id=uuid4(),
            comment_body="Second comment",
            commenter=sample_user.user_id,
            ticket_id=sample_ticket.ticket_id,
        )
        db_session.add(comment1)
        db_session.add(comment2)
        db_session.commit()

        # Delete first comment
        response = client.delete(f"/api/tickets/comments/{comment1.comment_id}")
        assert response.status_code == 204

        # Verify only second comment remains
        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}/comments")
        data = get_response.json()
        assert len(data) == 1
        assert data[0]["comment_body"] == "Second comment"
