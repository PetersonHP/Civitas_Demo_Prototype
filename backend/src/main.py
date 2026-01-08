from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from .config import get_settings
from .routers import items, tickets, crews, users, labels, dispatcher

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
app.include_router(users.router, prefix="/api")
app.include_router(labels.router, prefix="/api")
app.include_router(dispatcher.router, prefix="/api")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Serve frontend static files (for production)
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    # Serve index.html for root
    @app.get("/")
    def serve_frontend():
        """Serve the frontend index.html"""
        return FileResponse(frontend_dist / "index.html")

    # Catch-all route for client-side routing (SPA)
    @app.get("/{full_path:path}")
    def serve_frontend_routes(full_path: str):
        """Serve frontend for all non-API routes"""
        if full_path.startswith("api/") or full_path == "health" or full_path == "docs" or full_path == "redoc" or full_path == "openapi.json":
            raise HTTPException(status_code=404)
        return FileResponse(frontend_dist / "index.html")
else:
    # Fallback for development
    @app.get("/")
    def read_root():
        """Root endpoint."""
        return {
            "message": "Welcome to Civitas Demo API",
            "version": "1.0.0",
            "docs": "/docs",
        }
