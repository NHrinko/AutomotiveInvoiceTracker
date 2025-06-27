import os
import sys
from datetime import date, timedelta
import unittest
from unittest.mock import patch

# Ensure project root is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from automotive_invoice_manager.database.models import Base, engine, session_scope, User, Customer, Invoice
from automotive_invoice_manager.services.invoice_service import InvoiceService


class InvoiceWorkflowTestCase(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.service = InvoiceService(session_scope)
        with session_scope() as session:
            self.user = User(email="workflow@test.com")
            self.user.set_password("password123")
            session.add(self.user)
            session.flush()

            self.customer = Customer(
                user_id=self.user.id, name="Test Customer", email="cust@example.com"
            )
            session.add(self.customer)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    def test_invoice_full_workflow(self):
        data = {
            "customer": self.customer.name,
            "issued_date": date.today(),
            "due_date": date.today() + timedelta(days=30),
            "line_items": [
                {"description": "Item", "hours": 2, "rate": 50, "parts": 0, "tax": 0}
            ],
        }

        # Create draft invoice
        invoice = self.service.create_invoice(self.user, data)
        self.assertEqual(invoice.status, "draft")

        # Mark as sent
        self.service.update_invoice(invoice.id, {"status": "sent"})
        invoice = self.service.get_invoice(invoice.id)
        self.assertEqual(invoice.status, "sent")

        # Mark as paid
        self.service.update_invoice(invoice.id, {"status": "paid"})
        invoice = self.service.get_invoice(invoice.id)
        self.assertEqual(invoice.status, "paid")

        # Mark as overdue
        self.service.update_invoice(invoice.id, {"status": "overdue"})
        invoice = self.service.get_invoice(invoice.id)
        self.assertEqual(invoice.status, "overdue")

        # Generate PDF
        with patch(
            "automotive_invoice_manager.services.invoice_service.pdf_generator.generate_pdf",
            return_value="/tmp/test.pdf",
        ) as mock_gen:
            pdf_path = self.service.generate_pdf(invoice.id)
            self.assertEqual(pdf_path, "/tmp/test.pdf")
            mock_gen.assert_called_once()

        # Delete invoice
        result = self.service.delete_invoice(invoice.id)
        self.assertTrue(result)
        self.assertIsNone(self.service.get_invoice(invoice.id))

    def test_force_close_rollback(self):
        data = {
            "customer": self.customer.name,
            "issued_date": date.today(),
            "due_date": date.today() + timedelta(days=30),
        }
        # Simulate crash during commit
        with patch("sqlalchemy.orm.session.Session.commit", side_effect=Exception("fail")):
            with self.assertRaises(Exception):
                self.service.create_invoice(self.user, data)
        with session_scope() as session:
            self.assertEqual(session.query(Invoice).count(), 0)


if __name__ == "__main__":
    unittest.main()
