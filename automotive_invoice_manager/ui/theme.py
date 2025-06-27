import tkinter as tk
from tkinter import ttk

# Centralized color scheme for the desktop UI
COLORS = {
    "primary": "#8B4513",       # Saddle brown
    "secondary": "#CD853F",     # Peru  
    "background": "#FDF5E6",    # Old lace
    "section": "#FFFFFF",       # White
    "highlight": "#D2691E",     # Chocolate
    "border": "#DEB887",        # Burlywood
    "text": "#654321",          # Dark brown
    "text_purple": "#8B4513",   # Brown accent
    # Additional colors used across the application
    "muted": "#666666",
    "action_blue": "#3498db",
    "action_green": "#27ae60",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "brand_purple": "#4B0082",
    "light_bg": "#ecf0f1",
    "muted_text": "#7f8c8d",
    "footer_bg": "#34495e",
    "footer_text": "#bdc3c7",
    "disabled_bg": "#95a5a6",
    "dark_gray": "#404040",
}

# Font sizes used across the application
FONTS = {
    "xl": ("Arial", 18, "bold"),
    "lg": ("Arial", 16, "bold"),
    "base": ("Arial", 11),
    "sm": ("Arial", 9),
}


def setup_styles(style: ttk.Style | None = None) -> ttk.Style:
    """Configure ttk styles using the application color scheme - ENHANCED VERSION."""
    style = style or ttk.Style()

    # Primary button style
    style.configure(
        "Primary.TButton",
        background=COLORS["primary"],
        foreground="white",
        focuscolor="none",
        borderwidth=0,
        padding=(10, 5),
    )
    style.map("Primary.TButton", background=[("active", "#27486a")])

    # Secondary button style  
    style.configure(
        "Secondary.TButton",
        background=COLORS["secondary"],
        foreground="white",  # Changed from black to white
        focuscolor="none",
        borderwidth=0,
        padding=(10, 5),
    )
    style.map("Secondary.TButton", background=[("active", "#5a7ba0")])

    # Frame styles
    style.configure(
        "Card.TFrame", 
        background=COLORS["section"], 
        relief="solid", 
        borderwidth=1
    )

    # Label styles
    style.configure(
        "Heading.TLabel",
        font=FONTS["xl"],
        background=COLORS["section"],
        foreground=COLORS["text"],
    )

    style.configure(
        "Subheading.TLabel",
        font=FONTS["lg"],
        background=COLORS["section"],
        foreground=COLORS["text"],
    )

    style.configure(
        "Form.TLabel",
        font=FONTS["base"],
        background=COLORS["section"],
        foreground=COLORS["text"],
    )

    style.configure("Form.TEntry", font=FONTS["base"])

    # NOTEBOOK STYLES - This is the main fix
    style.configure(
        'TNotebook', 
        background=COLORS['background'],
        borderwidth=0,
        tabmargins=[2, 5, 2, 0]
    )
    
    style.configure(
        'TNotebook.Tab',
        padding=[20, 12, 20, 12],
        background=COLORS['secondary'],
        foreground='white',
        font=FONTS['base'],
        borderwidth=1,
        focuscolor='none'
    )
    
    style.map(
        'TNotebook.Tab',
        background=[
            ('selected', COLORS['primary']),
            ('active', COLORS['highlight']),
            ('!active', COLORS['secondary'])
        ],
        foreground=[
            ('selected', 'white'),
            ('active', 'white'),
            ('!active', 'white')
        ],
        expand=[('selected', [1, 1, 1, 0])]
    )

    return style