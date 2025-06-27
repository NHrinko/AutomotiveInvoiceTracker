# COMPLETE UPDATED CustomerService
# Replace your entire automotive_invoice_manager/services/customer_service.py with this:

import logging
from datetime import datetime
from automotive_invoice_manager.backend.database.models import Customer, Invoice
from automotive_invoice_manager.backend.database.connection import DatabaseManager
from sqlalchemy import or_, func, desc
from .base_service import BaseService


class CustomerService(BaseService):
    """Service for managing customers with all required methods."""

    def __init__(
        self, session_factory=DatabaseManager.get_instance().get_session
    ) -> None:
        """Initialize service with session factory."""
        super().__init__()
        self.session_factory = session_factory

    def get_all_customers(self, user_id, search: str | None = None):
        """Return all customers for a user with optional search."""
        try:
            with self.session_factory() as session:
                query = session.query(Customer).filter_by(user_id=user_id)
                if search:
                    pattern = f"%{search}%"
                    query = query.filter(
                        or_(
                            Customer.name.ilike(pattern),
                            Customer.email.ilike(pattern),
                            Customer.phone.ilike(pattern),
                            Customer.notes.ilike(pattern),
                        )
                    )
                return query.order_by(Customer.name).all()
        except Exception as e:
            logging.error(f"Error fetching customers: {e}")
            return []

    def create_customer(self, customer_data, user_id):
        """Create a new customer."""
        try:
            with self.session_factory() as session:
                customer = Customer(
                    user_id=user_id,
                    name=customer_data["name"],
                    email=customer_data.get("email"),
                    phone=customer_data.get("phone"),
                    address=customer_data.get("address"),
                    notes=customer_data.get("notes"),
                    created_at=datetime.utcnow(),
                )

                session.add(customer)
                session.flush()  # Ensure ID is available
                session.refresh(customer)  # Refresh to get all data

                logging.info(f"Customer created: {customer.name} (ID: {customer.id})")
                return customer

        except Exception as e:
            logging.error(f"Error creating customer: {e}")
            raise

    def get_customer(self, customer_id):
        """Get customer by ID."""
        try:
            with self.session_factory() as session:
                return session.query(Customer).filter_by(id=customer_id).first()
        except Exception as e:
            logging.error(f"Error getting customer {customer_id}: {e}")
            return None

    def update_customer(self, customer_id, customer_data, user_id):
        """Update existing customer."""
        try:
            with self.session_factory() as session:
                customer = (
                    session.query(Customer)
                    .filter_by(id=customer_id, user_id=user_id)
                    .first()
                )

                if not customer:
                    return False

                # Update fields
                customer.name = customer_data["name"]
                customer.email = customer_data.get("email")
                customer.phone = customer_data.get("phone")
                customer.address = customer_data.get("address")
                customer.notes = customer_data.get("notes")
                customer.updated_at = datetime.utcnow()

                logging.info(f"Customer updated: {customer.name} (ID: {customer.id})")
                return True

        except Exception as e:
            logging.error(f"Error updating customer {customer_id}: {e}")
            raise

    def delete_customer(self, customer_id, user_id):
        """Delete customer if no invoices exist."""
        try:
            with self.session_factory() as session:
                customer = (
                    session.query(Customer)
                    .filter_by(id=customer_id, user_id=user_id)
                    .first()
                )

                if not customer:
                    return False

                invoice_count = (
                    session.query(Invoice).filter_by(customer_id=customer_id).count()
                )
                if invoice_count > 0:
                    return False

                session.delete(customer)

                logging.info(f"Customer deleted: {customer.name} (ID: {customer.id})")
                return True

        except Exception as e:
            logging.error(f"Error deleting customer {customer_id}: {e}")
            raise

    def search_customers(self, user_id, search_term="", sort_by="name", sort_desc=False):
        """Search customers with optional filtering and sorting."""
        try:
            with self.session_factory() as session:
                query = session.query(Customer).filter_by(user_id=user_id)
                if search_term:
                    search_pattern = f"%{search_term}%"
                    query = query.filter(
                        or_(
                            Customer.name.ilike(search_pattern),
                            Customer.email.ilike(search_pattern),
                            Customer.phone.ilike(search_pattern),
                            Customer.notes.ilike(search_pattern),
                        )
                    )

                sort_column = getattr(Customer, sort_by, Customer.name)
                if sort_desc:
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(sort_column)

                return query.all()

        except Exception as e:
            logging.error(f"Error searching customers: {e}")
            return []

    def get_customer_count(self, user_id):
        """Get total number of customers for user."""
        try:
            with self.session_factory() as session:
                return session.query(Customer).filter_by(user_id=user_id).count()
        except Exception as e:
            logging.error(f"Error getting customer count: {e}")
            return 0

    def get_customer_stats(self, customer_id):
        """Get customer statistics (invoice count, total billed)."""
        try:
            with self.session_factory() as session:
                stats = (
                    session.query(
                        func.count(Invoice.id).label("invoice_count"),
                        func.coalesce(func.sum(Invoice.total), 0).label("total_billed"),
                    )
                    .filter_by(customer_id=customer_id)
                    .first()
                )

                return {
                    "invoice_count": stats.invoice_count or 0,
                    "total_billed": float(stats.total_billed or 0),
                }

        except Exception as e:
            logging.error(f"Error getting customer stats for {customer_id}: {e}")
            return {"invoice_count": 0, "total_billed": 0.0}

    # Async wrapper methods (if needed by other parts of your app)
    def get_all_customers_async(self, user_id, search: str | None = None):
        """Asynchronously fetch customers."""
        return self.run_async(self.get_all_customers, user_id, search)

    def create_customer_async(self, customer_data, user_id):
        """Asynchronously create a customer."""
        return self.run_async(self.create_customer, customer_data, user_id)

    def get_customer_async(self, customer_id):
        """Asynchronously get a customer."""
        return self.run_async(self.get_customer, customer_id)

    def update_customer_async(self, customer_id, customer_data, user_id):
        """Asynchronously update a customer."""
        return self.run_async(self.update_customer, customer_id, customer_data, user_id)

    def delete_customer_async(self, customer_id, user_id):
        """Asynchronously delete a customer."""
        return self.run_async(self.delete_customer, customer_id, user_id)

    def search_customers_async(self, user_id, search_term="", sort_by="name", sort_desc=False):
        """Asynchronously search customers."""
        return self.run_async(self.search_customers, user_id, search_term, sort_by, sort_desc)

    def get_customer_count_async(self, user_id):
        """Asynchronously get customer count."""
        return self.run_async(self.get_customer_count, user_id)

    def get_customer_stats_async(self, customer_id):
        """Asynchronously retrieve customer statistics."""
        return self.run_async(self.get_customer_stats, customer_id)