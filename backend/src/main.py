from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .routers import items, tickets, crews

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

# Configure CORS
origins = settings.allowed_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")
app.include_router(crews.router, prefix="/api")


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to Civitas Demo API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
