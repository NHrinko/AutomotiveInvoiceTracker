# services/invoice_service.py - Invoice Service
import logging
from datetime import datetime, date
from automotive_invoice_manager.backend.database.models import Invoice, Customer
from automotive_invoice_manager.backend.database.connection import DatabaseManager
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from .base_service import BaseService


class InvoiceService:
    """Service for managing invoices."""

    def __init__(
        self, session_factory=DatabaseManager.get_instance().get_session
    ) -> None:
        self.session_factory = session_factory

    def get_recent_invoices(self, user_id, limit=10):
        """Get recent invoices for dashboard."""
        try:
            with self.session_factory() as session:
                return (
                    session.query(Invoice).options(joinedload(Invoice.customer))
                    .join(Customer)
                    .filter(Invoice.user_id == user_id)
                    .order_by(desc(Invoice.created_at))
                    .limit(limit)
                    .all()
                )

        except Exception as e:
            logging.error(f"Error getting recent invoices: {e}")
            return []

    def get_invoice_count(self, user_id):
        """Get total number of invoices for user."""
        try:
            with self.session_factory() as session:
                return session.query(Invoice).options(joinedload(Invoice.customer)).filter_by(user_id=user_id).count()
        except Exception as e:
            logging.error(f"Error getting invoice count: {e}")
            return 0

    def get_total_revenue(self, user_id):
        """Get total revenue from paid invoices."""
        try:
            with self.session_factory() as session:
                result = (
                    session.query(func.sum(Invoice.total))
                    .filter(Invoice.user_id == user_id, Invoice.status == "paid")
                    .scalar()
                )

                return float(result or 0)

        except Exception as e:
            logging.error(f"Error getting total revenue: {e}")
            return 0.0

    def get_overdue_count(self, user_id):
        """Get count of overdue invoices."""
        try:
            with self.session_factory() as session:
                return (
                    session.query(Invoice).options(joinedload(Invoice.customer))
                    .filter(
                        Invoice.user_id == user_id,
                        Invoice.due_date < date.today(),
                        Invoice.status.in_(["sent", "draft"]),
                    )
                    .count()
                )

        except Exception as e:
            logging.error(f"Error getting overdue count: {e}")
            return 0

    def get_pending_count(self, user_id):
        """Get count of invoices that are pending payment."""
        try:
            with self.session_factory() as session:
                return (
                    session.query(Invoice)
                    .filter(
                        Invoice.user_id == user_id,
                        Invoice.status.in_(["draft", "sent"]),
                        Invoice.due_date >= date.today(),
                    )
                    .count()
                )
        except Exception as e:
            logging.error(f"Error getting pending count: {e}")
            return 0

    def get_invoices(self, user_id, page=1, per_page=10, search=None, status=None):
        """Return paginated invoices with optional search and status filter."""
        try:
            with self.session_factory() as session:
                query = (
                    session.query(Invoice).options(joinedload(Invoice.customer))
                    .join(Customer)
                    .filter(Invoice.user_id == user_id)
                )
                if search:
                    pattern = f"%{search}%"
                    query = query.filter(
                        (Invoice.invoice_number.ilike(pattern))
                        | (Customer.name.ilike(pattern))
                    )
                if status:
                    query = query.filter(Invoice.status == status)

                total = query.count()
                total_pages = max(1, (total + per_page - 1) // per_page)
                invoices = (
                    query.order_by(desc(Invoice.created_at))
                    .offset((page - 1) * per_page)
                    .limit(per_page)
                    .all()
                )
                return invoices, total_pages
        except Exception as e:
            logging.error(f"Error fetching invoices: {e}")
            return [], 1

    def get_invoice(self, invoice_id):
        """Get invoice by ID."""
        try:
            with self.session_factory() as session:
                return session.query(Invoice).options(joinedload(Invoice.customer)).get(invoice_id)
        except Exception as e:
            logging.error(f"Error fetching invoice {invoice_id}: {e}")
            return None

    def get_invoice_by_number(self, user_id, invoice_number):
        """Get invoice for a user by invoice number."""
        try:
            with self.session_factory() as session:
                return (
                    session.query(Invoice).options(joinedload(Invoice.customer))
                    .filter_by(user_id=user_id, invoice_number=invoice_number)
                    .first()
                )
        except Exception as e:
            logging.error(
                f"Error fetching invoice {invoice_number} for user {user_id}: {e}"
            )
            return None

    def create_invoice(self, user, data):
        """Create a new invoice for a user."""
        try:
            with self.session_factory() as session:
                customer = (
                    session.query(Customer)
                    .filter_by(user_id=user.id, name=data["customer"])
                    .first()
                )
                if not customer:
                    raise ValueError("Customer not found")

                number = data.get("invoice_number") or str(int(datetime.utcnow().timestamp()))
                existing = session.query(Invoice).options(joinedload(Invoice.customer)).filter_by(invoice_number=number).first()
                if existing:
                    raise ValueError("Invoice number already exists")

                if data["due_date"] < data["issued_date"]:
                    raise ValueError("Due date cannot be before issued date")

                invoice = Invoice(
                    user_id=user.id,
                    customer_id=customer.id,
                    invoice_number=number,
                    issued_date=data["issued_date"],
                    due_date=data["due_date"],
                    line_items=data.get("line_items", []),
                    status=data.get("status", "draft"),
                    template=data.get("template", "standard"),
                )
                invoice.total = invoice.calculate_total()
                session.add(invoice)
                return invoice
        except Exception as e:
            logging.error(f"Error creating invoice: {e}")
            raise

    def update_invoice(self, invoice_id, data):
        """Update an existing invoice."""
        try:
            with self.session_factory() as session:
                invoice = session.query(Invoice).options(joinedload(Invoice.customer)).get(invoice_id)
                if not invoice:
                    return False
                if "customer" in data:
                    customer = (
                        session.query(Customer)
                        .filter_by(user_id=invoice.user_id, name=data["customer"])
                        .first()
                    )
                    if customer:
                        invoice.customer_id = customer.id
                invoice.issued_date = data.get("issued_date", invoice.issued_date)
                invoice.due_date = data.get("due_date", invoice.due_date)
                if invoice.due_date < invoice.issued_date:
                    raise ValueError("Due date cannot be before issued date")
                if "line_items" in data:
                    invoice.line_items = data["line_items"]
                    invoice.total = invoice.calculate_total()
                invoice.status = data.get("status", invoice.status)
                invoice.template = data.get("template", invoice.template)
                invoice.updated_at = datetime.utcnow()
                return True
        except Exception as e:
            logging.error(f"Error updating invoice {invoice_id}: {e}")
            raise

    def delete_invoice(self, invoice_id):
        """Delete invoice by ID."""
        try:
            with self.session_factory() as session:
                invoice = session.query(Invoice).options(joinedload(Invoice.customer)).get(invoice_id)
                if not invoice:
                    return False
                session.delete(invoice)
                return True
        except Exception as e:
            logging.error(f"Error deleting invoice {invoice_id}: {e}")
            raise

    def generate_pdf(self, invoice_id, output_path=None):
        """Generate PDF for invoice using ReportLab."""
        try:
            from .pdf_service import PDFService
            pdf_service = PDFService()  # Use default DatabaseManager
            return pdf_service.generate_invoice_pdf(invoice_id, output_path)
        except Exception as e:
            logging.error(f"Error generating PDF for invoice {invoice_id}: {e}")
            raise
