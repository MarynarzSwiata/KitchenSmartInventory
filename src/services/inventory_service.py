"""
Service layer for managing inventory items.

This module handles all business logic for inventory operations, including:
- CRUD operations (Create, Read, Update, Delete)
- Foreign key validation (Task 028)
- Filtering and pagination
- Data integrity checks

The service ensures that all inventory items reference valid products,
locations, and stores before persisting to the database.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select, func

from database import get_session
from models import (
    InventoryItem,
    InventoryItemCreate,
    InventoryItemUpdate,
    Product,
    Location,
    Store,
)


class InventoryService:
    """
    Service layer for managing inventory items, including CRUD operations
    and business logic (like FK validation).
    """

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get_item_by_id(self, item_id: int) -> InventoryItem:
        """
        Internal helper to get an item by ID or raise 404.

        Args:
            item_id: The ID of the inventory item to retrieve

        Returns:
            InventoryItem: The retrieved inventory item

        Raises:
            HTTPException: 404 if item not found
        """
        item = self.session.get(InventoryItem, item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"InventoryItem with id {item_id} not found",
            )
        return item

    def _ensure_location_exists(self, location_id: int):
        """
        Internal helper to validate that a location exists.

        Args:
            location_id: The ID of the location to validate

        Raises:
            HTTPException: 404 if location not found
        """
        if not self.session.get(Location, location_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with id {location_id} not found",
            )

    def _validate_foreign_keys(
        self,
        product_id: int,
        location_id: int,
        store_id: Optional[int] = None,
    ):
        """
        (Task 028)
        Validates the existence of related entities before C/U operations.

        This prevents database integrity errors by checking that all foreign
        key references point to existing records before attempting to create
        or update an inventory item.

        Args:
            product_id: ID of the product to validate
            location_id: ID of the location to validate
            store_id: Optional ID of the store to validate

        Raises:
            HTTPException: 404 if any related entity is not found
        """
        if not self.session.get(Product, product_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found",
            )
        if not self.session.get(Location, location_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with id {location_id} not found",
            )
        if store_id and not self.session.get(Store, store_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store with id {store_id} not found",
            )

    def create_inventory_item(self, item_create: InventoryItemCreate) -> InventoryItem:
        """
        Creates a new inventory item after validating foreign keys.

        This method ensures data integrity by validating that all referenced
        entities (product, location, store) exist before creating the item.

        Args:
            item_create: The inventory item data to create

        Returns:
            InventoryItem: The created inventory item with generated ID

        Raises:
            HTTPException: 404 if any foreign key reference is invalid
        """
        # 1. Validate FKs (Task 028)
        self._validate_foreign_keys(
            product_id=item_create.product_id,
            location_id=item_create.location_id,
            store_id=item_create.store_id,
        )

        # 2. Create model
        db_item = InventoryItem.model_validate(item_create)

        # 3. Save to DB
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    def get_inventory_item(self, item_id: int) -> InventoryItem:
        """
        Gets a single inventory item by its ID.

        The endpoint will use response_model=InventoryItemReadWithRelations
        to automatically load and return related entities (product, location, store).

        Args:
            item_id: The ID of the inventory item to retrieve

        Returns:
            InventoryItem: The retrieved inventory item

        Raises:
            HTTPException: 404 if item not found
        """
        return self._get_item_by_id(item_id)

    def get_inventory_items(
        self,
        offset: int,
        limit: int,
        location_id: Optional[int] = None,
        product_id: Optional[int] = None,
    ) -> dict:
        """
        Gets a paginated list of inventory items, with optional filters.

        Uses the optimized two-query pattern from contract 025:
        - Direct count query (no subquery)
        - Separate items query with offset/limit
        - Same filters applied to both queries

        Args:
            offset: Number of records to skip (pagination)
            limit: Maximum number of records to return
            location_id: Optional filter by location
            product_id: Optional filter by product

        Returns:
            dict: Dictionary with 'total' count and 'items' list
        """
        # Base query for items
        items_query = select(InventoryItem)

        # Apply filters to items query
        if location_id is not None:
            items_query = items_query.where(InventoryItem.location_id == location_id)
        if product_id is not None:
            items_query = items_query.where(InventoryItem.product_id == product_id)

        # Get paginated results
        items = self.session.exec(items_query.offset(offset).limit(limit)).all()

        # Optimized count query (no subquery) - per contract 025
        count_query = select(func.count()).select_from(InventoryItem)

        # Apply same filters to count query
        if location_id is not None:
            count_query = count_query.where(InventoryItem.location_id == location_id)
        if product_id is not None:
            count_query = count_query.where(InventoryItem.product_id == product_id)

        total = self.session.exec(count_query).one()

        return {"total": total, "items": list(items)}

    def get_inventory_items_for_location(
        self,
        location_id: int,
        offset: int,
        limit: int,
        product_id: Optional[int] = None,
        store_id: Optional[int] = None,
    ) -> dict:
        """
        Gets paginated inventory items for a specific location.

        This method validates that the location exists, then retrieves all
        inventory items in that location with optional filtering by product
        and/or store. Uses the same optimized two-query pattern as
        get_inventory_items.

        Args:
            location_id: ID of the location to filter by (required)
            offset: Number of records to skip (pagination)
            limit: Maximum number of records to return
            product_id: Optional filter by product ID
            store_id: Optional filter by store ID

        Returns:
            dict: Dictionary with 'total' count and 'items' list,
                  ready to be wrapped in PaginatedResponse

        Raises:
            HTTPException: 404 if location not found
        """
        # Validate that location exists
        self._ensure_location_exists(location_id)

        # Base query for items (always filtered by location)
        items_query = select(InventoryItem).where(
            InventoryItem.location_id == location_id
        )

        # Apply optional filters
        if product_id is not None:
            items_query = items_query.where(InventoryItem.product_id == product_id)
        if store_id is not None:
            items_query = items_query.where(InventoryItem.store_id == store_id)

        # Get paginated results
        items = self.session.exec(items_query.offset(offset).limit(limit)).all()

        # Optimized count query (no subquery) - per contract 025
        count_query = (
            select(func.count())
            .select_from(InventoryItem)
            .where(InventoryItem.location_id == location_id)
        )

        # Apply same optional filters to count query
        if product_id is not None:
            count_query = count_query.where(InventoryItem.product_id == product_id)
        if store_id is not None:
            count_query = count_query.where(InventoryItem.store_id == store_id)

        total = self.session.exec(count_query).one()

        return {"total": total, "items": list(items)}

    def update_inventory_item(
        self, item_id: int, item_update: InventoryItemUpdate
    ) -> InventoryItem:
        """
        Updates an inventory item.

        Only updates fields that are explicitly provided in the request.
        Validates foreign keys if they are being changed.

        Args:
            item_id: The ID of the item to update
            item_update: The update data (partial update supported)

        Returns:
            InventoryItem: The updated inventory item

        Raises:
            HTTPException: 404 if item not found or foreign key invalid
        """
        db_item = self._get_item_by_id(item_id)

        # 1. Validate FKs (Task 028) if they are being changed
        if (
            item_update.product_id
            or item_update.location_id
            or item_update.store_id is not None
        ):
            self._validate_foreign_keys(
                product_id=item_update.product_id or db_item.product_id,
                location_id=item_update.location_id or db_item.location_id,
                store_id=(
                    item_update.store_id
                    if item_update.store_id is not None
                    else db_item.store_id
                ),
            )

        # 2. Update data (only fields provided in request)
        update_data = item_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)

        # 3. Save to DB
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    def delete_inventory_item(self, item_id: int):
        """
        Deletes an inventory item by its ID.

        Args:
            item_id: The ID of the item to delete

        Returns:
            dict: Success indicator

        Raises:
            HTTPException: 404 if item not found
        """
        db_item = self._get_item_by_id(item_id)
        self.session.delete(db_item)
        self.session.commit()
        return {"ok": True}
