# automotive_invoice_manager/backend/database/connection.py - FIXED
"""Database connection utilities using SQLAlchemy with FIXED session management."""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from automotive_invoice_manager.config.database import DatabaseConfig


class DatabaseManager:
    """Singleton class managing the SQLAlchemy engine and sessions with FIXED session management."""

    _instance = None

    def __init__(self) -> None:
        db_config = DatabaseConfig()
        self.engine = create_engine(db_config.normalized_url, echo=False)
        
        # CRITICAL FIX: Set expire_on_commit=False to prevent DetachedInstanceError
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine,
            expire_on_commit=False  # <<<< THIS IS THE KEY FIX
        )

    @classmethod
    def get_instance(cls) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @contextmanager
    def get_session(self):
        """Provide a transactional session scope."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

