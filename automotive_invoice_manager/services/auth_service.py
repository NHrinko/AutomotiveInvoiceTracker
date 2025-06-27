# services/auth_service.py - Authentication Service
import logging
from automotive_invoice_manager.backend.database.models import User
from automotive_invoice_manager.backend.database.connection import DatabaseManager
from .validators import validate_password
from .base_service import BaseService


class AuthService(BaseService):
    """Template authentication service using dependency injection."""

    def __init__(self, db_manager: DatabaseManager | None = None) -> None:
        """Initialize the service with a database manager instance.

        Example
        -------
        >>> db = DatabaseManager.get_instance()
        >>> service = AuthService(db)
        """
        super().__init__(db_manager)

    def login(self, email: str, password: str):
        """Authenticate a user by email and password."""
        pass

    def logout(self) -> None:
        """Clear any stored authentication state."""
        pass

    def register(self, email: str, password: str):
        """Create a new user account."""
        pass


class AuthManager:
    """Simple in-memory authentication manager."""

    def __init__(
        self, session_factory=DatabaseManager.get_instance().get_session
    ) -> None:
        self.current_user = None
        self.session_factory = session_factory

    def login(self, email, password):
        """Validate credentials and set current user."""
        try:
            with self.session_factory() as session:
                user = session.query(User).filter_by(email=email.lower().strip()).first()
                if user and user.check_password(password):
                    self.current_user = user
                    logging.info(f"User logged in: {email}")
                    return user
                logging.warning(f"Failed login attempt for: {email}")
                return None
        except Exception as e:
            logging.error(f"Login error: {e}")
            return None

    def logout(self):
        """Logout current user."""
        if self.current_user:
            logging.info(f"User logged out: {self.current_user.email}")
        self.current_user = None

    def register(self, email, password):
        """Register new user."""
        valid, message = validate_password(password)
        if not valid:
            return None, message
        try:
            with self.session_factory() as session:
                existing_user = session.query(User).filter_by(email=email.lower().strip()).first()
                if existing_user:
                    return None, "Email already registered"

                user = User(email=email.lower().strip())
                user.set_password(password)

                session.add(user)

                logging.info(f"New user registered: {email}")
                return user, None

        except Exception as e:
            logging.error(f"Registration error: {e}")
            return None, str(e)

    def is_authenticated(self):
        """Check if user is authenticated."""
        return self.current_user is not None


# Backwards compatibility - old name used in some modules
AuthService = AuthManager
