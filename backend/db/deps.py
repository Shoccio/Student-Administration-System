"""
FastAPI dependency injection for database session.
Use Depends(get_db) in route handlers to inject a database session.
"""
from db.database import SessionLocal
from sqlalchemy.orm import Session


def get_db() -> Session:
    """
    Dependency function that provides a database session to FastAPI routes.
    Automatically closes the session after the request completes.
    
    Usage in routes:
        from fastapi import Depends
        from sqlalchemy.orm import Session
        from db.deps import get_db
        
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
