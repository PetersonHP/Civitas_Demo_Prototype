"""
Tests for ticket label operations.
"""
import pytest
from uuid import uuid4


class TestSetTicketLabels:
    """Tests for POST /api/tickets/{ticket_id}/labels"""

    def test_set_labels_on_ticket(self, client, sample_ticket, sample_label):
        """Test setting labels on a ticket."""
        labels_data = {"label_ids": [str(sample_label.label_id)]}
        response = client.post(f"/api/tickets/{sample_ticket.ticket_id}/labels", json=labels_data)
        assert response.status_code == 200

        # Verify label is set
        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        data = get_response.json()
        assert len(data["labels"]) == 1
        assert data["labels"][0]["label_id"] == str(sample_label.label_id)

    def test_set_multiple_labels(self, client, sample_ticket, sample_label, db_session, sample_dispatcher):
        """Test setting multiple labels on a ticket."""
        from src.models.civitas import Label

        # Create additional label
        label2 = Label(
            label_id=uuid4(),
            label_name="Urgent",
            label_description="Urgent issues",
            color_hex="#FFA500",
            created_by=sample_dispatcher.user_id,
        )
        db_session.add(label2)
        db_session.commit()
        db_session.refresh(label2)

        labels_data = {"label_ids": [str(sample_label.label_id), str(label2.label_id)]}
        response = client.post(f"/api/tickets/{sample_ticket.ticket_id}/labels", json=labels_data)
        assert response.status_code == 200

        # Verify both labels are set
        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        data = get_response.json()
        assert len(data["labels"]) == 2

    def test_set_labels_replaces_existing(self, client, sample_ticket_with_relations, db_session, sample_dispatcher):
        """Test that setting labels replaces existing labels."""
        from src.models.civitas import Label

        # Verify initial label
        get_response = client.get(f"/api/tickets/{sample_ticket_with_relations.ticket_id}")
        initial_data = get_response.json()
        assert len(initial_data["labels"]) == 1

        # Create new label
        new_label = Label(
            label_id=uuid4(),
            label_name="Different Label",
            color_hex="#00FF00",
            created_by=sample_dispatcher.user_id,
        )
        db_session.add(new_label)
        db_session.commit()
        db_session.refresh(new_label)

        # Set new label (should replace existing)
        labels_data = {"label_ids": [str(new_label.label_id)]}
        response = client.post(
            f"/api/tickets/{sample_ticket_with_relations.ticket_id}/labels",
            json=labels_data
        )
        assert response.status_code == 200

        # Verify replacement
        get_response = client.get(f"/api/tickets/{sample_ticket_with_relations.ticket_id}")
        data = get_response.json()
        assert len(data["labels"]) == 1
        assert data["labels"][0]["label_id"] == str(new_label.label_id)

    def test_set_labels_empty_list(self, client, sample_ticket_with_relations):
        """Test setting empty label list removes all labels."""
        labels_data = {"label_ids": []}
        response = client.post(
            f"/api/tickets/{sample_ticket_with_relations.ticket_id}/labels",
            json=labels_data
        )
        assert response.status_code == 200

        # Verify all labels removed
        get_response = client.get(f"/api/tickets/{sample_ticket_with_relations.ticket_id}")
        data = get_response.json()
        assert len(data["labels"]) == 0

    def test_set_labels_ticket_not_found(self, client, sample_label):
        """Test setting labels on non-existent ticket."""
        fake_id = uuid4()
        labels_data = {"label_ids": [str(sample_label.label_id)]}
        response = client.post(f"/api/tickets/{fake_id}/labels", json=labels_data)
        assert response.status_code == 404

    def test_set_labels_invalid_label(self, client, sample_ticket):
        """Test setting non-existent label."""
        fake_id = uuid4()
        labels_data = {"label_ids": [str(fake_id)]}
        response = client.post(f"/api/tickets/{sample_ticket.ticket_id}/labels", json=labels_data)
        assert response.status_code == 400
        assert "label" in response.json()["detail"].lower()

    def test_set_labels_partial_invalid(self, client, sample_ticket, sample_label):
        """Test setting labels when some are invalid."""
        fake_id = uuid4()
        labels_data = {"label_ids": [str(sample_label.label_id), str(fake_id)]}
        response = client.post(f"/api/tickets/{sample_ticket.ticket_id}/labels", json=labels_data)
        assert response.status_code == 400

        # Verify no labels were set
        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        data = get_response.json()
        assert len(data["labels"]) == 0


class TestRemoveLabelFromTicket:
    """Tests for DELETE /api/tickets/{ticket_id}/labels/{label_id}"""

    def test_remove_label(self, client, sample_ticket_with_relations, sample_label):
        """Test removing a label from a ticket."""
        # Verify label exists
        get_response = client.get(f"/api/tickets/{sample_ticket_with_relations.ticket_id}")
        initial_data = get_response.json()
        assert len(initial_data["labels"]) == 1

        # Remove label
        response = client.delete(
            f"/api/tickets/{sample_ticket_with_relations.ticket_id}/labels/{sample_label.label_id}"
        )
        assert response.status_code == 200

        # Verify label is removed
        get_response = client.get(f"/api/tickets/{sample_ticket_with_relations.ticket_id}")
        data = get_response.json()
        assert len(data["labels"]) == 0

    def test_remove_label_not_attached(self, client, sample_ticket, sample_label):
        """Test removing a label that wasn't attached to the ticket."""
        response = client.delete(
            f"/api/tickets/{sample_ticket.ticket_id}/labels/{sample_label.label_id}"
        )
        # Should succeed but not change anything
        assert response.status_code == 200

        # Verify no labels
        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        data = get_response.json()
        assert len(data["labels"]) == 0

    def test_remove_one_of_many_labels(self, client, sample_ticket, sample_label, db_session, sample_dispatcher):
        """Test removing one label when multiple exist."""
        from src.models.civitas import Label

        # Create additional label
        label2 = Label(
            label_id=uuid4(),
            label_name="Another Label",
            color_hex="#0000FF",
            created_by=sample_dispatcher.user_id,
        )
        db_session.add(label2)
        db_session.commit()
        db_session.refresh(label2)

        # Set both labels
        labels_data = {"label_ids": [str(sample_label.label_id), str(label2.label_id)]}
        client.post(f"/api/tickets/{sample_ticket.ticket_id}/labels", json=labels_data)

        # Remove first label
        response = client.delete(
            f"/api/tickets/{sample_ticket.ticket_id}/labels/{sample_label.label_id}"
        )
        assert response.status_code == 200

        # Verify only second label remains
        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        data = get_response.json()
        assert len(data["labels"]) == 1
        assert data["labels"][0]["label_id"] == str(label2.label_id)

    def test_remove_label_ticket_not_found(self, client, sample_label):
        """Test removing label from non-existent ticket."""
        fake_id = uuid4()
        response = client.delete(f"/api/tickets/{fake_id}/labels/{sample_label.label_id}")
        assert response.status_code == 404

    def test_remove_label_label_not_found(self, client, sample_ticket):
        """Test removing non-existent label."""
        fake_id = uuid4()
        response = client.delete(f"/api/tickets/{sample_ticket.ticket_id}/labels/{fake_id}")
        assert response.status_code == 404


class TestLabelIntegration:
    """Integration tests for ticket label functionality."""

    def test_full_label_lifecycle(self, client, sample_ticket, sample_label, db_session, sample_dispatcher):
        """Test complete label lifecycle: add, update, remove."""
        from src.models.civitas import Label

        # 1. Start with no labels
        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        assert len(get_response.json()["labels"]) == 0

        # 2. Add first label
        labels_data = {"label_ids": [str(sample_label.label_id)]}
        client.post(f"/api/tickets/{sample_ticket.ticket_id}/labels", json=labels_data)

        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        assert len(get_response.json()["labels"]) == 1

        # 3. Add second label
        label2 = Label(
            label_id=uuid4(),
            label_name="Second Label",
            color_hex="#FFFF00",
            created_by=sample_dispatcher.user_id,
        )
        db_session.add(label2)
        db_session.commit()

        labels_data = {"label_ids": [str(sample_label.label_id), str(label2.label_id)]}
        client.post(f"/api/tickets/{sample_ticket.ticket_id}/labels", json=labels_data)

        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        assert len(get_response.json()["labels"]) == 2

        # 4. Remove one label
        client.delete(f"/api/tickets/{sample_ticket.ticket_id}/labels/{sample_label.label_id}")

        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        assert len(get_response.json()["labels"]) == 1

        # 5. Remove all labels
        labels_data = {"label_ids": []}
        client.post(f"/api/tickets/{sample_ticket.ticket_id}/labels", json=labels_data)

        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        assert len(get_response.json()["labels"]) == 0

    def test_labels_persist_across_updates(self, client, sample_ticket, sample_label):
        """Test that labels persist when ticket is updated."""
        # Set label
        labels_data = {"label_ids": [str(sample_label.label_id)]}
        client.post(f"/api/tickets/{sample_ticket.ticket_id}/labels", json=labels_data)

        # Update ticket
        update_data = {"ticket_subject": "Updated Subject"}
        client.patch(f"/api/tickets/{sample_ticket.ticket_id}", json=update_data)

        # Verify label still exists
        get_response = client.get(f"/api/tickets/{sample_ticket.ticket_id}")
        data = get_response.json()
        assert len(data["labels"]) == 1
        assert data["ticket_subject"] == "Updated Subject"
