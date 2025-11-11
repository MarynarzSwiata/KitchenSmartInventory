"""
KitchenSmartInventory FastAPI Application

Main entry point for the Kitchen Smart Inventory API.
This file initializes the FastAPI application and
configures database table creation on startup.
"""

from fastapi import FastAPI
from src.database import create_db_and_tables
from src import models  # CRITICAL: Import models so SQLModel can discover them

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

app = FastAPI(
    title="KitchenSmartInventory API",
    description="Smart kitchen inventory management system",
    version="1.0.0",
)


# ============================================================================
# STARTUP EVENT
# ============================================================================


@app.on_event("startup")
def on_startup():
    """
    Runs automatically when the application starts.

    This function:
    1. Calls create_db_and_tables() to initialize the database
    2. Creates all tables defined in models.py (if they don't exist)

    The models import above is crucial - without it, SQLModel won't know
    about our table definitions and create_db_and_tables() won't work.
    """
    create_db_and_tables()


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
