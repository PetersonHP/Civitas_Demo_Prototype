# Civitas API Tests

Comprehensive test suite for the Civitas ticket management API.

## Setup

### Test Database

The tests require a PostgreSQL database with PostGIS extension. Create a test database:

```bash
# Create test database
createdb civitas_test

# Enable PostGIS extension
psql civitas_test -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### Environment Configuration

Set the test database URL (optional, defaults shown below):

```bash
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/civitas_test"
```

Or create a `.env.test` file in the `backend/tests` directory:

```
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/civitas_test
```

## Running Tests

### Run all tests

```bash
# From project root
python -m pytest backend/tests/ -v

# Or from backend directory
cd backend
pytest tests/ -v
```

### Run specific test file

```bash
pytest backend/tests/test_tickets_crud.py -v
```

### Run specific test class or function

```bash
pytest backend/tests/test_tickets_crud.py::TestCreateTicket -v
pytest backend/tests/test_tickets_crud.py::TestCreateTicket::test_create_ticket_minimal -v
```

### Run with coverage

```bash
pytest backend/tests/ --cov=src --cov-report=html
```

## Test Structure

```
tests/
├── conftest.py                    # Pytest fixtures and configuration
├── test_tickets_crud.py           # Tests for ticket CRUD operations
├── test_tickets_assignments.py    # Tests for user/crew assignments
├── test_tickets_comments.py       # Tests for ticket comments
└── test_tickets_labels.py         # Tests for ticket labels
```

## Test Coverage

### Ticket CRUD Operations (test_tickets_crud.py)
- ✓ GET /api/tickets/ - List tickets with pagination and filtering
- ✓ GET /api/tickets/{id} - Get single ticket with relations
- ✓ POST /api/tickets/ - Create tickets (with/without assignees and labels)
- ✓ PATCH /api/tickets/{id} - Update tickets
- ✓ PATCH /api/tickets/{id}/status - Quick status updates
- ✓ DELETE /api/tickets/{id} - Delete tickets

### Assignment Operations (test_tickets_assignments.py)
- ✓ POST /api/tickets/{id}/assign-users - Assign users to tickets
- ✓ POST /api/tickets/{id}/assign-crews - Assign crews to tickets
- ✓ DELETE /api/tickets/{id}/unassign-user/{user_id} - Unassign users
- ✓ DELETE /api/tickets/{id}/unassign-crew/{crew_id} - Unassign crews

### Comment Operations (test_tickets_comments.py)
- ✓ GET /api/tickets/{id}/comments - List comments
- ✓ POST /api/tickets/{id}/comments - Create comments
- ✓ PATCH /api/tickets/comments/{id} - Update comments
- ✓ DELETE /api/tickets/comments/{id} - Delete comments

### Label Operations (test_tickets_labels.py)
- ✓ POST /api/tickets/{id}/labels - Set/replace labels
- ✓ DELETE /api/tickets/{id}/labels/{label_id} - Remove labels
- ✓ Integration tests for complete label lifecycle

## Fixtures

Available fixtures in `conftest.py`:

- `client` - FastAPI test client
- `db_session` - Database session for each test
- `sample_user` - User with citizen role
- `sample_dispatcher` - Dispatcher user
- `sample_crew` - Support crew with lead
- `sample_label` - Sample label
- `sample_ticket` - Basic ticket
- `sample_ticket_with_relations` - Ticket with all relations
- `multiple_tickets` - 5 tickets with varying status/priority

## Notes

- Each test runs in isolation with a fresh database state
- Tests use transactions that are rolled back after each test
- Spatial/location features require PostGIS extension
- All tests validate error cases (404, 400) and success paths
