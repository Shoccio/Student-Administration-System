"""
SQLAlchemy database configuration and session management.
Handles PostgreSQL connection, engine creation, and session factory.
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load .env (only if running locally, Docker can still inject env vars)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# =========================
# ENV VARIABLES
# =========================
DB_USER = os.getenv("POSTGRES_USER", "test_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "testing")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")  # Docker service name
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "test_db")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    future=True,
    pool_pre_ping=True,  # Verify connection before using
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session
)


def get_db():
    """
    Dependency injection function for FastAPI routes.
    Provides a database session and ensures cleanup.
    
    Usage in routes:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
