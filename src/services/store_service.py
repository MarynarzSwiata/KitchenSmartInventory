"""
Store Service Layer

This service handles all business logic and database operations for Stores.
It separates the database operations from the API endpoints, following best practices
for maintainable and testable code.

The service uses Dependency Injection to receive a database session from FastAPI.
"""

from fastapi import Depends
from sqlmodel import Session, select, func
from database import get_session
from models import Store


class StoreService:
    """
    Service layer for store-related operations.

    This class encapsulates all business logic for managing stores where products
    can be purchased. It handles CRUD operations (Create, Read, Update, Delete) and
    any complex business rules related to stores.

    The service receives a database session through FastAPI's dependency injection,
    ensuring proper session management and lifecycle.
    """

    def __init__(self, session: Session = Depends(get_session)):
        """
        Initialize the service with a database session.

        Args:
            session: Database session provided by FastAPI's Depends(get_session)
                    This session is automatically managed - opened before the request
                    and closed after the response is sent.
        """
        self.session = session

    def create_store(self, store_data: Store) -> Store:
        """
        Create a new store in the database.

        Args:
            store_data: Store object containing the data to save
                       (typically created from API request body)

        Returns:
            Store: The saved store object with its database-assigned ID

        Process:
            1. Add the store to the session (stages it for saving)
            2. Commit the transaction (writes to database)
            3. Refresh the object (loads the assigned ID and any defaults)
            4. Return the complete object
        """
        self.session.add(store_data)
        self.session.commit()
        self.session.refresh(store_data)
        return store_data

    def get_all_stores(self, offset: int = 0, limit: int = 100) -> dict:
        """
        Retrieve all stores from the database with pagination.

        Args:
            offset: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            dict: Dictionary with 'total' count and 'items' list of stores

        Process:
            1. Create separate queries for counting and fetching items
            2. Execute count query to get total number of stores
            3. Apply pagination to items query and fetch results
            4. Return dictionary with total and items
        """
        # Build two separate queries
        items_query = select(Store)
        count_query = select(func.count()).select_from(Store)

        # Execute count query
        total = self.session.exec(count_query).one()

        # Apply pagination and execute items query
        items_query = items_query.offset(offset).limit(limit)
        items = self.session.exec(items_query).all()

        return {"total": total, "items": list(items)}
