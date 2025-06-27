import os
import sys
from datetime import date, timedelta
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from automotive_invoice_manager.database import models
from automotive_invoice_manager.services.invoice_service import InvoiceService

models.create_tables()
service = InvoiceService(models.session_scope)

with models.session_scope() as session:
    user = models.User(email='svc@test.com')
    user.set_password('pw')
    session.add(user)
    session.flush()
    cust = models.Customer(user_id=user.id, name='Cust', email='c@ex.com')
    session.add(cust)


def test_create_invoice_generates_number_and_total():
    data = {
        'customer': cust.name,
        'issued_date': date.today(),
        'due_date': date.today(),
        'line_items': [{'description': 'a', 'hours': 2, 'rate': 5, 'parts': 0, 'tax': 0}],
    }
    inv = service.create_invoice(user, data)
    assert inv.invoice_number
    assert inv.total == 10


def test_duplicate_invoice_number_raises():
    data = {
        'invoice_number': 'DUP',
        'customer': cust.name,
        'issued_date': date.today(),
        'due_date': date.today(),
    }
    service.create_invoice(user, data)
    with pytest.raises(ValueError):
        service.create_invoice(user, data)


def test_due_date_validation_on_create():
    with pytest.raises(ValueError):
        service.create_invoice(
            user,
            {
                'customer': cust.name,
                'issued_date': date.today(),
                'due_date': date.today() - timedelta(days=1),
            },
        )


def test_due_date_validation_on_update():
    inv = service.create_invoice(
        user,
        {
            'customer': cust.name,
            'issued_date': date.today(),
            'due_date': date.today(),
        },
    )
    with pytest.raises(ValueError):
        service.update_invoice(inv.id, {'due_date': date.today() - timedelta(days=1)})
