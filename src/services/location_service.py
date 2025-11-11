"""
Location Service Layer

This service handles all business logic and database operations for Locations.
It separates the database operations from the API endpoints, following best practices
for maintainable and testable code.

The service uses Dependency Injection to receive a database session from FastAPI.
"""

from fastapi import Depends
from sqlmodel import Session, select
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

    def get_all_locations(self) -> list[Location]:
        """
        Retrieve all locations from the database.

        Returns:
            list[Location]: List of all location objects in the database
                           Returns empty list if no locations exist

        Process:
            1. Create a SELECT query for all Location records
            2. Execute the query and fetch all results
            3. Return the list of Location objects
        """
        locations = self.session.exec(select(Location)).all()
        return list(locations)
