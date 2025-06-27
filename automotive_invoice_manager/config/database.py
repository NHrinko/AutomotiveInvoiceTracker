from dataclasses import dataclass
import os

@dataclass
class DatabaseConfig:
    """Database configuration options."""
    url: str = os.environ.get("DATABASE_URL", "sqlite:///invoices.db")

    @property
    def normalized_url(self) -> str:
        if self.url.startswith("postgres://"):
            return self.url.replace("postgres://", "postgresql://", 1)
        return self.url
