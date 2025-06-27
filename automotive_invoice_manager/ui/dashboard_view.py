# automotive_invoice_manager/ui/dashboard_view.py - IMPROVED WITH BETTER ERROR HANDLING

import tkinter as tk
from tkinter import messagebox
import logging
from .theme import COLORS, FONTS
from .tooltips import add_tooltip

logger = logging.getLogger(__name__)


class DashboardView(tk.Frame):
    """Dashboard tab displaying statistics and quick actions."""

    def __init__(self, parent, main_interface):
        super().__init__(parent, bg=COLORS["background"])
        self.main_interface = main_interface
        self.customer_service = main_interface.customer_service
        self.invoice_service = main_interface.invoice_service
        self.user = main_interface.user

        # Initialize stats tracking
        self.stats_loaded = False
        self.last_error = None

        try:
            self.setup_ui()
            logger.info("DashboardView initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing DashboardView: {e}")
            self.create_error_ui(str(e))

    def setup_ui(self) -> None:
        """Initialize dashboard widgets with error handling."""
        try:
            header_label = tk.Label(
                self,
                text="Dashboard",
                font=FONTS["lg"],
                fg=COLORS["text"],
                bg=COLORS["background"],
            )
            header_label.pack(anchor=tk.W, padx=20, pady=(20, 20))

            # Create stats frame first
            self.stats_frame = tk.Frame(self, bg=COLORS["background"])
            self.stats_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

            # Load and display stats
            self.load_dashboard_stats()

            # Quick actions section
            actions_frame = tk.LabelFrame(
                self,
                text="Quick Actions",
                font=FONTS["base"],
                bg=COLORS["background"],
            )
            actions_frame.pack(fill=tk.X, padx=20, pady=10)

            actions_grid = tk.Frame(actions_frame, bg=COLORS["background"])
            actions_grid.pack(pady=10)

            new_cust_btn = tk.Button(
                actions_grid,
                text="New Customer",
                command=self.safe_new_customer,
                font=FONTS["base"],
                bg=COLORS["secondary"],
                fg=COLORS["text"],
                relief="flat",
                padx=20,
                pady=8,
                cursor="hand2",
            )
            new_cust_btn.grid(row=0, column=0, padx=5, pady=5)
            add_tooltip(new_cust_btn, "Create a new customer")

            new_invoice_btn = tk.Button(
                actions_grid,
                text="New Invoice",
                command=self.safe_new_invoice,
                font=FONTS["base"],
                bg=COLORS["primary"],
                fg=COLORS["section"],
                relief="flat",
                padx=20,
                pady=8,
                cursor="hand2",
            )
            new_invoice_btn.grid(row=0, column=1, padx=5, pady=5)
            add_tooltip(new_invoice_btn, "Create a new invoice")

            # Refresh button
            refresh_btn = tk.Button(
                actions_grid,
                text="Refresh",
                command=self.load_dashboard_stats,
                font=FONTS["base"],
                bg=COLORS["highlight"],
                fg="white",
                relief="flat",
                padx=20,
                pady=8,
                cursor="hand2",
            )
            refresh_btn.grid(row=0, column=2, padx=5, pady=5)
            add_tooltip(refresh_btn, "Refresh dashboard statistics")

        except Exception as e:
            logger.error(f"Error in setup_ui: {e}")
            self.create_error_ui(str(e))

    def create_error_ui(self, error_message):
        """Create a basic error UI when normal setup fails."""
        for child in self.winfo_children():
            child.destroy()
            
        error_frame = tk.Frame(self, bg=COLORS["background"])
        error_frame.pack(expand=True, fill=tk.BOTH)
        
        tk.Label(
            error_frame,
            text="Dashboard Error",
            font=FONTS["lg"],
            fg=COLORS["danger"],
            bg=COLORS["background"]
        ).pack(pady=20)
        
        tk.Label(
            error_frame,
            text=f"Error loading dashboard: {error_message}",
            font=FONTS["base"],
            fg=COLORS["text"],
            bg=COLORS["background"],
            wraplength=400,
            justify=tk.CENTER
        ).pack(pady=10)
        
        tk.Button(
            error_frame,
            text="Retry",
            command=self.retry_setup,
            font=FONTS["base"],
            bg=COLORS["primary"],
            fg="white",
            relief="flat",
            padx=20,
            pady=8
        ).pack(pady=10)

    def retry_setup(self):
        """Retry setting up the dashboard."""
        for child in self.winfo_children():
            child.destroy()
        self.setup_ui()

    def load_dashboard_stats(self) -> None:
        """Load dashboard statistics from services with comprehensive error handling."""
        try:
            # Clear existing stats
            for child in self.stats_frame.winfo_children():
                child.destroy()

            # Show loading indicator
            loading_label = tk.Label(
                self.stats_frame,
                text="Loading statistics...",
                font=FONTS["base"],
                fg=COLORS["text"],
                bg=COLORS["background"]
            )
            loading_label.pack(pady=20)
            self.update()  # Force UI update

            # Get statistics with individual error handling
            stats_data = self.gather_statistics()
            
            # Remove loading indicator
            loading_label.destroy()
            
            # Display statistics
            self.display_statistics(stats_data)
            
            self.stats_loaded = True
            self.last_error = None
            logger.info("Dashboard statistics loaded successfully")

        except Exception as e:
            logger.error(f"Error loading dashboard statistics: {e}")
            self.last_error = str(e)
            self.display_error_stats(str(e))

    def gather_statistics(self):
        """Gather statistics with individual error handling for each stat."""
        stats_data = {}
        
        # Customer count
        try:
            customers = self.customer_service.search_customers(
                user_id=self.user.id, search_term=""
            )
            stats_data['customer_count'] = len(customers)
        except Exception as e:
            logger.error(f"Error getting customer count: {e}")
            stats_data['customer_count'] = "Error"

        # Invoice statistics
        try:
            stats_data['invoice_count'] = self.invoice_service.get_invoice_count(self.user.id)
        except Exception as e:
            logger.error(f"Error getting invoice count: {e}")
            stats_data['invoice_count'] = "Error"

        try:
            stats_data['pending'] = self.invoice_service.get_pending_count(self.user.id)
        except Exception as e:
            logger.error(f"Error getting pending count: {e}")
            stats_data['pending'] = "Error"

        try:
            stats_data['overdue'] = self.invoice_service.get_overdue_count(self.user.id)
        except Exception as e:
            logger.error(f"Error getting overdue count: {e}")
            stats_data['overdue'] = "Error"

        return stats_data

    def display_statistics(self, stats_data):
        """Display statistics in cards."""
        stats = [
            ("Total Customers", stats_data.get('customer_count', 0), COLORS["primary"]),
            ("Total Invoices", stats_data.get('invoice_count', 0), COLORS["secondary"]),
            ("Pending Invoices", stats_data.get('pending', 0), COLORS["highlight"]),
            ("Overdue Invoices", stats_data.get('overdue', 0), "#e74c3c"),
        ]

        for i, (label, value, color) in enumerate(stats):
            stat_card = tk.Frame(self.stats_frame, bg=COLORS["section"], relief="raised", bd=2)
            stat_card.pack(
                side=tk.LEFT,
                fill=tk.BOTH,
                expand=True,
                padx=(0, 10) if i < len(stats) - 1 else 0,
            )

            tk.Label(
                stat_card,
                text=str(value),
                font=FONTS["lg"],
                fg=color,
                bg=COLORS["section"],
            ).pack(pady=(15, 5))

            tk.Label(
                stat_card,
                text=label,
                font=FONTS["base"],
                fg=COLORS["text"],
                bg=COLORS["section"],
            ).pack(pady=(0, 15))

    def display_error_stats(self, error_message):
        """Display error message in stats area."""
        error_frame = tk.Frame(self.stats_frame, bg=COLORS["section"], relief="raised", bd=2)
        error_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            error_frame,
            text="Error Loading Statistics",
            font=FONTS["base"],
            fg="#e74c3c",
            bg=COLORS["section"],
        ).pack(pady=(15, 5))

        tk.Label(
            error_frame,
            text=error_message,
            font=FONTS["sm"],
            fg=COLORS["text"],
            bg=COLORS["section"],
            wraplength=200,
            justify=tk.CENTER
        ).pack(pady=(0, 15))

    def safe_new_customer(self):
        """Safely call new customer function."""
        try:
            self.main_interface.new_customer()
        except Exception as e:
            logger.error(f"Error creating new customer: {e}")
            messagebox.showerror("Error", f"Failed to create customer: {e}")

    def safe_new_invoice(self):
        """Safely call new invoice function."""
        try:
            self.main_interface.new_invoice()
        except Exception as e:
            logger.error(f"Error creating new invoice: {e}")
            messagebox.showerror("Error", f"Failed to create invoice: {e}")

    def get_status(self):
        """Get current dashboard status for debugging."""
        return {
            'stats_loaded': self.stats_loaded,
            'last_error': self.last_error,
            'has_load_dashboard_stats': hasattr(self, 'load_dashboard_stats'),
            'class_name': self.__class__.__name__
        }