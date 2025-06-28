#!/usr/bin/env python3
"""
Simple launcher for the OfflineManager application.
This fixes the relative import issues in the original app.py.
"""

import sys
import os
import logging
import tkinter as tk
from tkinter import messagebox

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def launch_application():
    """Launch the OfflineManager application with fixed imports."""
    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Import all necessary components with absolute imports
        from automotive_invoice_manager.backend.database.models import init_database
        from automotive_invoice_manager.backend.database.connection import DatabaseManager
        from automotive_invoice_manager.services import AuthManager, CustomerService, InvoiceService
        from automotive_invoice_manager.ui.theme import COLORS, setup_styles
        
        # Initialize database
        print("Initializing database...")
        init_database()
        
        # Initialize services
        print("Initializing services...")
        auth_service = AuthManager()
        customer_service = CustomerService()
        invoice_service = InvoiceService()
        
        # Create main window
        print("Creating main window...")
        root = tk.Tk()
        root.title("OfflineManager - Invoice Manager")
        root.geometry("1200x800")
        
        # Setup UI theme
        setup_styles()
        
        # Create a simple welcome screen for now
        # You can replace this with the full login interface later
        welcome_frame = tk.Frame(root, bg=COLORS.get("background", "#f0f0f0"))
        welcome_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(
            welcome_frame,
            text="OfflineManager Invoice System",
            font=("Arial", 24, "bold"),
            bg=COLORS.get("background", "#f0f0f0"),
            fg=COLORS.get("primary", "#333333")
        )
        title_label.pack(pady=50)
        
        status_label = tk.Label(
            welcome_frame,
            text="Application started successfully!\nServices initialized and ready.",
            font=("Arial", 14),
            bg=COLORS.get("background", "#f0f0f0"),
            fg=COLORS.get("text", "#333333")
        )
        status_label.pack(pady=20)
        
        # Add close button
        close_button = tk.Button(
            welcome_frame,
            text="Close",
            font=("Arial", 12),
            command=root.quit,
            bg=COLORS.get("primary", "#007acc"),
            fg="white",
            padx=20,
            pady=10
        )
        close_button.pack(pady=20)
        
        print("Application ready! Starting main loop...")
        
        # Start the application
        root.mainloop()
        
    except ImportError as e:
        error_msg = f"Import error: {e}\n\nPlease ensure all dependencies are installed:\npip install -r requirements.txt"
        print(error_msg)
        messagebox.showerror("Import Error", error_msg)
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Failed to start application: {e}"
        print(error_msg)
        logging.error(f"Application startup error: {e}")
        messagebox.showerror("Startup Error", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    launch_application()