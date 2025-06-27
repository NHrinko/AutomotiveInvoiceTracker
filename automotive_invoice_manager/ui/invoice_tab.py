import tkinter as tk
import logging
from .theme import COLORS, FONTS

try:
    from automotive_invoice_manager.ui.invoices.invoice_list import InvoiceListFrame
    INVOICE_LIST_AVAILABLE = True
except ImportError:
    INVOICE_LIST_AVAILABLE = False
    logging.getLogger(__name__).info("InvoiceListFrame not available")

try:
    from automotive_invoice_manager.ui.invoices.invoice_form import InvoiceForm
    INVOICE_FORM_AVAILABLE = True
except ImportError:
    INVOICE_FORM_AVAILABLE = False

logger = logging.getLogger(__name__)


class InvoiceTab(tk.Frame):
    """Tab for managing invoices."""

    def __init__(self, parent, main_interface):
        super().__init__(parent, bg=COLORS["background"])
        self.main_interface = main_interface
        self.user = main_interface.user
        self.invoice_service = main_interface.invoice_service
        self.inner = None
        self.setup_ui()

    def setup_ui(self) -> None:
        if INVOICE_LIST_AVAILABLE:
            try:
                self.inner = InvoiceListFrame(
                    self,
                    self.user,
                    self.invoice_service,
                    self.main_interface.customer_service,
                    status_callback=self.main_interface.status_var.set,
                )
                self.inner.pack(fill=tk.BOTH, expand=True)
                return
            except Exception as e:
                logger.error(f"Error creating InvoiceListFrame: {e}")

        self._create_fallback()

    def _create_fallback(self) -> None:
        header_label = tk.Label(
            self,
            text="Invoice Management",
            font=FONTS["lg"],
            fg=COLORS["text"],
            bg=COLORS["background"],
        )
        header_label.pack(anchor=tk.W, padx=20, pady=(20, 20))

        action_frame = tk.Frame(self, bg=COLORS["background"])
        action_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            action_frame,
            text="New Invoice",
            command=self.main_interface.new_invoice,
            font=FONTS["base"],
            bg=COLORS["primary"],
            fg=COLORS["section"],
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=5)

        placeholder_frame = tk.Frame(self, bg=COLORS["section"], relief="raised", bd=2)
        placeholder_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(
            placeholder_frame,
            text=(
                "Your invoice modules are not available.\n\n"
                f"InvoiceListFrame: {'✓ Available' if INVOICE_LIST_AVAILABLE else '✗ Not found'}\n"
                f"InvoiceForm: {'✓ Available' if INVOICE_FORM_AVAILABLE else '✗ Not found'}\n\n"
                "Place them in automotive_invoice_manager/ui/invoices/ to enable this tab."
            ),
            font=FONTS["base"],
            fg=COLORS["text"],
            bg=COLORS["section"],
            justify=tk.CENTER,
        ).pack(expand=True)

    def load_data(self) -> None:
        if self.inner and hasattr(self.inner, "load_data"):
            self.inner.load_data()
