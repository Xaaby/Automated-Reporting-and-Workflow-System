from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://reporting_user:reporting_pass@localhost:5432/reporting_db"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Use NullPool for simpler connection management
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    This should be called on application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger = logging.getLogger(__name__)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not initialize database tables: {str(e)}")
        logger.warning("The application will continue, but database operations may fail.")
        logger.warning("Please ensure PostgreSQL is running and DATABASE_URL is correct.")
