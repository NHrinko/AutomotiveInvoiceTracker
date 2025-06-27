from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Settings:
    """Application level settings."""
    default_db_path: str = "invoice_manager.db"
    colors: Dict[str, str] = field(default_factory=lambda: {
        # Core application palette
        'primary': '#1E3A5F',        # ACCENT_PRIMARY
        'secondary': '#4F6D8A',      # ACCENT_SECONDARY
        # Light gray background for main window
        'background': '#F7F9FC',     # BG_WINDOW
        'section_bg': '#FFFFFF',     # BG_SECTION
        # Medium gray for borders and highlights
        'highlight': '#6C757D',      # ACCENT_HIGHLIGHT
        'border': '#6C757D',         # ACCENT_BORDER
        # Dark gray text for readability
        'text': '#212529',           # TEXT_PRIMARY
        'text_purple': '#1E3A5F',    # TEXT_PRIMARY_ALT

        # Existing semantic colors
        'success': '#28a745',
        'danger': '#dc3545',
        'warning': '#ffc107',
        'info': '#17a2b8',
    })
