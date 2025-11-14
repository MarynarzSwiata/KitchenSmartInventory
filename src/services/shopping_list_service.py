"""
Service layer for managing shopping list items.

This module handles all business logic for shopping list operations, including:
- CRUD operations (Create, Read, Delete)
- Foreign key validation
- Filtering and pagination
- Data integrity checks

The service ensures that all shopping list items reference valid products
and stores before persisting to the database.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select, func

from database import get_session
from models import (
    ShoppingListItem,
    ShoppingListItemCreate,
    Product,
    Store,
)


class ShoppingListService:
    """
    Service layer for managing shopping list items, including CRUD operations
    and business logic (like FK validation).
    """

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get_item_by_id(self, item_id: int) -> ShoppingListItem:
        """
        Internal helper to get a shopping list item by ID or raise 404.

        Args:
            item_id: The ID of the shopping list item to retrieve

        Returns:
            ShoppingListItem: The retrieved shopping list item

        Raises:
            HTTPException: 404 if item not found
        """
        item = self.session.get(ShoppingListItem, item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ShoppingListItem with id {item_id} not found",
            )
        return item

    def _validate_foreign_keys(
        self,
        product_id: int,
        store_id: Optional[int] = None,
    ):
        """
        Validates the existence of related entities before create operations.

        This prevents database integrity errors by checking that all foreign
        key references point to existing records before attempting to create
        a shopping list item.

        Args:
            product_id: ID of the product to validate
            store_id: Optional ID of the store to validate

        Raises:
            HTTPException: 404 if any related entity is not found
        """
        if not self.session.get(Product, product_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found",
            )
        if store_id and not self.session.get(Store, store_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store with id {store_id} not found",
            )

    def create_shopping_list_item(
        self, item_create: ShoppingListItemCreate
    ) -> ShoppingListItem:
        """
        Creates a new shopping list item after validating foreign keys.

        This method ensures data integrity by validating that all referenced
        entities (product, store) exist before creating the item.

        Args:
            item_create: The shopping list item data to create

        Returns:
            ShoppingListItem: The created shopping list item with generated ID
                              and populated relationships (product, store)

        Raises:
            HTTPException: 404 if any foreign key reference is invalid
        """
        # 1. Validate FKs
        self._validate_foreign_keys(
            product_id=item_create.product_id,
            store_id=item_create.store_id,
        )

        # 2. Create model
        db_item = ShoppingListItem.model_validate(item_create)

        # 3. Save to DB
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    def get_shopping_list(
        self,
        offset: int,
        limit: int,
        product_id: Optional[int] = None,
        store_id: Optional[int] = None,
    ) -> dict:
        """
        Gets a paginated list of shopping list items, with optional filters.

        Uses the optimized two-query pattern:
        - Direct count query (no subquery)
        - Separate items query with offset/limit
        - Same filters applied to both queries

        The returned items will have their relationships (product, store)
        automatically loaded when serialized with ShoppingListItemReadWithRelations.

        Args:
            offset: Number of records to skip (pagination)
            limit: Maximum number of records to return
            product_id: Optional filter by product ID
            store_id: Optional filter by store ID

        Returns:
            dict: Dictionary with 'total' count and 'items' list,
                  ready to be wrapped in PaginatedResponse
        """
        # Base query for items
        items_query = select(ShoppingListItem)

        # Apply filters to items query
        if product_id is not None:
            items_query = items_query.where(ShoppingListItem.product_id == product_id)
        if store_id is not None:
            items_query = items_query.where(ShoppingListItem.store_id == store_id)

        # Get paginated results
        items = self.session.exec(items_query.offset(offset).limit(limit)).all()

        # Optimized count query (no subquery)
        count_query = select(func.count()).select_from(ShoppingListItem)

        # Apply same filters to count query
        if product_id is not None:
            count_query = count_query.where(ShoppingListItem.product_id == product_id)
        if store_id is not None:
            count_query = count_query.where(ShoppingListItem.store_id == store_id)

        total = self.session.exec(count_query).one()

        return {"total": total, "items": list(items)}

    def delete_shopping_list_item(self, item_id: int):
        """
        Deletes a shopping list item by its ID.

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
