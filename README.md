# Civitas Demo - Full Stack Application

A modern full-stack application with FastAPI backend, PostgreSQL database, and React + Vite frontend.

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Axios** - HTTP client

## Project Structure

```
Civitas_Demo_Prototype/
├── backend/
│   ├── src/
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── config.py         # Configuration management
│   │   ├── database.py       # Database connection
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── routers/          # API endpoints
│   │   └── services/         # Business logic
│   ├── tests/                # Backend tests
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API service layer
│   │   ├── App.tsx           # Main App component
│   │   └── main.tsx          # Entry point
│   ├── package.json          # Node dependencies
│   ├── vite.config.ts        # Vite configuration
│   └── .env.example          # Frontend environment variables
└── docker-compose.yml        # PostgreSQL container
```

## Prerequisites

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** and npm - [Download](https://nodejs.org/)
- **Docker** (optional, for PostgreSQL) - [Download](https://www.docker.com/products/docker-desktop/)
- **PostgreSQL** (if not using Docker)

## Setup Instructions

### 1. Database Setup

**Option A: Using Docker (Recommended)**

```bash
docker-compose up -d
```

**Option B: Install PostgreSQL locally**

Install PostgreSQL and create a database:

```sql
CREATE DATABASE civitas_db;
CREATE USER civitas_user WITH PASSWORD 'civitas_password';
GRANT ALL PRIVILEGES ON DATABASE civitas_db TO civitas_user;
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

# Edit .env and update DATABASE_URL if needed
```

**Configure environment variables in backend/.env:**

```env
DATABASE_URL=postgresql://civitas_user:civitas_password@localhost:5432/civitas_db
APP_NAME=Civitas Demo
DEBUG=True
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
SECRET_KEY=your-secret-key-here
```

**Initialize the database:**

```bash
# Create database tables (for now, we'll use SQLAlchemy directly)
# You can set up Alembic migrations later

# Run the application to create tables
python -m uvicorn src.main:app --reload
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

# Run the server
python -m uvicorn src.main:app --reload
```

Backend will run on: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Start the Frontend

```bash
cd frontend
npm run dev
```

Frontend will run on: http://localhost:5173

## Database Migrations (Optional Setup)

To set up Alembic for database migrations:

```bash
cd backend

# Initialize Alembic
alembic init alembic

# Edit alembic.ini and set:
# sqlalchemy.url = postgresql://civitas_user:civitas_password@localhost:5432/civitas_db

# Edit alembic/env.py and import your models
# Add: from src.database import Base
# Add: target_metadata = Base.metadata

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## API Endpoints

### Health Check
- `GET /` - Welcome message
- `GET /health` - Health check

### Items (Example CRUD)
- `GET /api/items/` - Get all items
- `GET /api/items/{id}` - Get item by ID
- `POST /api/items/` - Create new item
- `PUT /api/items/{id}` - Update item
- `DELETE /api/items/{id}` - Delete item

## Development

### Backend Development

```bash
# Run tests
pytest

# Run with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
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

Update `ALLOWED_ORIGINS` in backend/.env to add more origins.

### Proxy Configuration
Vite is configured to proxy `/api` requests to the FastAPI backend at http://localhost:8000.

See [frontend/vite.config.ts](frontend/vite.config.ts) for configuration.

## Next Steps

1. **Database Migrations**: Set up Alembic for managing database schema changes
2. **Authentication**: Add user authentication (JWT, OAuth, etc.)
3. **Testing**: Add comprehensive tests for backend and frontend
4. **Styling**: Enhance UI with a component library (Material-UI, Chakra UI, etc.)
5. **State Management**: Add Redux, Zustand, or React Query for complex state
6. **Deployment**: Configure for production deployment

## Troubleshooting

### Backend won't start
- Check if PostgreSQL is running
- Verify DATABASE_URL in backend/.env
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### Frontend can't connect to backend
- Verify backend is running on http://localhost:8000
- Check VITE_API_URL in frontend/.env
- Check CORS settings in backend/src/main.py

### Database connection issues
- Verify PostgreSQL is running: `docker ps` (if using Docker)
- Test connection: `psql -U civitas_user -d civitas_db -h localhost`
- Check credentials in backend/.env

## License

MIT
