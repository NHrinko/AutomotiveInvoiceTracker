import os
import sys
from datetime import date
import importlib

# Ensure project root is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Configure path to project

from automotive_invoice_manager.database import models

importlib.reload(models)
models.create_tables()

from automotive_invoice_manager.services.invoice_service import InvoiceService

service = InvoiceService(models.session_scope)

# Create test user and related objects
with models.session_scope() as session:
    user = models.User(email="user@example.com")
    user.set_password("password")
    session.add(user)
    session.flush()

customer_a = models.Customer(user_id=user.id, name="Alpha Corp", email="a@example.com")
customer_b = models.Customer(user_id=user.id, name="Beta LLC", email="b@example.com")
with models.session_scope() as session:
    session.add_all([customer_a, customer_b])

invoices = [
    models.Invoice(
        user_id=user.id,
        customer_id=customer_a.id,
        invoice_number="INV-001",
        issued_date=date.today(),
        due_date=date.today(),
        line_items=[],
        total=100,
        status="draft",
    ),
    models.Invoice(
        user_id=user.id,
        customer_id=customer_b.id,
        invoice_number="INV-002",
        issued_date=date.today(),
        due_date=date.today(),
        line_items=[],
        total=200,
        status="sent",
    ),
    models.Invoice(
        user_id=user.id,
        customer_id=customer_b.id,
        invoice_number="INV-003",
        issued_date=date.today(),
        due_date=date.today(),
        line_items=[],
        total=300,
        status="paid",
    ),
]
with models.session_scope() as session:
    session.add_all(invoices)


def test_search_filters_case_insensitive():
    items, _ = service.get_invoices(user.id, search="inv-00")
    assert len(items) == 3
    items, _ = service.get_invoices(user.id, search="alpha")
    assert len(items) == 1
    assert items[0].customer.name == "Alpha Corp"
    items, _ = service.get_invoices(user.id, search="ALPHA")
    assert len(items) == 1
    assert items[0].customer.name == "Alpha Corp"


def test_status_combobox_options():
    statuses = ["draft", "sent", "paid"]
    for status in statuses:
        items, _ = service.get_invoices(user.id, status=status)
        assert all(inv.status == status for inv in items)

    # Selecting 'All' should return all invoices (status=None)
    items, _ = service.get_invoices(user.id, status=None)
    assert len(items) == 3


def test_pagination_boundaries():
    items, total_pages = service.get_invoices(user.id, page=1, per_page=2)
    assert len(items) == 2
    assert total_pages == 2

    items, _ = service.get_invoices(user.id, page=2, per_page=2)
    assert len(items) == 1


class DummyVar:
    def __init__(self):
        self._value = ""

    def get(self):
        return self._value

    def set(self, value):
        self._value = value


class DummyButton:
    def __init__(self):
        self.state = "normal"

    def config(self, state=None):
        if state is not None:
            self.state = state


class DummyLabel:
    def __init__(self):
        self.text = ""

    def config(self, text=None):
        if text is not None:
            self.text = text


class DummyTree:
    def __init__(self):
        self.rows = []

    def delete(self, *items):
        self.rows.clear()

    def insert(self, parent, index, values):
        self.rows.append(values)

    def get_children(self):
        return list(range(len(self.rows)))

    def item(self, item, option=None):
        return {"values": self.rows[item]}


class FakeInvoiceListFrame:
    def __init__(self, invoice_service):
        self.invoice_service = invoice_service
        self.current_page = 1
        self.per_page = 2
        self.search_var = DummyVar()
        self.status_var = DummyVar()
        self.tree = DummyTree()
        self.prev_btn = DummyButton()
        self.next_btn = DummyButton()
        self.page_label = DummyLabel()

    def load_data(self):
        search = self.search_var.get()
        status = (
            self.status_var.get().lower()
            if self.status_var.get() and self.status_var.get() != "All"
            else None
        )
        items, total_pages = self.invoice_service.get_invoices(
            user.id,
            page=self.current_page,
            per_page=self.per_page,
            search=search,
            status=status,
        )
        self.tree.delete(*self.tree.get_children())
        for inv in items:
            self.tree.insert(
                "",
                "end",
                values=(
                    inv.invoice_number,
                    inv.customer.name,
                    inv.issued_date,
                    inv.status,
                    f"{inv.total:.2f}",
                ),
            )
        self.total_pages = total_pages
        self.page_label.config(text=f"Page {self.current_page} of {self.total_pages}")
        self.prev_btn.config(state=("normal" if self.current_page > 1 else "disabled"))
        self.next_btn.config(
            state=("normal" if self.current_page < self.total_pages else "disabled")
        )

    def on_filter(self):
        self.current_page = 1
        self.load_data()

    def on_prev(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def on_next(self):
        if self.current_page < getattr(self, "total_pages", 1):
            self.current_page += 1
            self.load_data()


def test_pagination_button_states_and_label():
    frame = FakeInvoiceListFrame(service)
    frame.load_data()
    assert frame.page_label.text == "Page 1 of 2"
    assert frame.prev_btn.state == "disabled"
    assert frame.next_btn.state == "normal"

    frame.on_next()
    assert frame.page_label.text == "Page 2 of 2"
    assert frame.prev_btn.state == "normal"
    assert frame.next_btn.state == "disabled"
