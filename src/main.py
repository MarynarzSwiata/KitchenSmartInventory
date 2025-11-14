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
from database import create_db_and_tables
from models import (
    Location,
    Store,
    Product,
    LocationRead,
    StoreRead,
    ProductRead,
    PaginatedResponse,
    InventoryItemCreate,
    InventoryItemReadWithRelations,
    ShoppingListItemCreate,
    ShoppingListItemReadWithRelations,
)
from services.location_service import LocationService
from services.store_service import StoreService
from services.product_service import ProductService
from services.inventory_service import InventoryService
from services.shopping_list_service import ShoppingListService

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


@app.post("/inventory_items", response_model=InventoryItemReadWithRelations)
def create_inventory_item(
    item: InventoryItemCreate, service: InventoryService = Depends()
):
    """
    Create a new inventory item.

    Validates that the referenced product, location, and store (if provided)
    exist before creating the item. Returns the created item with all
    related entities loaded.

    Args:
        item: InventoryItemCreate object from request body
        service: InventoryService injected by FastAPI's dependency injection

    Returns:
        InventoryItemReadWithRelations: The created item with related entities

    Raises:
        HTTPException 404: If product_id, location_id, or store_id not found

    Example request body:
        {
            "product_id": 1,
            "location_id": 2,
            "store_id": 1,
            "quantity": 2.5,
            "purchase_date": "2025-11-10",
            "expiration_date": "2025-11-20",
            "price": 12.99
        }

    Example response:
        {
            "id": 1,
            "product_id": 1,
            "location_id": 2,
            "store_id": 1,
            "quantity": 2.5,
            "purchase_date": "2025-11-10",
            "expiration_date": "2025-11-20",
            "price": 12.99,
            "created_at": "2025-11-12T10:30:00",
            "updated_at": "2025-11-12T10:30:00",
            "product": {"id": 1, "name": "Milk", "brand": "Łaciate", ...},
            "location": {"id": 2, "name": "Fridge", ...},
            "store": {"id": 1, "name": "Lidl", ...}
        }
    """
    return service.create_inventory_item(item)


@app.get(
    "/inventory_items", response_model=PaginatedResponse[InventoryItemReadWithRelations]
)
def get_inventory_items(
    service: InventoryService = Depends(),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=250),
    location_id: Optional[int] = Query(None, description="Filter by Location ID"),
    product_id: Optional[int] = Query(None, description="Filter by Product ID"),
):
    """
    Retrieve all inventory items with pagination and optional filtering.

    Returns items with all related entities (product, location, store) loaded.
    Supports filtering by location and/or product.

    Args:
        service: InventoryService injected by FastAPI's dependency injection
        offset: Number of records to skip (for pagination)
        limit: Maximum number of records to return (1-250)
        location_id: Optional filter by location ID
        product_id: Optional filter by product ID

    Returns:
        PaginatedResponse[InventoryItemReadWithRelations]: Paginated items

    Example response:
        {
            "total": 45,
            "offset": 0,
            "limit": 100,
            "items": [
                {
                    "id": 1,
                    "product_id": 1,
                    "location_id": 2,
                    "store_id": 1,
                    "quantity": 2.5,
                    "purchase_date": "2025-11-10",
                    "expiration_date": "2025-11-20",
                    "price": 12.99,
                    "created_at": "2025-11-12T10:30:00",
                    "updated_at": "2025-11-12T10:30:00",
                    "product": {"id": 1, "name": "Milk", "brand": "Łaciate", ...},
                    "location": {"id": 2, "name": "Fridge", ...},
                    "store": {"id": 1, "name": "Lidl", ...}
                }
            ]
        }

    Example queries:
        - All items: GET /inventory_items
        - Items in fridge: GET /inventory_items?location_id=2
        - Milk products: GET /inventory_items?product_id=1
        - Milk in fridge: GET /inventory_items?location_id=2&product_id=1
    """
    result = service.get_inventory_items(
        offset=offset, limit=limit, location_id=location_id, product_id=product_id
    )
    return PaginatedResponse(
        total=result["total"],
        items=result["items"],
        offset=offset,
        limit=limit,
    )


@app.get(
    "/locations/{location_id}/items",
    response_model=PaginatedResponse[InventoryItemReadWithRelations],
)
def get_location_items(
    location_id: int,
    service: InventoryService = Depends(),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=250),
    product_id: Optional[int] = Query(None, description="Filter by Product ID"),
    store_id: Optional[int] = Query(None, description="Filter by Store ID"),
):
    """
    Retrieve inventory items for a specific location.

    Returns paginated items assigned to the given location, with all related
    entities (product, location, store) loaded. Supports optional filtering
    by product and/or store.

    Args:
        location_id: The ID of the location to retrieve items for
        service: InventoryService injected by FastAPI's dependency injection
        offset: Number of records to skip (for pagination)
        limit: Maximum number of records to return (1-250)
        product_id: Optional filter by product ID
        store_id: Optional filter by store ID

    Returns:
        PaginatedResponse[InventoryItemReadWithRelations]: Paginated items

    Raises:
        HTTPException 404: If location with given ID does not exist

    Example response:
        {
            "total": 12,
            "offset": 0,
            "limit": 100,
            "items": [
                {
                    "id": 1,
                    "product_id": 1,
                    "location_id": 2,
                    "store_id": 1,
                    "quantity": 2.5,
                    "purchase_date": "2025-11-10",
                    "expiration_date": "2025-11-20",
                    "price": 12.99,
                    "created_at": "2025-11-12T10:30:00",
                    "updated_at": "2025-11-12T10:30:00",
                    "product": {"id": 1, "name": "Milk", "brand": "Łaciate", ...},
                    "location": {"id": 2, "name": "Fridge", ...},
                    "store": {"id": 1, "name": "Lidl", ...}
                }
            ]
        }

    Example queries:
        - All items in fridge: GET /locations/2/items
        - Milk in fridge: GET /locations/2/items?product_id=1
        - Items from Lidl in fridge: GET /locations/2/items?store_id=1
        - Milk from Lidl in fridge: GET /locations/2/items?product_id=1&store_id=1
    """
    result = service.get_inventory_items_for_location(
        location_id=location_id,
        offset=offset,
        limit=limit,
        product_id=product_id,
        store_id=store_id,
    )
    return PaginatedResponse(
        total=result["total"],
        items=result["items"],
        offset=offset,
        limit=limit,
    )


@app.post("/shopping-list", response_model=ShoppingListItemReadWithRelations)
def create_shopping_list_item(
    item_data: ShoppingListItemCreate, service: ShoppingListService = Depends()
):
    """
    Create a new shopping list item.

    Validates that the referenced product and store (if provided) exist
    before creating the item. Returns the created item with all related
    entities loaded.

    Args:
        item_data: ShoppingListItemCreate object from request body
        service: ShoppingListService injected by FastAPI's dependency injection

    Returns:
        ShoppingListItemReadWithRelations: The created item with related entities

    Raises:
        HTTPException 404: If product_id or store_id not found

    Example request body:
        {
            "product_id": 1,
            "store_id": 2,
            "quantity": 3.0,
            "note": "Buy the large pack"
        }

    Example response:
        {
            "id": 1,
            "product_id": 1,
            "store_id": 2,
            "quantity": 3.0,
            "note": "Buy the large pack",
            "created_at": "2025-11-12T14:30:00",
            "updated_at": "2025-11-12T14:30:00",
            "product": {"id": 1, "name": "Milk", "brand": "Łaciate", ...},
            "store": {"id": 2, "name": "Lidl", ...}
        }
    """
    return service.create_shopping_list_item(item_data)


@app.get(
    "/shopping-list",
    response_model=PaginatedResponse[ShoppingListItemReadWithRelations],
)
def get_shopping_list(
    service: ShoppingListService = Depends(),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=250),
    product_id: Optional[int] = Query(None, description="Filter by Product ID"),
    store_id: Optional[int] = Query(None, description="Filter by Store ID"),
):
    """
    Retrieve all shopping list items with pagination and optional filtering.

    Returns items with all related entities (product, store) loaded.
    Supports filtering by product and/or store.

    Args:
        service: ShoppingListService injected by FastAPI's dependency injection
        offset: Number of records to skip (for pagination)
        limit: Maximum number of records to return (1-250)
        product_id: Optional filter by product ID
        store_id: Optional filter by store ID

    Returns:
        PaginatedResponse[ShoppingListItemReadWithRelations]: Paginated items

    Example response:
        {
            "total": 8,
            "offset": 0,
            "limit": 100,
            "items": [
                {
                    "id": 1,
                    "product_id": 1,
                    "store_id": 2,
                    "quantity": 3.0,
                    "note": "Buy the large pack",
                    "created_at": "2025-11-12T14:30:00",
                    "updated_at": "2025-11-12T14:30:00",
                    "product": {"id": 1, "name": "Milk", "brand": "Łaciate", ...},
                    "store": {"id": 2, "name": "Lidl", ...}
                }
            ]
        }

    Example queries:
        - All items: GET /shopping-list
        - Specific product: GET /shopping-list?product_id=1
        - Items from specific store: GET /shopping-list?store_id=2
        - Product from store: GET /shopping-list?product_id=1&store_id=2
    """
    result = service.get_shopping_list(
        offset=offset, limit=limit, product_id=product_id, store_id=store_id
    )
    return PaginatedResponse(
        total=result["total"],
        items=result["items"],
        offset=offset,
        limit=limit,
    )


@app.delete("/shopping-list/{item_id}")
def delete_shopping_list_item(item_id: int, service: ShoppingListService = Depends()):
    """
    Delete a shopping list item by its ID.

    Args:
        item_id: The ID of the shopping list item to delete
        service: ShoppingListService injected by FastAPI's dependency injection

    Returns:
        dict: Success indicator {"ok": True}

    Raises:
        HTTPException 404: If item with given ID does not exist

    Example response:
        {"ok": true}
    """
    return service.delete_shopping_list_item(item_id)
