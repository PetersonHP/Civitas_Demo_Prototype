# Civitas Demo

An AI-powered 311 ticket management and dispatch system for municipal governments. Civitas demonstrates how modern artificial intelligence can transform civic service delivery by intelligently triaging citizen service requests, automatically assigning work crews based on location and expertise, and streamlining city operations.

## Overview

Municipal governments handle thousands of citizen service requests daily—reports of potholes, broken streetlights, fallen trees, sanitation issues, and more. Traditional 311 systems require dispatchers to manually review each ticket, assess priority, identify the appropriate department and crew, and coordinate responses. This manual process is time-consuming, prone to delays, and can result in suboptimal crew assignments.

**Civitas** leverages Anthropic's Claude AI to automate and enhance this process. The system's intelligent dispatcher analyzes ticket content and location data, queries the database for available resources, and provides comprehensive recommendations including:

- Priority assessment with detailed justification
- Optimal crew assignments based on expertise and proximity
- Individual staff recommendations
- Categorization labels for efficient organization
- Professional responses to citizens

By combining geospatial analysis (PostGIS), real-time crew tracking (Mapbox), and AI-powered decision-making, Civitas represents a modern approach to civic technology that can significantly reduce response times and improve resource allocation.

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework for building APIs
- **PostgreSQL 16** - Relational database with PostGIS extension
- **PostGIS** - Spatial database extension for geospatial queries
- **SQLAlchemy 2.0** - ORM for database operations
- **Alembic** - Database migration management
- **Pydantic** - Data validation and settings management
- **GeoAlchemy2** - Geospatial extension for SQLAlchemy
- **Anthropic Claude SDK** - AI-powered ticket dispatching and analysis

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and development server
- **Chakra UI** - Accessible component library with theming
- **Axios** - HTTP client for API communication
- **Mapbox GL** - Interactive map rendering
- **React Map GL** - React wrapper for Mapbox
- **React Markdown** - Markdown rendering for comments
- **SimpleMDE** - Markdown editor component
- **Framer Motion** - Animation library

## Key Features

### AI-Powered Intelligent Dispatching

The core innovation of Civitas is its AI dispatcher powered by Anthropic's Claude. When a dispatcher clicks the "AI Dispatch" button on a ticket, the system:

1. Analyzes the ticket's subject, description, and location coordinates
2. Uses Claude's tool-calling capabilities to query the database for:
   - Available support crews and their locations
   - Qualified staff members
   - Relevant categorization labels
3. Performs geospatial calculations to identify nearest crews
4. Returns comprehensive recommendations:
   - **Priority Level** (High/Medium/Low) with detailed justification
   - **Crew Assignments** based on crew type and proximity
   - **Staff Assignments** for individual accountability
   - **Labels** for categorization and filtering
   - **Citizen Response** - a professional message to the reporter

This AI-driven approach can reduce manual dispatcher workload by hours per day while improving assignment accuracy.

### Interactive Geospatial Mapping

- **Visual Ticket Tracking**: All tickets displayed on an interactive Mapbox map
- **Crew Location Monitoring**: Real-time crew positions shown with team icons
- **Color-Coded Status**: Tickets marked by status (awaiting response, in progress, resolved)
- **Nearest Crew Search**: PostGIS-powered distance calculations to find optimal crews
- **Click-to-View Details**: Interactive markers for tickets and crews

### Comprehensive Ticket Management

- **Full CRUD Operations**: Create, read, update, and delete tickets
- **Status Workflow**: Track tickets from "awaiting response" → "in progress" → "resolved"
- **Priority Levels**: Low, medium, and high priority classification
- **Origin Tracking**: Differentiate tickets by source (phone, web, SMS)
- **Rich Text Editing**: Markdown support for detailed descriptions
- **Comment Threads**: Collaborative discussion on tickets with user attribution
- **Update Audit Trail**: Automatic logging of all ticket changes

### Assignment System

- **Multi-User Assignment**: Assign multiple staff members to a single ticket
- **Multi-Crew Assignment**: Deploy multiple specialized crews as needed
- **Six Crew Types**:
  - Pothole repair crews
  - Drainage maintenance crews
  - Tree service crews
  - Sign maintenance crews
  - Snow removal crews
  - Sanitation crews
- **Visual Management**: See all assignees with one-click removal capability
- **Search and Filter**: Find users and crews by name, type, or location

### Label and Categorization System

- **Multi-Label Support**: Tag tickets with multiple categories
- **Colored Tags**: Visual distinction between label types
- **Search Capabilities**: Filter tickets by labels
- **Custom Labels**: Create organization-specific categorization schemes

## Project Structure

```
Civitas_Demo_Prototype/
├── backend/
│   ├── src/
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── config.py         # Configuration and environment management
│   │   ├── database.py       # Database connection and session management
│   │   ├── models/           # SQLAlchemy ORM models
│   │   │   └── civitas.py    # Tickets, Users, Crews, Labels, Comments
│   │   ├── schemas/          # Pydantic validation schemas
│   │   │   └── civitas.py    # Request/response data models
│   │   ├── routers/          # API endpoint routers
│   │   │   ├── tickets.py    # Ticket CRUD and operations
│   │   │   ├── crews.py      # Crew management
│   │   │   ├── users.py      # User management
│   │   │   ├── labels.py     # Label management
│   │   │   ├── dispatcher.py # AI dispatcher endpoint
│   │   │   └── items.py      # Example endpoints
│   │   ├── services/         # Business logic layer
│   │   │   └── dispatcher_agent.py  # AI dispatcher implementation
│   │   └── prompts/          # AI system prompts
│   │       └── dispatcher_system.md # Dispatcher role and instructions
│   ├── tests/                # Comprehensive test suite
│   │   ├── conftest.py       # Test fixtures and configuration
│   │   ├── test_tickets_crud.py
│   │   ├── test_tickets_assignments.py
│   │   ├── test_tickets_comments.py
│   │   ├── test_crews.py
│   │   ├── test_users.py
│   │   └── README.md         # Test documentation
│   ├── scripts/              # Utility scripts
│   │   ├── import_tickets_from_csv.py    # Bulk ticket import
│   │   ├── import_crews_from_csv.py      # Crew data import
│   │   ├── transform_nyc_311_to_tickets.py  # NYC 311 data transformation
│   │   ├── test_dispatcher.py            # Dispatcher testing tool
│   │   └── analyze_test_results.py       # Test result analysis
│   ├── data/                 # Sample datasets
│   │   ├── nyc_311_data.csv
│   │   ├── sample_tickets.csv
│   │   └── sample_crews.csv
│   ├── alembic/              # Database migrations
│   ├── logs/                 # Application logs
│   ├── requirements.txt      # Python dependencies
│   ├── alembic.ini          # Migration configuration
│   └── .env.example          # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── TicketDashboard.tsx  # Main dashboard
│   │   │   ├── MapView.tsx          # Interactive map
│   │   │   ├── TicketMarker.tsx     # Ticket map markers
│   │   │   ├── CrewMarker.tsx       # Crew map markers
│   │   │   └── CommentSection.tsx   # Comment threads
│   │   ├── services/         # API service layer
│   │   │   ├── api.ts               # Axios configuration
│   │   │   ├── ticketService.ts     # Ticket API client
│   │   │   ├── crewService.ts       # Crew API client
│   │   │   ├── userService.ts       # User API client
│   │   │   ├── labelService.ts      # Label API client
│   │   │   └── dispatcherService.ts # AI dispatcher client
│   │   ├── hooks/            # Custom React hooks
│   │   ├── utils/            # Utility functions
│   │   ├── App.tsx           # Main App component
│   │   └── main.tsx          # Entry point
│   ├── dist/                 # Production build output
│   ├── package.json          # Node dependencies and scripts
│   ├── vite.config.ts        # Vite configuration
│   ├── tsconfig.json         # TypeScript configuration
│   └── .env.example          # Frontend environment variables
└── docker-compose.yml        # PostgreSQL container setup
```

## Prerequisites

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** and npm - [Download](https://nodejs.org/)
- **PostgreSQL 16** with **PostGIS extension** (required for geospatial features)
- **Docker** (optional, for PostgreSQL container) - [Download](https://www.docker.com/products/docker-desktop/)
- **Anthropic API Key** (required for AI dispatcher) - [Get one here](https://console.anthropic.com/)
- **Mapbox Access Token** (optional, for production maps)

## Setup Instructions

### 1. Database Setup

**Option A: Using Docker (Recommended)**

The project includes a `docker-compose.yml` file that automatically sets up PostgreSQL 16 with PostGIS:

```bash
docker-compose up -d
```

This creates a database with:
- Database: `civitas_db`
- User: `civitas_user`
- Password: `civitas_password`
- Port: `5432`
- PostGIS extension pre-installed

**Option B: Install PostgreSQL locally**

Install PostgreSQL 16 and create a database:

```sql
CREATE DATABASE civitas_db;
CREATE USER civitas_user WITH PASSWORD 'civitas_password';
GRANT ALL PRIVILEGES ON DATABASE civitas_db TO civitas_user;

-- Required: Enable PostGIS extension for geospatial features
\c civitas_db
CREATE EXTENSION IF NOT EXISTS postgis;
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Edit .env and configure environment variables (see below)
```

**Configure environment variables in backend/.env:**

```env
# Database Configuration
DATABASE_URL=postgresql://civitas_user:civitas_password@localhost:5432/civitas_db

# Application Settings
APP_NAME=Civitas Demo
DEBUG=True
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# AI / LLM Configuration (REQUIRED for AI dispatcher)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GROQ_API_KEY=your-groq-api-key-here  # Optional - alternative LLM provider
```

**Important**: The AI dispatcher will not function without a valid `ANTHROPIC_API_KEY`. Obtain one from the [Anthropic Console](https://console.anthropic.com/).

**Run database migrations:**

The project includes pre-configured Alembic migrations. Apply them to set up the database schema:

```bash
# Apply all migrations to create tables
alembic upgrade head
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Create .env file from example
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

**Configure environment variables in frontend/.env:**

```env
VITE_API_URL=http://localhost:8000
```

## Running the Application

### Start the Backend

```bash
cd backend
# Activate virtual environment if not already active
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Run the development server with auto-reload
python -m uvicorn src.main:app --reload
```

Backend will run on: http://localhost:8000
- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### Start the Frontend

```bash
cd frontend
npm run dev
```

Frontend will run on: http://localhost:5173

## Database Migrations

The project uses Alembic for database schema management. Migrations are located in the `backend/alembic/` directory.

### Common Migration Commands

```bash
cd backend

# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# View current migration version
alembic current
```

## Importing Sample Data

The project includes utility scripts for importing sample data from CSV files.

### Import Sample Tickets

```bash
cd backend
python scripts/import_tickets_from_csv.py data/sample_tickets.csv
```

### Import Sample Crews

```bash
cd backend
python scripts/import_crews_from_csv.py data/sample_crews.csv
```

### Transform NYC 311 Data

To use real NYC 311 service request data:

```bash
cd backend
# First, transform NYC 311 CSV format to Civitas ticket format
python scripts/transform_nyc_311_to_tickets.py data/nyc_311_data.csv data/transformed_tickets.csv

# Then import the transformed data
python scripts/import_tickets_from_csv.py data/transformed_tickets.csv
```

Sample CSV files are available in the `backend/data/` directory.

## API Endpoints

The backend provides a RESTful API for all operations. Full interactive documentation is available at http://localhost:8000/docs once the backend is running.

### Health Check
- `GET /` - Welcome message
- `GET /health` - Health check status

### Tickets API (`/api/tickets/`)
- `GET /api/tickets/` - List all tickets with optional filters
- `GET /api/tickets/{id}` - Get ticket details by ID
- `POST /api/tickets/` - Create new ticket
- `PUT /api/tickets/{id}` - Update ticket
- `DELETE /api/tickets/{id}` - Delete ticket

**Ticket Operations:**
- `POST /api/tickets/{id}/comments` - Add comment to ticket
- `GET /api/tickets/{id}/comments` - Get all comments for ticket
- `POST /api/tickets/{id}/users` - Assign user to ticket
- `DELETE /api/tickets/{ticket_id}/users/{user_id}` - Remove user assignment
- `POST /api/tickets/{id}/crews` - Assign crew to ticket
- `DELETE /api/tickets/{ticket_id}/crews/{crew_id}` - Remove crew assignment
- `POST /api/tickets/{id}/labels` - Add label to ticket
- `DELETE /api/tickets/{ticket_id}/labels/{label_id}` - Remove label
- `GET /api/tickets/{id}/update-logs` - Get audit trail for ticket

### AI Dispatcher API (`/api/dispatcher/`) - CORE FEATURE

- `POST /api/dispatcher/{ticket_id}/dispatch` - Run AI analysis on ticket

**Response includes:**
- Priority assessment (high/medium/low) with justification
- Recommended crew assignments with reasoning
- Recommended user assignments
- Suggested labels for categorization
- Professional response message for citizen

This endpoint leverages Claude AI with tool-calling to query the database and make intelligent dispatching decisions based on ticket content, location, and available resources.

### Crews API (`/api/crews/`)
- `GET /api/crews/` - List all crews
- `GET /api/crews/{id}` - Get crew details
- `POST /api/crews/` - Create new crew
- `PUT /api/crews/{id}` - Update crew
- `DELETE /api/crews/{id}` - Delete crew
- `GET /api/crews/nearest?lat={lat}&lon={lon}&crew_type={type}` - Find nearest crew (geospatial query)

### Users API (`/api/users/`)
- `GET /api/users/` - List all users
- `GET /api/users/{id}` - Get user details
- `POST /api/users/` - Create new user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Labels API (`/api/labels/`)
- `GET /api/labels/` - List all labels
- `GET /api/labels/{id}` - Get label details
- `POST /api/labels/` - Create new label
- `PUT /api/labels/{id}` - Update label
- `DELETE /api/labels/{id}` - Delete label

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run server with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run all tests
pytest

# Run tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_tickets_crud.py

# Run AI dispatcher tests
pytest tests/test_dispatcher_agent.py

# Run tests with coverage report
pytest --cov=src --cov-report=html
```

**Test Suite**: The project includes comprehensive backend tests covering all API endpoints, database operations, geospatial queries, and AI dispatcher functionality. See [backend/tests/README.md](backend/tests/README.md) for detailed test documentation.

**Utility Scripts**: The `backend/scripts/` directory contains helpful tools:
- `test_dispatcher.py` - Test AI dispatcher on sample tickets and measure accuracy
- `analyze_test_results.py` - Parse and analyze dispatcher test results
- `delete_all_tickets.py` - Clean up test data
- `delete_all_crews.py` - Clean up crew data
- Various SQL cleanup scripts

### Frontend Development

```bash
cd frontend

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Project Configuration

### CORS Configuration
The backend is configured to accept requests from:
- http://localhost:5173 (Vite default)
- http://localhost:3000 (Alternative React port)

Update `ALLOWED_ORIGINS` in `backend/.env` to add more origins for production deployment.

### Proxy Configuration
Vite is configured to proxy `/api` requests to the FastAPI backend at http://localhost:8000. This eliminates CORS issues during development.

See [frontend/vite.config.ts](frontend/vite.config.ts) for configuration details.

## Troubleshooting

### Backend won't start
- **Check PostgreSQL**: Verify PostgreSQL is running (`docker ps` if using Docker)
- **Verify DATABASE_URL**: Ensure connection string in `backend/.env` is correct
- **Install dependencies**: Run `pip install -r requirements.txt` in activated virtual environment
- **Check Python version**: Ensure Python 3.10+ is installed

### PostGIS extension not found
```bash
# Connect to your database
psql -U civitas_user -d civitas_db

# Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
```

### AI Dispatcher not working
- **Check API key**: Verify `ANTHROPIC_API_KEY` is set in `backend/.env`
- **Valid key**: Ensure the API key is valid and has available credits
- **Check logs**: Review `backend/logs/` for error messages
- **Network**: Ensure backend can reach Anthropic API (check firewall/proxy settings)

### Frontend can't connect to backend
- **Backend running**: Verify backend is running on http://localhost:8000
- **Check VITE_API_URL**: Ensure `frontend/.env` has correct API URL
- **CORS settings**: Verify `ALLOWED_ORIGINS` in `backend/.env` includes frontend URL
- **Clear cache**: Try clearing browser cache and restarting Vite dev server

### Database connection issues
- **PostgreSQL running**: `docker ps` (Docker) or check system services
- **Test connection**: `psql -U civitas_user -d civitas_db -h localhost`
- **Credentials**: Verify username/password in `backend/.env`
- **Port conflicts**: Ensure port 5432 is not already in use

### Map not loading
- **Mapbox token**: For production, you may need a Mapbox access token
- **Network**: Check browser console for map loading errors
- **Coordinates**: Ensure tickets have valid latitude/longitude values

---

This readme and all code in this project were generated by Claude Code. Some files and portions of this readme were modified.
