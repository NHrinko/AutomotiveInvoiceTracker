import os
import sys

# Ensure project root is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from automotive_invoice_manager.database.models import Base, engine, session_scope
from automotive_invoice_manager.services.auth_service import AuthManager


def setup_module(module):
    Base.metadata.create_all(bind=engine)


def teardown_module(module):
    Base.metadata.drop_all(bind=engine)


def test_register_rejects_weak_password():
    auth = AuthManager(session_scope)
    user, error = auth.register("test@example.com", "short")
    assert user is None
    assert "Password" in error


def test_register_accepts_strong_password():
    auth = AuthManager(session_scope)
    user, error = auth.register("user2@example.com", "Valid123")
    assert error is None
    assert user.email == "user2@example.com"
