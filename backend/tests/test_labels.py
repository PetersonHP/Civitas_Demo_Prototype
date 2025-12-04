"""
Tests for label operations.
"""
import pytest
from uuid import uuid4


class TestGetLabels:
    """Tests for GET /api/labels/"""

    def test_get_labels_empty(self, client):
        """Test getting labels when database is empty."""
        response = client.get("/api/labels/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_labels(self, client, sample_label):
        """Test getting all labels."""
        response = client.get("/api/labels/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["label_id"] == str(sample_label.label_id)
        assert data[0]["label_name"] == sample_label.label_name
        assert data[0]["color_hex"] == sample_label.color_hex

    def test_get_labels_pagination(self, client, db_session, sample_dispatcher):
        """Test label pagination."""
        from src.models.civitas import Label

        # Create multiple labels
        labels = []
        for i in range(5):
            label = Label(
                label_id=uuid4(),
                label_name=f"Label {i}",
                label_description=f"Description {i}",
                color_hex=f"#00000{i}",
                created_by=sample_dispatcher.user_id,
            )
            labels.append(label)
            db_session.add(label)
        db_session.commit()

        # Get first page
        response = client.get("/api/labels/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Get second page
        response = client.get("/api/labels/?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Get third page
        response = client.get("/api/labels/?skip=4&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_labels_search_by_name(self, client, db_session, sample_dispatcher):
        """Test searching labels by name."""
        from src.models.civitas import Label

        # Create labels with different names
        label1 = Label(
            label_id=uuid4(),
            label_name="Urgent",
            label_description="Urgent issues",
            color_hex="#FF0000",
            created_by=sample_dispatcher.user_id,
        )
        label2 = Label(
            label_id=uuid4(),
            label_name="Low Priority",
            label_description="Can wait",
            color_hex="#00FF00",
            created_by=sample_dispatcher.user_id,
        )
        label3 = Label(
            label_id=uuid4(),
            label_name="Critical",
            label_description="Critical issues",
            color_hex="#FF00FF",
            created_by=sample_dispatcher.user_id,
        )
        db_session.add_all([label1, label2, label3])
        db_session.commit()

        # Search by name
        response = client.get("/api/labels/?search=Urgent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["label_name"] == "Urgent"

        # Search case insensitive
        response = client.get("/api/labels/?search=critical")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["label_name"] == "Critical"

    def test_get_labels_search_by_description(self, client, db_session, sample_dispatcher):
        """Test searching labels by description."""
        from src.models.civitas import Label

        label = Label(
            label_id=uuid4(),
            label_name="Safety",
            label_description="Safety related concerns",
            color_hex="#FFA500",
            created_by=sample_dispatcher.user_id,
        )
        db_session.add(label)
        db_session.commit()

        # Search by description
        response = client.get("/api/labels/?search=safety")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["label_description"] == "Safety related concerns"

    def test_get_labels_search_partial_match(self, client, db_session, sample_dispatcher):
        """Test searching with partial matches."""
        from src.models.civitas import Label

        label1 = Label(
            label_id=uuid4(),
            label_name="Infrastructure",
            label_description="Infrastructure issues",
            color_hex="#0000FF",
            created_by=sample_dispatcher.user_id,
        )
        label2 = Label(
            label_id=uuid4(),
            label_name="Street Infrastructure",
            label_description="Street related",
            color_hex="#00FFFF",
            created_by=sample_dispatcher.user_id,
        )
        db_session.add_all([label1, label2])
        db_session.commit()

        # Search by partial match
        response = client.get("/api/labels/?search=Infra")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_labels_search_no_results(self, client, sample_label):
        """Test search with no matching results."""
        response = client.get("/api/labels/?search=NonexistentLabel")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_labels_multiple(self, client, db_session, sample_dispatcher):
        """Test getting multiple labels."""
        from src.models.civitas import Label

        label1 = Label(
            label_id=uuid4(),
            label_name="Label A",
            color_hex="#111111",
            created_by=sample_dispatcher.user_id,
        )
        label2 = Label(
            label_id=uuid4(),
            label_name="Label B",
            color_hex="#222222",
            created_by=sample_dispatcher.user_id,
        )
        label3 = Label(
            label_id=uuid4(),
            label_name="Label C",
            color_hex="#333333",
            created_by=sample_dispatcher.user_id,
        )
        db_session.add_all([label1, label2, label3])
        db_session.commit()

        response = client.get("/api/labels/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_labels_with_creator(self, client, sample_label, sample_dispatcher):
        """Test getting labels with creator information."""
        response = client.get("/api/labels/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["created_by"] == str(sample_dispatcher.user_id)


class TestGetLabelById:
    """Tests for GET /api/labels/{label_id}"""

    def test_get_label_by_id(self, client, sample_label):
        """Test getting a specific label by ID."""
        response = client.get(f"/api/labels/{sample_label.label_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["label_id"] == str(sample_label.label_id)
        assert data["label_name"] == sample_label.label_name
        assert data["color_hex"] == sample_label.color_hex

    def test_get_label_with_description(self, client, sample_label):
        """Test getting a label with description."""
        response = client.get(f"/api/labels/{sample_label.label_id}")
        assert response.status_code == 200
        data = response.json()
        assert "label_description" in data
        assert data["label_description"] == sample_label.label_description

    def test_get_label_with_creator(self, client, sample_label, sample_dispatcher):
        """Test getting a label with creator information."""
        response = client.get(f"/api/labels/{sample_label.label_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["created_by"] == str(sample_dispatcher.user_id)

    def test_get_label_not_found(self, client):
        """Test getting a non-existent label."""
        fake_id = uuid4()
        response = client.get(f"/api/labels/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_label_complete(self, client, db_session, sample_dispatcher):
        """Test getting a label with all fields populated."""
        from src.models.civitas import Label

        label = Label(
            label_id=uuid4(),
            label_name="Complete Label",
            label_description="A label with all fields",
            color_hex="#ABCDEF",
            created_by=sample_dispatcher.user_id,
        )
        db_session.add(label)
        db_session.commit()
        db_session.refresh(label)

        response = client.get(f"/api/labels/{label.label_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["label_name"] == "Complete Label"
        assert data["label_description"] == "A label with all fields"
        assert data["color_hex"] == "#ABCDEF"
        assert data["created_by"] == str(sample_dispatcher.user_id)
        assert "time_created" in data

    def test_get_label_no_description(self, client, db_session, sample_dispatcher):
        """Test getting a label without description."""
        from src.models.civitas import Label

        label = Label(
            label_id=uuid4(),
            label_name="No Description",
            color_hex="#123456",
            created_by=sample_dispatcher.user_id,
        )
        db_session.add(label)
        db_session.commit()
        db_session.refresh(label)

        response = client.get(f"/api/labels/{label.label_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["label_name"] == "No Description"
        assert data["label_description"] is None


class TestLabelColorFormats:
    """Tests for various label color formats."""

    def test_label_hex_color_format(self, client, db_session, sample_dispatcher):
        """Test labels with various hex color formats."""
        from src.models.civitas import Label

        # Standard 6-digit hex
        label = Label(
            label_id=uuid4(),
            label_name="Red Label",
            color_hex="#FF0000",
            created_by=sample_dispatcher.user_id,
        )
        db_session.add(label)
        db_session.commit()
        db_session.refresh(label)

        response = client.get(f"/api/labels/{label.label_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["color_hex"] == "#FF0000"

    def test_multiple_color_labels(self, client, db_session, sample_dispatcher):
        """Test getting multiple labels with different colors."""
        from src.models.civitas import Label

        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"]
        for i, color in enumerate(colors):
            label = Label(
                label_id=uuid4(),
                label_name=f"Color {i}",
                color_hex=color,
                created_by=sample_dispatcher.user_id,
            )
            db_session.add(label)
        db_session.commit()

        response = client.get("/api/labels/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        retrieved_colors = [label["color_hex"] for label in data]
        for color in colors:
            assert color in retrieved_colors
