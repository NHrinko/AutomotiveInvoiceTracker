import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from automotive_invoice_manager.config.settings import Settings

# Use a temporary path for the database during tests
_TEST_DB = os.path.join(tempfile.gettempdir(), f"test_{Settings().default_db_path}")
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"

@pytest.fixture(scope="session", autouse=True)
def test_database_url(monkeypatch):
    """Ensure tests use an isolated database."""
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{_TEST_DB}")
    yield f"sqlite:///{_TEST_DB}"
