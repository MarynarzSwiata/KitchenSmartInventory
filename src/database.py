from sqlmodel import create_engine, Session, SQLModel

# Database configuration
sqlite_file_name = "kitchen.db"
sqlite_url = f"sqlite:///./{sqlite_file_name}"

# Create engine with development settings
engine = create_engine(
    sqlite_url,
    echo=True,  # Print all SQL queries to console for development
    connect_args={"check_same_thread": False},  # Required for SQLite with FastAPI
)


# FastAPI dependency for database sessions
def get_session():
    """Generator function that yields a database session and ensures it's closed."""
    with Session(engine) as session:
        yield session


# Table creation function
def create_db_and_tables():
    """Create all database tables based on SQLModel metadata."""
    SQLModel.metadata.create_all(engine)
