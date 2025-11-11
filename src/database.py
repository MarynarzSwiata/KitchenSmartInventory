"""
Database connection and session management for Kitchen Smart Inventory.

This module is responsible for:
- Configuring the database connection (SQLite)
- Creating the SQLAlchemy engine
- Providing database sessions for FastAPI endpoints
- Creating database tables on application startup

Usage:
    In FastAPI endpoints, use get_session() as a dependency to get a database session.
    Call create_db_and_tables() once during application startup to initialize tables.
"""

from sqlmodel import create_engine, Session, SQLModel

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# SQLite database file configuration
# The database file will be created in the project root directory
sqlite_file_name = "database.db"

# Create the SQLite connection URL
# Format: sqlite:///./filename.db
# The './' makes the path relative to where the application runs (project root)
sqlite_url = f"sqlite:///./{sqlite_file_name}"

# ============================================================================
# ENGINE CREATION
# ============================================================================

# Create the SQLAlchemy engine - the core interface to the database
# This engine will be used for all database operations
engine = create_engine(
    sqlite_url,
    echo=True,  # DEVELOPMENT SETTING: Print all SQL queries to console
    # This helps us see what SQL is being generated
    # Set to False in production for better performance
    connect_args={
        "check_same_thread": False
    },  # SQLITE SPECIFIC: Allow multiple threads
    # FastAPI uses multiple threads, but SQLite
    # by default only allows same-thread access
    # This setting disables that check
)


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================


def get_session():
    """
    FastAPI dependency that provides a database session.

    This is a generator function that:
    1. Creates a new database session
    2. Yields it to the endpoint function
    3. Automatically closes the session when done (even if an error occurs)

    Usage in FastAPI:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            items = session.exec(select(InventoryItem)).all()
            return items

    The 'with' statement ensures the session is always closed properly,
    preventing database connection leaks.
    """
    with Session(engine) as session:
        yield session


# ============================================================================
# TABLE CREATION
# ============================================================================


def create_db_and_tables():
    """
    Create all database tables based on SQLModel class definitions.

    This function should be called ONCE during application startup.
    It will:
    1. Read all SQLModel classes marked with table=True
    2. Generate CREATE TABLE SQL statements
    3. Execute them to create tables in the database

    If tables already exist, this function does nothing (safe to call multiple times).

    Call this in main.py during a startup event:
        @app.on_event("startup")
        def on_startup():
            create_db_and_tables()

    Important: Models must be imported BEFORE calling this function,
    otherwise SQLModel won't know about them.
    """
    SQLModel.metadata.create_all(engine)
