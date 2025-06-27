# automotive_invoice_manager/ui/customer_tab.py - FIXED VERSION
import tkinter as tk
import logging
from .theme import COLORS, FONTS
# DIRECT imports - no try/except
from automotive_invoice_manager.ui.customers.customer_list import CustomerListFrame
from automotive_invoice_manager.ui.customers.customer_form import CustomerFormDialog

CUSTOMER_LIST_AVAILABLE = True
CUSTOMER_FORM_AVAILABLE = True

logger = logging.getLogger(__name__)
try:
    from automotive_invoice_manager.ui.customers.customer_list import CustomerListFrame
    CUSTOMER_LIST_AVAILABLE = True
except ImportError:
    CUSTOMER_LIST_AVAILABLE = False
    logging.getLogger(__name__).info("CustomerListFrame not available")

try:
    from automotive_invoice_manager.ui.customers.customer_form import CustomerFormDialog
    CUSTOMER_FORM_AVAILABLE = True
except ImportError:
    CUSTOMER_FORM_AVAILABLE = False

logger = logging.getLogger(__name__)


class CustomerTab(tk.Frame):
    """Tab for managing customers with fixed event handling."""

    def __init__(self, parent, main_interface):
        super().__init__(parent, bg=COLORS["background"])
        self.main_interface = main_interface
        self.user = main_interface.user
        self.customer_service = main_interface.customer_service
        self.inner = None
        
        # Remove the problematic tab change binding that was causing errors
        # parent.bind("<<NotebookTabChanged>>", self._on_tab_changed, add="+")
        
        self.setup_ui()

    def setup_ui(self) -> None:
        if CUSTOMER_LIST_AVAILABLE:
            try:
                self.inner = CustomerListFrame(
                    self,
                    self.user,
                    self.customer_service,
                    main_interface=self.main_interface,
                    status_callback=self.main_interface.status_var.set,
                    new_customer_callback=self.main_interface.new_customer,
                )
                self.inner.pack(fill=tk.BOTH, expand=True)
                return
            except Exception as e:
                logger.error(f"Error creating CustomerListFrame: {e}")

        self._create_fallback()

    def _create_fallback(self) -> None:
        header_label = tk.Label(
            self,
            text="Customer Management",
            font=FONTS["lg"],
            fg="black",
            bg=COLORS["background"],
        )
        header_label.pack(anchor=tk.W, padx=20, pady=(20, 20))

        info_frame = tk.Frame(self, bg=COLORS["section"], relief="raised", bd=2)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(
            info_frame,
            text=(
                "Your CustomerListFrame will appear here when available.\n\n"
                "Current status:\n"
                f"CustomerListFrame: {'✓ Available' if CUSTOMER_LIST_AVAILABLE else '✗ Not found'}\n"
                f"CustomerFormDialog: {'✓ Available' if CUSTOMER_FORM_AVAILABLE else '✗ Not found'}\n\n"
                "Make sure your customer modules are in:\n"
                "automotive_invoice_manager/ui/customers/"
            ),
            font=FONTS["base"],
            fg="black",
            bg=COLORS["section"],
            justify=tk.CENTER,
        ).pack(expand=True)

        button_frame = tk.Frame(self, bg=COLORS["background"])
        button_frame.pack(pady=10)
        self.button_frame = button_frame

        tk.Button(
            button_frame,
            text="New Customer",
            command=self.main_interface.new_customer,
            font=FONTS["base"],
            bg=COLORS["secondary"],
            fg="black",
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=5)

    def refresh_data(self, callback=None) -> None:
        """Refresh customer data with optional callback support."""
        try:
            if self.inner and hasattr(self.inner, "refresh_data"):
                # Check if the inner refresh_data method accepts callback
                import inspect
                sig = inspect.signature(self.inner.refresh_data)
                if 'callback' in sig.parameters:
                    self.inner.refresh_data(callback=callback)
                else:
                    self.inner.refresh_data()
                    # Execute callback manually if inner method doesn't support it
                    if callback:
                        callback()
            else:
                # No inner frame, just execute callback if provided
                if callback:
                    callback()
        except Exception as e:
            logger.error(f"Error refreshing customer data: {e}")
            # Still execute callback even if refresh fails
            if callback:
                callback()