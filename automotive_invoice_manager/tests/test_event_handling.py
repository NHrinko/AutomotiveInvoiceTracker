import os
import sys
from datetime import date
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "stubs"))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from automotive_invoice_manager.ui.components import invoice_widgets


class FakeList:
    def __init__(self):
        self.load_data_called = False
        self._bindings = {}

    def bind(self, event, func):
        self._bindings[event] = func

    def event_generate(self, event):
        if event in self._bindings:
            self._bindings[event](None)

    def load_data(self):
        self.load_data_called = True


class EventErrorHandlingTests(unittest.TestCase):
    def _make_form_dialog(self, master, service, invoice=None, exception=None):
        dialog = invoice_widgets.InvoiceFormDialog.__new__(
            invoice_widgets.InvoiceFormDialog
        )
        dialog.master = master
        dialog.invoice_service = service
        dialog.invoice = invoice
        dialog.customer_cb = Mock(get=Mock(return_value="Cust"))
        today = date.today()
        dialog.issued_date = Mock(get_date=Mock(return_value=today))
        dialog.due_date = Mock(get_date=Mock(return_value=today))
        dialog.line_items = []
        dialog.destroy = Mock()
        if exception:
            if invoice:
                service.update_invoice.side_effect = exception
            else:
                service.create_invoice.side_effect = exception
        return dialog

    def _make_detail_window(self, master, service, exception=None):
        window = invoice_widgets.InvoiceDetailWindow.__new__(
            invoice_widgets.InvoiceDetailWindow
        )
        window.master = master
        window.invoice_service = service
        window.invoice_id = 1
        window.destroy = Mock()
        window.invoice = Mock(
            invoice_number="1",
            customer=Mock(name="C"),
            issued_date=date.today(),
            due_date=date.today(),
            status="draft",
            total=0,
            line_items=[],
        )
        if exception:
            service.delete_invoice.side_effect = exception
        return window

    def test_form_save_error_shows_message(self):
        master = FakeList()
        service = Mock()
        dialog = self._make_form_dialog(master, service, exception=Exception("fail"))
        with patch.object(invoice_widgets.messagebox, "showerror") as err:
            dialog.on_save()
            err.assert_called_with("Error", "fail")

    def test_generate_pdf_error_shows_message(self):
        master = FakeList()
        service = Mock()
        window = self._make_detail_window(master, service)
        service.generate_pdf.side_effect = Exception("pdf fail")
        with patch.object(
            invoice_widgets.filedialog,
            "asksaveasfilename",
            return_value="out.pdf",
        ), patch.object(invoice_widgets.messagebox, "showerror") as err:
            window.on_generate_pdf()
            err.assert_called_with("Error", "pdf fail")

    def test_delete_error_shows_message(self):
        master = FakeList()
        service = Mock()
        window = self._make_detail_window(
            master, service, exception=Exception("del fail")
        )
        with patch.object(
            invoice_widgets.messagebox, "askyesno", return_value=True
        ), patch.object(invoice_widgets.messagebox, "showerror") as err:
            window.on_delete()
            err.assert_called_with("Error", "del fail")

    def test_form_success_refreshes_list(self):
        master = FakeList()
        master.bind("<<InvoiceUpdated>>", lambda e: master.load_data())
        service = Mock()
        dialog = self._make_form_dialog(master, service)
        with patch.object(invoice_widgets.messagebox, "showerror"):
            dialog.on_save()
        self.assertTrue(master.load_data_called)

    def test_delete_success_refreshes_list(self):
        master = FakeList()
        master.bind("<<InvoiceDeleted>>", lambda e: master.load_data())
        service = Mock()
        window = self._make_detail_window(master, service)
        with patch.object(
            invoice_widgets.messagebox, "askyesno", return_value=True
        ), patch.object(invoice_widgets.messagebox, "showerror"):
            window.on_delete()
        self.assertTrue(master.load_data_called)


if __name__ == "__main__":
    unittest.main()
