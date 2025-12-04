"""
Tests for user operations.
"""
import pytest
from uuid import uuid4


class TestGetUsers:
    """Tests for GET /api/users/"""

    def test_get_users_empty(self, client):
        """Test getting users when database is empty."""
        response = client.get("/api/users/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_users(self, client, sample_user):
        """Test getting all users."""
        response = client.get("/api/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == str(sample_user.user_id)
        assert data[0]["firstname"] == sample_user.firstname
        assert data[0]["lastname"] == sample_user.lastname
        assert data[0]["email"] == sample_user.email

    def test_get_users_pagination(self, client, db_session, sample_role):
        """Test user pagination."""
        from src.models.civitas import CivitasUser, UserStatus

        # Create multiple users
        users = []
        for i in range(5):
            user = CivitasUser(
                user_id=uuid4(),
                firstname=f"User{i}",
                lastname=f"Test{i}",
                email=f"user{i}@example.com",
                phone_number=f"+123456789{i}",
                status=UserStatus.ACTIVE,
            )
            users.append(user)
            db_session.add(user)
        db_session.commit()

        # Get first page
        response = client.get("/api/users/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Get second page
        response = client.get("/api/users/?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Get third page
        response = client.get("/api/users/?skip=4&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_users_search_by_firstname(self, client, db_session):
        """Test searching users by first name."""
        from src.models.civitas import CivitasUser, UserStatus

        # Create users with different names
        user1 = CivitasUser(
            user_id=uuid4(),
            firstname="Alice",
            lastname="Smith",
            email="alice@example.com",
            phone_number="+1111111111",
            status=UserStatus.ACTIVE,
        )
        user2 = CivitasUser(
            user_id=uuid4(),
            firstname="Bob",
            lastname="Jones",
            email="bob@example.com",
            phone_number="+2222222222",
            status=UserStatus.ACTIVE,
        )
        db_session.add_all([user1, user2])
        db_session.commit()

        # Search by first name
        response = client.get("/api/users/?search=Alice")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["firstname"] == "Alice"

        # Search case insensitive
        response = client.get("/api/users/?search=bob")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["firstname"] == "Bob"

    def test_get_users_search_by_lastname(self, client, db_session):
        """Test searching users by last name."""
        from src.models.civitas import CivitasUser, UserStatus

        user = CivitasUser(
            user_id=uuid4(),
            firstname="Charlie",
            lastname="Anderson",
            email="charlie@example.com",
            phone_number="+3333333333",
            status=UserStatus.ACTIVE,
        )
        db_session.add(user)
        db_session.commit()

        response = client.get("/api/users/?search=Anderson")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["lastname"] == "Anderson"

    def test_get_users_search_by_email(self, client, db_session):
        """Test searching users by email."""
        from src.models.civitas import CivitasUser, UserStatus

        user = CivitasUser(
            user_id=uuid4(),
            firstname="David",
            lastname="Brown",
            email="david.brown@company.com",
            phone_number="+4444444444",
            status=UserStatus.ACTIVE,
        )
        db_session.add(user)
        db_session.commit()

        # Search by full email
        response = client.get("/api/users/?search=david.brown@company.com")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == "david.brown@company.com"

        # Search by partial email
        response = client.get("/api/users/?search=company.com")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_users_search_by_phone(self, client, db_session):
        """Test searching users by phone number."""
        from src.models.civitas import CivitasUser, UserStatus

        user = CivitasUser(
            user_id=uuid4(),
            firstname="Eve",
            lastname="Wilson",
            email="eve@example.com",
            phone_number="+15551234567",
            status=UserStatus.ACTIVE,
        )
        db_session.add(user)
        db_session.commit()

        # Search by phone number
        response = client.get("/api/users/?search=5551234567")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["phone_number"] == "+15551234567"

    def test_get_users_search_partial_match(self, client, db_session):
        """Test searching with partial matches."""
        from src.models.civitas import CivitasUser, UserStatus

        user1 = CivitasUser(
            user_id=uuid4(),
            firstname="Frank",
            lastname="Franklin",
            email="frank@example.com",
            phone_number="+6666666666",
            status=UserStatus.ACTIVE,
        )
        user2 = CivitasUser(
            user_id=uuid4(),
            firstname="Francis",
            lastname="Johnson",
            email="francis@example.com",
            phone_number="+7777777777",
            status=UserStatus.ACTIVE,
        )
        db_session.add_all([user1, user2])
        db_session.commit()

        # Search by partial match
        response = client.get("/api/users/?search=Fran")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_users_search_no_results(self, client, sample_user):
        """Test search with no matching results."""
        response = client.get("/api/users/?search=NonexistentUser")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_users_multiple(self, client, sample_user, sample_dispatcher):
        """Test getting multiple users."""
        response = client.get("/api/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        user_ids = [user["user_id"] for user in data]
        assert str(sample_user.user_id) in user_ids
        assert str(sample_dispatcher.user_id) in user_ids

    def test_get_users_with_timestamps(self, client, sample_user):
        """Test getting users includes timestamp information."""
        response = client.get("/api/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        # Verify timestamp fields are present
        assert "time_created" in data[0]
        assert "time_updated" in data[0]


class TestGetUserById:
    """Tests for GET /api/users/{user_id}"""

    def test_get_user_by_id(self, client, sample_user):
        """Test getting a specific user by ID."""
        response = client.get(f"/api/users/{sample_user.user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(sample_user.user_id)
        assert data["firstname"] == sample_user.firstname
        assert data["lastname"] == sample_user.lastname
        assert data["email"] == sample_user.email
        assert data["phone_number"] == sample_user.phone_number
        assert data["status"] == sample_user.status.value

    def test_get_user_with_timestamps(self, client, sample_user):
        """Test getting a user with timestamp information."""
        response = client.get(f"/api/users/{sample_user.user_id}")
        assert response.status_code == 200
        data = response.json()
        assert "time_created" in data
        assert "time_updated" in data
        assert "time_last_login" in data

    def test_get_user_not_found(self, client):
        """Test getting a non-existent user."""
        fake_id = uuid4()
        response = client.get(f"/api/users/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_user_complete_profile(self, client, db_session):
        """Test getting a user with complete profile information."""
        from src.models.civitas import CivitasUser, UserStatus

        # Create user with all fields
        user = CivitasUser(
            user_id=uuid4(),
            firstname="George",
            lastname="Taylor",
            email="george@example.com",
            phone_number="+18885551234",
            status=UserStatus.ACTIVE,
            google_id="google123",
            google_email="george@gmail.com",
            google_avatar_url="https://example.com/avatar.jpg",
            meta_data={"department": "IT"}
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        response = client.get(f"/api/users/{user.user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["firstname"] == "George"
        assert data["lastname"] == "Taylor"
        assert data["email"] == "george@example.com"
        assert data["phone_number"] == "+18885551234"
        assert data["status"] == "active"
        assert data["google_id"] == "google123"
        assert data["google_email"] == "george@gmail.com"
        assert data["google_avatar_url"] == "https://example.com/avatar.jpg"
        assert data["meta_data"]["department"] == "IT"

    def test_get_user_inactive_status(self, client, db_session):
        """Test getting a user with inactive status."""
        from src.models.civitas import CivitasUser, UserStatus

        user = CivitasUser(
            user_id=uuid4(),
            firstname="Hannah",
            lastname="Davis",
            email="hannah@example.com",
            phone_number="+19995551234",
            status=UserStatus.INACTIVE,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        response = client.get(f"/api/users/{user.user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "inactive"

    def test_get_user_minimal_fields(self, client, db_session):
        """Test getting a user with minimal optional fields."""
        from src.models.civitas import CivitasUser, UserStatus

        user = CivitasUser(
            user_id=uuid4(),
            firstname="Ivan",
            lastname="Martinez",
            email="ivan@example.com",
            phone_number="+17775551234",
            status=UserStatus.ACTIVE,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        response = client.get(f"/api/users/{user.user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["firstname"] == "Ivan"
        assert data["lastname"] == "Martinez"
        assert data["google_id"] is None
        assert data["google_email"] is None
        assert data["google_avatar_url"] is None
