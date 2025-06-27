import os
import sys
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stubs'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from automotive_invoice_manager.ui.components.invoice_widgets import InvoiceFormDialog

class FakeDateEntry:
    def __init__(self, *a, **kw):
        self._d = date.today()
    def get_date(self):
        return self._d
    def set_date(self, d):
        self._d = d


def create_dialog():
    with patch('automotive_invoice_manager.ui.components.invoice_widgets.DateEntry', FakeDateEntry):
        root = MagicMock()
        service = MagicMock()
        customers = [MagicMock(name='A'), MagicMock(name='B')]
        dialog = InvoiceFormDialog(root, service, customers)
        return dialog


def test_add_and_remove_line_items_update_total():
    d = create_dialog()
    d._add_line()
    desc, hours, rate, parts, tax = d.line_items[-1]
    hours.set(2)
    rate.set(5)
    d._recalculate_total()
    assert d.total_var.get() == '10.00'
    d._remove_line(desc.master)
    assert d.total_var.get() == '0.00'


def test_default_dates_and_customer_list():
    d = create_dialog()
    assert d.issued_date.get_date() == date.today()
    assert d.due_date.get_date() == date.today() + timedelta(days=30)
    names = [c.name for c in d.customer_list]
    assert names == ['A', 'B']
