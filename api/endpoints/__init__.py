from typing import Generator

from api.db.session import SessionLocal


def get_db() -> Generator:
    """Create a local session from factory and return the generator db."""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
