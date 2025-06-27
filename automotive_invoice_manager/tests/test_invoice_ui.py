import os
import sys
import unittest
import tkinter as tk
from tkinter import ttk, messagebox
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "stubs"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


sys.modules.setdefault("tkcalendar", MagicMock(DateEntry=object))

from automotive_invoice_manager.ui.components.invoice_widgets import (
    InvoiceDetailWindow,
    InvoiceListFrame,
)


class TestInvoiceDetailWindow(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.invoice_service = MagicMock()
        self.invoice = MagicMock()
        self.invoice.invoice_number = "INV-001"
        self.invoice.issued_date = "2024-01-01"
        self.invoice.due_date = "2024-01-15"
        self.invoice.status = "sent"
        self.invoice.total = 150.0
        self.invoice.customer = MagicMock()
        self.invoice.customer.name = "Test Customer"
        self.invoice.line_items = [
            {"description": "Item", "hours": 1, "rate": 150.0, "parts": 0, "tax": 0}
        ]
        self.invoice_service.get_invoice.return_value = self.invoice

    def tearDown(self):
        self.root.destroy()

    def test_fields_render_read_only_and_match(self):
        window = InvoiceDetailWindow(self.root, self.invoice_service, 1)
        texts = [
            child.cget("text")
            for child in window.winfo_children()
            if isinstance(child, ttk.Label)
        ]
        self.assertIn(self.invoice.invoice_number, texts)
        self.assertIn(self.invoice.customer.name, texts)
        self.assertIn(str(self.invoice.issued_date), texts)
        self.assertIn(str(self.invoice.due_date), texts)
        self.assertIn(self.invoice.status, texts)
        self.assertIn(str(self.invoice.total), texts)
        entries = [c for c in window.winfo_children() if isinstance(c, tk.Entry)]
        self.assertEqual(len(entries), 0)
        window.destroy()

    def test_edit_button_opens_form(self):
        self.root.open_invoice_form = MagicMock()
        window = InvoiceDetailWindow(self.root, self.invoice_service, 1)
        window.on_edit()
        self.root.open_invoice_form.assert_called_once_with(self.invoice)

    def test_delete_button_confirms_and_calls_service(self):
        self.root.event_generate = MagicMock()
        with patch.object(messagebox, "askyesno", return_value=True) as mock_confirm:
            window = InvoiceDetailWindow(self.root, self.invoice_service, 1)
            window.on_delete()
        mock_confirm.assert_called_once()
        self.invoice_service.delete_invoice.assert_called_once_with(1)
        self.root.event_generate.assert_called_once_with("<<InvoiceDeleted>>")


class TestInvoiceListFrame(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.invoice_service = MagicMock()
        self.invoice_service.get_invoices.return_value = ([], 1)
        self.frame = InvoiceListFrame(self.root, self.invoice_service)
        self.frame.handle_open_detail = MagicMock()

    def tearDown(self):
        self.root.destroy()

    def test_double_click_opens_detail_with_correct_id(self):
        item = self.frame.tree.insert(
            "", tk.END, values=("INV-001", "Cust", "2024-01-01", "sent", "150.00")
        )
        self.frame.tree.selection_set(item)
        self.frame.on_double_click(None)
        self.frame.handle_open_detail.assert_called_once_with("INV-001")

    def test_search_filters_results_case_insensitive(self):
        alpha = MagicMock(
            invoice_number="INV-001",
            customer=MagicMock(name="Alpha Corp"),
            issued_date="2024-01-01",
            status="draft",
            total=100.0,
        )
        beta = MagicMock(
            invoice_number="INV-002",
            customer=MagicMock(name="Beta LLC"),
            issued_date="2024-01-02",
            status="sent",
            total=200.0,
        )

        def side_effect(page=1, per_page=10, search=None, status=None):
            if search and search.lower() == "inv-00":
                return [alpha, beta], 1
            if search and search.lower() == "alpha":
                return [alpha], 1
            return [], 1

        self.invoice_service.get_invoices.side_effect = side_effect

        self.frame.search_var.set("inv-00")
        self.frame.on_filter()
        self.assertEqual(len(self.frame.tree.get_children()), 2)

        self.frame.search_var.set("ALPHA")
        self.frame.on_filter()
        children = self.frame.tree.get_children()
        self.assertEqual(len(children), 1)
        values = self.frame.tree.item(children[0], "values")
        self.assertEqual(values[1], "Alpha Corp")

    def test_status_combobox_filters(self):
        draft = MagicMock(
            invoice_number="INV-001",
            customer=MagicMock(name="C1"),
            issued_date="2024-01-01",
            status="draft",
            total=50.0,
        )
        sent = MagicMock(
            invoice_number="INV-002",
            customer=MagicMock(name="C2"),
            issued_date="2024-01-02",
            status="sent",
            total=60.0,
        )
        paid = MagicMock(
            invoice_number="INV-003",
            customer=MagicMock(name="C3"),
            issued_date="2024-01-03",
            status="paid",
            total=70.0,
        )

        def side_effect(page=1, per_page=10, search=None, status=None):
            if status == "draft":
                return [draft], 1
            if status == "sent":
                return [sent], 1
            if status == "paid":
                return [paid], 1
            return [draft, sent, paid], 1

        self.invoice_service.get_invoices.side_effect = side_effect

        self.frame.status_var.set("All")
        self.frame.on_filter()
        self.assertEqual(len(self.frame.tree.get_children()), 3)

        for label, expected in [("Draft", "draft"), ("Sent", "sent"), ("Paid", "paid")]:
            self.frame.status_var.set(label)
            self.frame.on_filter()
            children = self.frame.tree.get_children()
            self.assertEqual(len(children), 1)
            values = self.frame.tree.item(children[0], "values")
            self.assertEqual(values[3], expected)

    def test_pagination_buttons_and_label(self):
        first = MagicMock(
            invoice_number="INV-001",
            customer=MagicMock(name="Alpha"),
            issued_date="2024-01-01",
            status="draft",
            total=10.0,
        )
        second = MagicMock(
            invoice_number="INV-002",
            customer=MagicMock(name="Beta"),
            issued_date="2024-01-02",
            status="sent",
            total=20.0,
        )

        def side_effect(page=1, per_page=10, search=None, status=None):
            if page == 1:
                return [first], 2
            return [second], 2

        self.invoice_service.get_invoices.side_effect = side_effect

        self.frame.load_data()
        self.assertEqual(self.frame.page_label.cget("text"), "Page 1 of 2")
        self.assertEqual(self.frame.prev_btn["state"], tk.DISABLED)
        self.assertEqual(self.frame.next_btn["state"], tk.NORMAL)

        self.frame.on_next()
        self.assertEqual(self.frame.page_label.cget("text"), "Page 2 of 2")
        self.assertEqual(self.frame.prev_btn["state"], tk.NORMAL)
        self.assertEqual(self.frame.next_btn["state"], tk.DISABLED)
