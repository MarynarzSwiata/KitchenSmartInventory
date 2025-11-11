"""
KitchenSmartInventory FastAPI Application

Main entry point for the Kitchen Smart Inventory API.
This file initializes the FastAPI application and
configures database table creation on startup.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from src.database import create_db_and_tables
from src import models  # CRITICAL: Import models so SQLModel can discover them
from src.models import Location
from src.services.location_service import LocationService

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    This replaces the deprecated @app.on_event("startup") and @app.on_event("shutdown").

    Startup logic (before yield):
    1. Calls create_db_and_tables() to initialize the database
    2. Creates all tables defined in models.py (if they don't exist)

    The models import above is crucial - without it, SQLModel won't know
    about our table definitions and create_db_and_tables() won't work.

    Shutdown logic (after yield):
    - Currently empty, but can be used for cleanup tasks
    """
    # Startup
    create_db_and_tables()
    yield
    # Shutdown (cleanup code would go here)


app = FastAPI(
    title="KitchenSmartInventory API",
    description="Smart kitchen inventory management system",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/")
def read_root():
    """
    Health check endpoint.

    Returns a simple message to verify the API is running.
    Access this at: http://localhost:8000/
    """
    return {"message": "KitchenSmartInventory API is running!"}


@app.post("/locations", response_model=Location)
def create_location(location_data: Location, service: LocationService = Depends()):
    """
    Create a new location in the kitchen.

    Args:
        location_data: Location object from request body (e.g., {"name": "Fridge"})
        service: LocationService injected by FastAPI's dependency injection

    Returns:
        Location: The created location with its database-assigned ID

    Example request body:
        {"name": "Fridge"}

    Example response:
        {"id": 1, "name": "Fridge"}

    The response_model=Location ensures FastAPI validates and formats the output.
    The Depends() automatically creates a LocationService
    instance with a database session.
    """
    return service.create_location(location_data)
