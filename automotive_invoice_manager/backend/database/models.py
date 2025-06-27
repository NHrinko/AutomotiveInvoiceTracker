# database/models.py - Database Models (adapted from Flask app)
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Date,
    Numeric,
    Boolean,
    ForeignKey,
    JSON,
    text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from decimal import Decimal
from contextlib import contextmanager
import logging

from .connection import DatabaseManager

Base = declarative_base()

# Singleton database manager
_db_manager = DatabaseManager.get_instance()
engine = _db_manager.engine
SessionLocal = _db_manager.SessionLocal


def check_connection() -> bool:
    """Verify database connectivity before using services."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return False


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customers = relationship(
        "Customer", back_populates="user", cascade="all, delete-orphan"
    )
    invoices = relationship(
        "Invoice", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=16
        )

    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class Customer(Base):
    """Customer model."""

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(100), index=True)
    phone = Column(String(20))
    address = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="customers")
    invoices = relationship(
        "Invoice", back_populates="customer", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Customer {self.name}>"


class Invoice(Base):
    """Invoice model."""

    __tablename__ = "invoices"
    __table_args__ = (UniqueConstraint("invoice_number"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    customer_id = Column(
        Integer, ForeignKey("customers.id"), nullable=False, index=True
    )
    invoice_number = Column(String(50), nullable=False, index=True)
    issued_date = Column(Date, default=date.today, nullable=False)
    due_date = Column(Date, nullable=False)
    line_items = Column(JSON, default=list)
    total = Column(Numeric(12, 2), default=0, nullable=False)
    template = Column(String(50), default="standard")
    status = Column(String(20), default="draft", nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")

    def calculate_total(self):
        """Calculate total from line items."""
        total = Decimal("0")
        for item in self.line_items or []:
            try:
                hours = Decimal(str(item.get("hours", item.get("quantity", 0))))
                rate = Decimal(str(item.get("rate", 0)))
                parts = Decimal(str(item.get("parts", 0)))
                tax = Decimal(str(item.get("tax", 0)))
                line = (hours * rate + parts) * (Decimal("1") + tax / Decimal("100"))
                total += line
            except (ValueError, TypeError, ArithmeticError):
                continue
        return total

    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"


# Database initialization functions
def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def init_database():
    """Initialize database with tables."""
    try:
        create_tables()
        logging.info("Database initialized successfully")
        return True
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        return False


def get_db_session():
    """Get database session."""
    return _db_manager.SessionLocal()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    with _db_manager.get_session() as session:
        yield session


