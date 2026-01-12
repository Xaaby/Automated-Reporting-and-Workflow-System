from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
import logging
from dotenv import load_dotenv

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Get database URL from environment
# Default to SQLite for easy testing (no PostgreSQL required)
# Force SQLite if DATABASE_URL is not explicitly set or if it's set to PostgreSQL
env_db_url = os.getenv("DATABASE_URL", "")
if not env_db_url or env_db_url.startswith("postgresql"):
    # Use SQLite by default (no PostgreSQL required)
    DATABASE_URL = "sqlite:///./reporting.db"
    logger.info(f"Using SQLite database: {DATABASE_URL}")
    if env_db_url.startswith("postgresql"):
        logger.warning(f"PostgreSQL URL detected in environment, but using SQLite instead. To use PostgreSQL, ensure it's running and set DATABASE_URL correctly.")
else:
    DATABASE_URL = env_db_url
    logger.info(f"Using database: {DATABASE_URL}")

# Create engine with connection pooling
# SQLite requires check_same_thread=False for FastAPI
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool if not DATABASE_URL.startswith("sqlite") else None,  # SQLite doesn't need NullPool
    connect_args=connect_args,
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
        if DATABASE_URL.startswith("sqlite"):
            logger.warning("Please ensure the database file directory is writable.")
        else:
            logger.warning("Please ensure the database is running and DATABASE_URL is correct.")
