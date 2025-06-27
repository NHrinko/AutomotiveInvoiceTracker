"""Base service with shared database utilities."""

from automotive_invoice_manager.backend.database.connection import DatabaseManager

class BaseService:
    """Base class for all services using :class:`DatabaseManager` for DB access."""

    def __init__(self, db_manager: DatabaseManager | None = None) -> None:
        """Initialize the service with an injected :class:`DatabaseManager`.

        Parameters
        ----------
        db_manager : DatabaseManager, optional
            Custom database manager instance. If omitted the global
            :meth:`DatabaseManager.get_instance` is used.
        """
        self.db_manager = db_manager or DatabaseManager.get_instance()

    def session_scope(self):
        """Return the context manager for a database session."""
        return self.db_manager.get_session()
