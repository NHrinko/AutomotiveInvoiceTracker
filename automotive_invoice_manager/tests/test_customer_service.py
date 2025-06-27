import os
import sys
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from automotive_invoice_manager.database import models
from automotive_invoice_manager.services.customer_service import CustomerService

models.create_tables()
service = CustomerService(models.session_scope)

with models.session_scope() as session:
    user = models.User(email='cust@test.com')
    user.set_password('pw')
    session.add(user)
    session.flush()


def test_create_and_get_customer():
    cust = service.create_customer({'name': 'Acme', 'email': 'a@ex.com'}, user.id)
    assert cust.id is not None
    fetched = service.get_customer(cust.id)
    assert fetched.name == 'Acme'


def test_update_customer():
    cust = service.create_customer({'name': 'Old'}, user.id)
    ok = service.update_customer(cust.id, {'name': 'New'}, user.id)
    assert ok
    updated = service.get_customer(cust.id)
    assert updated.name == 'New'


def test_delete_customer_blocked_when_invoices_exist():
    cust = service.create_customer({'name': 'HasInv'}, user.id)
    inv = models.Invoice(
        user_id=user.id,
        customer_id=cust.id,
        invoice_number='C1',
        issued_date=date.today(),
        due_date=date.today(),
        line_items=[],
    )
    with models.session_scope() as session:
        session.add(inv)
    assert not service.delete_customer(cust.id, user.id)
    with models.session_scope() as session:
        session.delete(inv)
    assert service.delete_customer(cust.id, user.id)


def test_get_customer_stats():
    cust = service.create_customer({'name': 'Stats'}, user.id)
    inv = models.Invoice(
        user_id=user.id,
        customer_id=cust.id,
        invoice_number='S1',
        issued_date=date.today(),
        due_date=date.today(),
        line_items=[{'description': 'x', 'hours': 2, 'rate': 5, 'parts': 0, 'tax': 0}],
        status='paid',
    )
    with models.session_scope() as session:
        session.add(inv)
    stats = service.get_customer_stats(cust.id)
    assert stats['invoice_count'] == 1
    assert stats['total_billed'] == 10.0
