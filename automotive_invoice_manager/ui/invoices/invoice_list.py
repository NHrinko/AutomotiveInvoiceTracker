# automotive_invoice_manager/ui/invoices/invoice_list.py - FIXED VERSION

from tkinter import ttk, messagebox
import tkinter as tk

from ..components.invoice_widgets import (
    InvoiceListFrame as _BaseList,
    InvoiceDetailWindow,
)

# Import the fixed invoice form
try:
    from .invoice_form import InvoiceFormDialog
    INVOICE_FORM_AVAILABLE = True
except ImportError:
    try:
        from ..components.invoice_widgets import InvoiceFormDialog
        INVOICE_FORM_AVAILABLE = True
    except ImportError:
        INVOICE_FORM_AVAILABLE = False


class InvoiceListFrame(_BaseList):
    """Invoice list with search, filters and pagination."""

    def __init__(
        self,
        parent,
        user,
        invoice_service,
        customer_service,
        status_callback=None,
    ):
        self.user = user
        self.customer_service = customer_service
        self.status_callback = status_callback or (lambda _msg: None)
        super().__init__(parent, invoice_service)
        # refresh when child dialogs signal updates
        self.bind("<<InvoiceUpdated>>", lambda e: self.load_data())
        self.bind("<<InvoiceDeleted>>", lambda e: self.load_data())

    def load_data(self):
        search = self.search_var.get()
        status = (
            self.status_var.get().lower()
            if self.status_var.get() and self.status_var.get() != "All"
            else None
        )
        items, total_pages = self.invoice_service.get_invoices(
            self.user.id,
            page=self.current_page,
            per_page=self.per_page,
            search=search,
            status=status,
        )
        self.tree.delete(*self.tree.get_children())
        for inv in items:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    inv.invoice_number,
                    inv.customer.name,
                    inv.issued_date,
                    inv.status,
                    f"{inv.total:.2f}",
                ),
            )
        self.total_pages = total_pages
        self.page_label.config(text=f"Page {self.current_page} of {self.total_pages}")
        self.prev_btn.config(
            state=(tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        )
        self.next_btn.config(
            state=(tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED)
        )

    def handle_open_detail(self, invoice_number):
        inv = self.invoice_service.get_invoice_by_number(self.user.id, invoice_number)
        if not inv:
            messagebox.showerror("Error", "Invoice not found")
            return
        InvoiceDetailWindow(self, self.invoice_service, inv.id)

    def new_invoice(self):
        """Create a new invoice with correct parameters."""
        if not INVOICE_FORM_AVAILABLE:
            messagebox.showerror("Error", "Invoice form is not available")
            return
            
        try:
            customers = self.customer_service.get_all_customers(self.user.id)
            
            if not customers:
                result = messagebox.askyesno(
                    "No Customers", 
                    "You need at least one customer to create an invoice.\n\nWould you like to create a customer first?"
                )
                if result:
                    # Try to trigger customer creation
                    if hasattr(self, 'main_interface') and hasattr(self.main_interface, 'new_customer'):
                        self.main_interface.new_customer()
                return
            
            # FIXED: Use correct parameter order: parent, invoice_service, user, customers
            dialog = InvoiceFormDialog(
                self, 
                self.invoice_service, 
                self.user,
                customers
            )
            result = dialog.show()
            
            if result:
                self.load_data()  # Refresh the list
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create invoice: {e}")

    def open_invoice_form(self, invoice):
        """Open invoice form for editing with correct parameters."""
        if not INVOICE_FORM_AVAILABLE:
            messagebox.showerror("Error", "Invoice form is not available")
            return
            
        try:
            customers = self.customer_service.get_all_customers(self.user.id)
            
            # FIXED: Use correct parameter order: parent, invoice_service, user, customers, invoice
            dialog = InvoiceFormDialog(
                self, 
                self.invoice_service, 
                self.user,
                customers, 
                invoice
            )
            result = dialog.show()
            
            if result:
                self.load_data()  # Refresh the list
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit invoice: {e}")