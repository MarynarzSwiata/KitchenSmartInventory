"""
KitchenSmartInventory FastAPI Application

Main entry point for the Kitchen Smart Inventory API.
This file initializes the FastAPI application and
configures database table creation on startup.
"""

from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from src.database import create_db_and_tables
from src.models import (
    Location,
    Store,
    Product,
    LocationRead,
    StoreRead,
    ProductRead,
    PaginatedResponse,
)
from src.services.location_service import LocationService
from src.services.store_service import StoreService
from src.services.product_service import ProductService

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


@app.post("/locations", response_model=LocationRead)
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


@app.get("/locations", response_model=PaginatedResponse[LocationRead])
def get_all_locations(
    service: LocationService = Depends(),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=250),
):
    """
    Retrieve all locations from the database with pagination.

    Args:
        service: LocationService injected by FastAPI's dependency injection
        offset: Number of records to skip (for pagination)
        limit: Maximum number of records to return (1-250)

    Returns:
        PaginatedResponse[LocationRead]: Paginated locations with metadata

    Example response:
        {
            "total": 5,
            "offset": 0,
            "limit": 100,
            "items": [
                {"id": 1, "name": "Fridge", "created_at": "...", "updated_at": "..."},
                {"id": 2, "name": "Pantry", "created_at": "...", "updated_at": "..."}
            ]
        }
    """
    result = service.get_all_locations(offset=offset, limit=limit)
    return PaginatedResponse(
        total=result["total"],
        items=result["items"],
        offset=offset,
        limit=limit,
    )


@app.post("/stores", response_model=StoreRead)
def create_store(store_data: Store, service: StoreService = Depends()):
    """
    Create a new store in the database.

    Args:
        store_data: Store object from request body (e.g., {"name": "Lidl"})
        service: StoreService injected by FastAPI's dependency injection

    Returns:
        Store: The created store with its database-assigned ID

    Example request body:
        {"name": "Lidl"}

    Example response:
        {"id": 1, "name": "Lidl"}

    The response_model=Store ensures FastAPI validates and formats the output.
    The Depends() automatically creates a StoreService instance with a database session.
    """
    return service.create_store(store_data)


@app.get("/stores", response_model=PaginatedResponse[StoreRead])
def get_all_stores(
    service: StoreService = Depends(),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=250),
):
    """
    Retrieve all stores from the database with pagination.

    Args:
        service: StoreService injected by FastAPI's dependency injection
        offset: Number of records to skip (for pagination)
        limit: Maximum number of records to return (1-250)

    Returns:
        PaginatedResponse[StoreRead]: Paginated stores with metadata

    Example response:
        {
            "total": 3,
            "offset": 0,
            "limit": 100,
            "items": [
                {"id": 1, "name": "Lidl", "created_at": "...", "updated_at": "..."},
                {"id": 2, "name": "Biedronka", "created_at": "...", "updated_at": "..."}
            ]
        }
    """
    result = service.get_all_stores(offset=offset, limit=limit)
    return PaginatedResponse(
        total=result["total"],
        items=result["items"],
        offset=offset,
        limit=limit,
    )


@app.post("/products", response_model=ProductRead)
def create_product(product_data: Product, service: ProductService = Depends()):
    """
    Create a new product in the database.

    Args:
        product_data: Product object from request body
        service: ProductService injected by FastAPI's dependency injection

    Returns:
        ProductRead: The created product with ID and timestamps

    Example request body:
        {"name": "Milk", "brand": "Łaciate"}

    Example response:
        {
            "id": 1,
            "name": "Milk",
            "brand": "Łaciate",
            "created_at": "2025-11-12T10:30:00",
            "updated_at": "2025-11-12T10:30:00"
        }
    """
    try:
        return service.create_product(product_data)
    except IntegrityError:
        service.session.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                f"Product '{product_data.name}' with brand "
                f"'{product_data.brand}' already exists."
            ),
        )


@app.get("/products", response_model=PaginatedResponse[ProductRead])
def get_all_products(
    service: ProductService = Depends(),
    name: Optional[str] = Query(
        None, description="Filter by product name (case-insensitive)"
    ),
    brand: Optional[str] = Query(
        None, description="Filter by brand name (case-insensitive)"
    ),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=250),
):
    """
    Retrieve all products from the database with pagination.

    Args:
        service: ProductService injected by FastAPI's dependency injection
        name: Optional filter by product name (case-insensitive)
        brand: Optional filter by brand name (case-insensitive)
        offset: Number of records to skip (for pagination)
        limit: Maximum number of records to return (1-250)

    Returns:
        PaginatedResponse[ProductRead]: Paginated products with metadata

    Example response:
        {
            "total": 150,
            "offset": 0,
            "limit": 100,
            "items": [
                {
                    "id": 1,
                    "name": "Milk",
                    "brand": "Łaciate",
                    "created_at": "2025-11-12T10:30:00",
                    "updated_at": "2025-11-12T10:30:00"
                }
            ]
        }
    """
    result = service.get_all_products(
        name=name, brand=brand, offset=offset, limit=limit
    )
    return PaginatedResponse(
        total=result["total"],
        items=result["items"],
        offset=offset,
        limit=limit,
    )
