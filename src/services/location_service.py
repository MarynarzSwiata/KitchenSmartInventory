"""
Location Service Layer

This service handles all business logic and database operations for Locations.
It separates the database operations from the API endpoints, following best practices
for maintainable and testable code.

The service uses Dependency Injection to receive a database session from FastAPI.
"""

from fastapi import Depends
from sqlmodel import Session, select, func
from src.database import get_session
from src.models import Location


class LocationService:
    """
    Service layer for location-related operations.

    This class encapsulates all business logic for managing kitchen locations.
    It handles CRUD operations (Create, Read, Update, Delete) and any complex
    business rules related to locations.

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

    def create_location(self, location_data: Location) -> Location:
        """
        Create a new location in the database.

        Args:
            location_data: Location object containing the data to save
                          (typically created from API request body)

        Returns:
            Location: The saved location object with its database-assigned ID

        Process:
            1. Add the location to the session (stages it for saving)
            2. Commit the transaction (writes to database)
            3. Refresh the object (loads the assigned ID and any defaults)
            4. Return the complete object
        """
        self.session.add(location_data)
        self.session.commit()
        self.session.refresh(location_data)
        return location_data

    def get_all_locations(self, offset: int = 0, limit: int = 100) -> dict:
        """
        Retrieve all locations from the database with pagination.

        Args:
            offset: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            dict: Dictionary with 'total' count and 'items' list of locations

        Process:
            1. Create separate queries for counting and fetching items
            2. Execute count query to get total number of locations
            3. Apply pagination to items query and fetch results
            4. Return dictionary with total and items
        """
        # Build two separate queries
        items_query = select(Location)
        count_query = select(func.count()).select_from(Location)

        # Execute count query
        total = self.session.exec(count_query).one()

        # Apply pagination and execute items query
        items_query = items_query.offset(offset).limit(limit)
        items = self.session.exec(items_query).all()

        return {"total": total, "items": list(items)}
