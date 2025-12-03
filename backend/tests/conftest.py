"""
Pytest configuration and fixtures for testing the Civitas API.
"""
import pytest
import os
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
from dotenv import load_dotenv

# Load .env.test from tests directory if it exists
env_test_path = Path(__file__).parent / ".env.test"
if env_test_path.exists():
    load_dotenv(env_test_path)

# Set environment variable to skip spatial metadata initialization
os.environ["GEOALCHEMY2_FORCE_GENERIC"] = "true"

from src.main import app
from src.database import Base, get_db
from src.models.civitas import (
    CivitasUser,
    CivitasRole,
    Ticket,
    Label,
    SupportCrew,
    TicketComment,
    UserStatus,
    TicketOrigin,
    TicketStatus,
    TicketPriority,
    SupportCrewType,
    SupportCrewStatus,
)


# Use PostgreSQL for testing (same as production)
# This requires a test database to be available
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/civitas_test"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()
    # Clean up all tables after test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with the test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_role(db_session):
    """Create a sample role."""
    role = CivitasRole(
        role_id=uuid4(),
        role_name="Citizen"
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture
def sample_user(db_session, sample_role):
    """Create a sample user."""
    user = CivitasUser(
        user_id=uuid4(),
        firstname="John",
        lastname="Doe",
        email="john.doe@example.com",
        phone_number="+1234567890",
        status=UserStatus.ACTIVE,
    )
    user.roles.append(sample_role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_dispatcher(db_session):
    """Create a sample dispatcher user."""
    dispatcher = CivitasUser(
        user_id=uuid4(),
        firstname="Jane",
        lastname="Dispatcher",
        email="jane.dispatcher@example.com",
        phone_number="+1987654321",
        status=UserStatus.ACTIVE,
    )
    db_session.add(dispatcher)
    db_session.commit()
    db_session.refresh(dispatcher)
    return dispatcher


@pytest.fixture
def sample_crew(db_session, sample_dispatcher):
    """Create a sample support crew."""
    crew = SupportCrew(
        team_id=uuid4(),
        team_name="Pothole Repair Team Alpha",
        description="Main pothole repair crew",
        crew_type=SupportCrewType.POTHOLE_CREW,
        status=SupportCrewStatus.ACTIVE,
    )
    crew.leads.append(sample_dispatcher)
    db_session.add(crew)
    db_session.commit()
    db_session.refresh(crew)
    return crew


@pytest.fixture
def sample_label(db_session, sample_dispatcher):
    """Create a sample label."""
    label = Label(
        label_id=uuid4(),
        label_name="High Priority",
        label_description="Issues requiring immediate attention",
        color_hex="#FF0000",
        created_by=sample_dispatcher.user_id,
    )
    db_session.add(label)
    db_session.commit()
    db_session.refresh(label)
    return label


@pytest.fixture
def sample_ticket(db_session, sample_user):
    """Create a sample ticket."""
    ticket = Ticket(
        ticket_id=uuid4(),
        ticket_subject="Pothole on Main Street",
        ticket_body="There is a large pothole on Main Street near the intersection with 1st Ave.",
        origin=TicketOrigin.WEB_FORM,
        status=TicketStatus.AWAITING_RESPONSE,
        priority=TicketPriority.MEDIUM,
        reporter_id=sample_user.user_id,
        meta_data={"source": "web"},
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)
    return ticket


@pytest.fixture
def sample_ticket_with_relations(db_session, sample_user, sample_dispatcher, sample_crew, sample_label):
    """Create a sample ticket with all relations."""
    ticket = Ticket(
        ticket_id=uuid4(),
        ticket_subject="Broken Street Light",
        ticket_body="Street light is out on Oak Avenue.",
        origin=TicketOrigin.PHONE,
        status=TicketStatus.RESPONSE_IN_PROGRESS,
        priority=TicketPriority.HIGH,
        reporter_id=sample_user.user_id,
        meta_data={"source": "phone"},
    )
    ticket.user_assignees.append(sample_dispatcher)
    ticket.crew_assignees.append(sample_crew)
    ticket.labels.append(sample_label)
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)
    return ticket


@pytest.fixture
def multiple_tickets(db_session, sample_user):
    """Create multiple tickets for testing pagination and filtering."""
    tickets = []

    # Create tickets with different statuses and priorities
    configs = [
        ("Ticket 1", TicketStatus.AWAITING_RESPONSE, TicketPriority.HIGH),
        ("Ticket 2", TicketStatus.AWAITING_RESPONSE, TicketPriority.MEDIUM),
        ("Ticket 3", TicketStatus.RESPONSE_IN_PROGRESS, TicketPriority.LOW),
        ("Ticket 4", TicketStatus.RESOLVED, TicketPriority.HIGH),
        ("Ticket 5", TicketStatus.RESOLVED, TicketPriority.MEDIUM),
    ]

    for subject, status, priority in configs:
        ticket = Ticket(
            ticket_id=uuid4(),
            ticket_subject=subject,
            ticket_body=f"Body for {subject}",
            origin=TicketOrigin.WEB_FORM,
            status=status,
            priority=priority,
            reporter_id=sample_user.user_id,
        )
        db_session.add(ticket)
        tickets.append(ticket)

    db_session.commit()
    for ticket in tickets:
        db_session.refresh(ticket)

    return tickets
