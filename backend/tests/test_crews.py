"""
Tests for crew operations.
"""
import pytest
from uuid import uuid4


class TestGetCrews:
    """Tests for GET /api/crews/"""

    def test_get_crews_empty(self, client):
        """Test getting crews when database is empty."""
        response = client.get("/api/crews/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_crews(self, client, sample_crew):
        """Test getting all crews."""
        response = client.get("/api/crews/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["team_id"] == str(sample_crew.team_id)
        assert data[0]["team_name"] == sample_crew.team_name

    def test_get_crews_pagination(self, client, db_session, sample_dispatcher):
        """Test crew pagination."""
        from src.models.civitas import SupportCrew, SupportCrewType, SupportCrewStatus

        # Create multiple crews
        crews = []
        for i in range(5):
            crew = SupportCrew(
                team_id=uuid4(),
                team_name=f"Crew {i}",
                crew_type=SupportCrewType.POTHOLE_CREW,
                status=SupportCrewStatus.ACTIVE,
            )
            crews.append(crew)
            db_session.add(crew)
        db_session.commit()

        # Get first page
        response = client.get("/api/crews/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Get second page
        response = client.get("/api/crews/?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Get third page
        response = client.get("/api/crews/?skip=4&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_crews_filter_by_status(self, client, db_session):
        """Test filtering crews by status."""
        from src.models.civitas import SupportCrew, SupportCrewType, SupportCrewStatus

        # Create active crew
        active_crew = SupportCrew(
            team_id=uuid4(),
            team_name="Active Crew",
            crew_type=SupportCrewType.POTHOLE_CREW,
            status=SupportCrewStatus.ACTIVE,
        )
        # Create inactive crew
        inactive_crew = SupportCrew(
            team_id=uuid4(),
            team_name="Inactive Crew",
            crew_type=SupportCrewType.DRAIN_CREW,
            status=SupportCrewStatus.INACTIVE,
        )
        db_session.add(active_crew)
        db_session.add(inactive_crew)
        db_session.commit()

        # Filter by active status
        response = client.get("/api/crews/?status=active")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "active"

        # Filter by inactive status
        response = client.get("/api/crews/?status=inactive")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "inactive"

    def test_get_crews_filter_by_crew_type(self, client, db_session):
        """Test filtering crews by crew type."""
        from src.models.civitas import SupportCrew, SupportCrewType, SupportCrewStatus

        # Create pothole crew
        pothole_crew = SupportCrew(
            team_id=uuid4(),
            team_name="Pothole Crew",
            crew_type=SupportCrewType.POTHOLE_CREW,
            status=SupportCrewStatus.ACTIVE,
        )
        # Create drain crew
        drain_crew = SupportCrew(
            team_id=uuid4(),
            team_name="Drain Crew",
            crew_type=SupportCrewType.DRAIN_CREW,
            status=SupportCrewStatus.ACTIVE,
        )
        db_session.add(pothole_crew)
        db_session.add(drain_crew)
        db_session.commit()

        # Filter by pothole crew type
        response = client.get("/api/crews/?crew_type=pothole+crew")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["crew_type"] == "pothole crew"

        # Filter by drain crew type
        response = client.get("/api/crews/?crew_type=drain+crew")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["crew_type"] == "drain crew"

    def test_get_crews_search(self, client, db_session):
        """Test searching crews by name and description."""
        from src.models.civitas import SupportCrew, SupportCrewType, SupportCrewStatus

        # Create crews with different names and descriptions
        crew1 = SupportCrew(
            team_id=uuid4(),
            team_name="Alpha Team",
            description="Handles pothole repairs",
            crew_type=SupportCrewType.POTHOLE_CREW,
            status=SupportCrewStatus.ACTIVE,
        )
        crew2 = SupportCrew(
            team_id=uuid4(),
            team_name="Beta Squad",
            description="Drain maintenance crew",
            crew_type=SupportCrewType.DRAIN_CREW,
            status=SupportCrewStatus.ACTIVE,
        )
        crew3 = SupportCrew(
            team_id=uuid4(),
            team_name="Gamma Force",
            description="Emergency response team",
            crew_type=SupportCrewType.POTHOLE_CREW,
            status=SupportCrewStatus.ACTIVE,
        )
        db_session.add_all([crew1, crew2, crew3])
        db_session.commit()

        # Search by team name
        response = client.get("/api/crews/?search=Alpha")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["team_name"] == "Alpha Team"

        # Search by description
        response = client.get("/api/crews/?search=drain")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["team_name"] == "Beta Squad"

        # Search case insensitive
        response = client.get("/api/crews/?search=gamma")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["team_name"] == "Gamma Force"

    def test_get_crews_combined_filters(self, client, db_session):
        """Test using multiple filters together."""
        from src.models.civitas import SupportCrew, SupportCrewType, SupportCrewStatus

        # Create various crews
        crew1 = SupportCrew(
            team_id=uuid4(),
            team_name="Active Pothole Team",
            crew_type=SupportCrewType.POTHOLE_CREW,
            status=SupportCrewStatus.ACTIVE,
        )
        crew2 = SupportCrew(
            team_id=uuid4(),
            team_name="Inactive Pothole Team",
            crew_type=SupportCrewType.POTHOLE_CREW,
            status=SupportCrewStatus.INACTIVE,
        )
        crew3 = SupportCrew(
            team_id=uuid4(),
            team_name="Active Drain Team",
            crew_type=SupportCrewType.DRAIN_CREW,
            status=SupportCrewStatus.ACTIVE,
        )
        db_session.add_all([crew1, crew2, crew3])
        db_session.commit()

        # Filter by status and crew_type
        response = client.get("/api/crews/?status=active&crew_type=pothole+crew")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["team_name"] == "Active Pothole Team"

        # Filter by search and status
        response = client.get("/api/crews/?search=Pothole&status=inactive")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["team_name"] == "Inactive Pothole Team"

    def test_get_crews_with_location(self, client, db_session):
        """Test getting crews with location coordinates."""
        from src.models.civitas import SupportCrew, SupportCrewType, SupportCrewStatus
        from geoalchemy2.elements import WKTElement

        crew = SupportCrew(
            team_id=uuid4(),
            team_name="Mobile Crew",
            crew_type=SupportCrewType.POTHOLE_CREW,
            status=SupportCrewStatus.ACTIVE,
            location_coordinates=WKTElement("POINT(-74.0060 40.7128)", srid=4326),
        )
        db_session.add(crew)
        db_session.commit()

        response = client.get("/api/crews/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["location_coordinates"] is not None
        assert data[0]["location_coordinates"]["lat"] == pytest.approx(40.7128, rel=1e-4)
        assert data[0]["location_coordinates"]["lng"] == pytest.approx(-74.0060, rel=1e-4)


class TestGetCrewById:
    """Tests for GET /api/crews/{team_id}"""

    def test_get_crew_by_id(self, client, sample_crew):
        """Test getting a specific crew by ID."""
        response = client.get(f"/api/crews/{sample_crew.team_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["team_id"] == str(sample_crew.team_id)
        assert data["team_name"] == sample_crew.team_name
        assert data["crew_type"] == sample_crew.crew_type.value
        assert data["status"] == sample_crew.status.value

    def test_get_crew_with_members(self, client, sample_crew, db_session, sample_user):
        """Test getting a crew with members populated."""
        # Add member to crew
        sample_crew.members.append(sample_user)
        db_session.commit()

        response = client.get(f"/api/crews/{sample_crew.team_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["members"]) == 1
        assert data["members"][0]["user_id"] == str(sample_user.user_id)

    def test_get_crew_with_leads(self, client, sample_crew):
        """Test getting a crew with leads populated."""
        response = client.get(f"/api/crews/{sample_crew.team_id}")
        assert response.status_code == 200
        data = response.json()
        # sample_crew fixture has one lead (sample_dispatcher)
        assert len(data["leads"]) == 1

    def test_get_crew_with_location(self, client, db_session):
        """Test getting a crew with location coordinates."""
        from src.models.civitas import SupportCrew, SupportCrewType, SupportCrewStatus
        from geoalchemy2.elements import WKTElement

        crew = SupportCrew(
            team_id=uuid4(),
            team_name="Located Crew",
            crew_type=SupportCrewType.POTHOLE_CREW,
            status=SupportCrewStatus.ACTIVE,
            location_coordinates=WKTElement("POINT(-118.2437 34.0522)", srid=4326),
        )
        db_session.add(crew)
        db_session.commit()
        db_session.refresh(crew)

        response = client.get(f"/api/crews/{crew.team_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["location_coordinates"] is not None
        assert data["location_coordinates"]["lat"] == pytest.approx(34.0522, rel=1e-4)
        assert data["location_coordinates"]["lng"] == pytest.approx(-118.2437, rel=1e-4)

    def test_get_crew_not_found(self, client):
        """Test getting a non-existent crew."""
        fake_id = uuid4()
        response = client.get(f"/api/crews/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_crew_full_details(self, client, db_session, sample_dispatcher, sample_user):
        """Test getting a crew with all related data."""
        from src.models.civitas import SupportCrew, SupportCrewType, SupportCrewStatus
        from geoalchemy2.elements import WKTElement

        crew = SupportCrew(
            team_id=uuid4(),
            team_name="Complete Crew",
            description="Fully staffed crew",
            crew_type=SupportCrewType.POTHOLE_CREW,
            status=SupportCrewStatus.ACTIVE,
            location_coordinates=WKTElement("POINT(-74.0060 40.7128)", srid=4326),
        )
        crew.leads.append(sample_dispatcher)
        crew.members.extend([sample_dispatcher, sample_user])
        db_session.add(crew)
        db_session.commit()
        db_session.refresh(crew)

        response = client.get(f"/api/crews/{crew.team_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["team_name"] == "Complete Crew"
        assert data["description"] == "Fully staffed crew"
        assert len(data["leads"]) == 1
        assert len(data["members"]) == 2
        assert data["location_coordinates"] is not None
