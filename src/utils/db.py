from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import re

from src.utils.config import settings
from src.services.database import Base, metadata

# Convert async URL to sync URL
sync_db_url = re.sub(r'^postgresql\+asyncpg:', 'postgresql:', settings.DATABASE_URL)

# Create engine for synchronous access
engine = create_engine(sync_db_url, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_sync_db() -> Generator[Session, None, None]:
    """
    Get a synchronous database session.
    
    Yields:
        A SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_sync_db() -> None:
    """
    Initialize the database with tables.
    """
    Base.metadata.create_all(bind=engine) 