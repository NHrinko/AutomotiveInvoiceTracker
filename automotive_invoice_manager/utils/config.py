import os

class Config:
    """Minimal configuration for the desktop application."""

    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///invoices.db")
    WINDOW_SIZE = os.environ.get("WINDOW_SIZE", "1200x800")
    PDF_OUTPUT_DIR = os.environ.get("PDF_OUTPUT_DIR", "generated_pdfs")
