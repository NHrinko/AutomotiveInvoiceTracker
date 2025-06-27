# automotive_invoice_manager/ui/invoices/invoice_form.py - FIXED VERSION

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
import logging

try:
    from tkcalendar import DateEntry
except ImportError:
    # Fallback for missing tkcalendar
    class DateEntry(ttk.Entry):
        def __init__(self, master, **kwargs):
            super().__init__(master, **kwargs)
            self._date = date.today()
            # FIXED: Store parent reference properly
            self.parent = parent  # <-- ADD THIS LINE
        def get_date(self):
            return self._date
        
        def set_date(self, date_obj):
            self._date = date_obj
            self.delete(0, tk.END)
            self.insert(0, date_obj.strftime('%Y-%m-%d'))

from automotive_invoice_manager.ui.theme import COLORS, FONTS

logger = logging.getLogger(__name__)


class InvoiceFormDialog(tk.Toplevel):
    """Dialog for creating and editing invoices with proper customer integration."""


    def __init__(self, parent, invoice_service, user, customers=None, invoice=None):
        """Initialize invoice form dialog.
        
        Args:
            parent: Parent window
            invoice_service: Service for invoice operations
            user: Current user object
            customers: List of customer objects
            invoice: Invoice to edit (None for new invoice)
        """
        super().__init__(parent)
        
        # CRITICAL FIX: Store all parameters as instance attributes
        self.parent = parent                    # <-- ADD THIS LINE
        self.invoice_service = invoice_service  # <-- Already exists
        self.user = user                        # <-- Already exists
        self.customers = customers or []        # <-- Already exists
        self.invoice = invoice                  # <-- Already exists
        self.result = None                      # <-- Already exists
        
        # Form variables
        self.customer_var = tk.StringVar()
        self.invoice_number_var = tk.StringVar()
        self.issued_date_obj = date.today()
        self.due_date_obj = date.today() + timedelta(days=30)
        self.status_var = tk.StringVar(value="draft")
        self.total_var = tk.StringVar(value="0.00")
        
        # Line items storage
        self.line_items = []
        
        self.setup_dialog()
        self.create_form()
        
        if self.invoice:
            self.populate_form()
        else:
            self.add_line_item()  # Start with one line item

    # 
    def setup_dialog(self):
        """Setup dialog window properties."""
        self.title("Edit Invoice" if self.invoice else "New Invoice")
        self.geometry("800x650")
        self.resizable(True, True)
        
        # Center dialog
        self.transient(self.parent)
        self.grab_set()
        
        x = (self.winfo_screenwidth() // 2) - 400
        y = (self.winfo_screenheight() // 2) - 350
        self.geometry(f"800x650+{x}+{y}")
        
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def create_form(self):
        """Create the invoice form."""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_text = "Edit Invoice" if self.invoice else "New Invoice"
        title_label = ttk.Label(main_frame, text=title_text, style="Heading.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Create form sections
        self.create_header_section(main_frame)
        self.create_line_items_section(main_frame)
        self.create_total_section(main_frame)
        self.create_buttons_section(main_frame)
        
        # Bind Enter and Escape keys
        self.bind('<Return>', lambda e: self.on_save())
        self.bind('<Escape>', lambda e: self.on_cancel())

    def create_header_section(self, parent):
        """Create invoice header fields."""
        header_frame = ttk.LabelFrame(parent, text="Invoice Information", padding=15)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Configure grid
        header_frame.columnconfigure(1, weight=1)
        header_frame.columnconfigure(3, weight=1)
        
        # Customer selection
        ttk.Label(header_frame, text="Customer *:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        
        self.customer_combo = ttk.Combobox(
            header_frame, 
            textvariable=self.customer_var,
            values=[c.name for c in self.customers],
            state="readonly",
            width=30
        )
        self.customer_combo.grid(row=0, column=1, sticky=tk.EW, padx=(0, 20), pady=5)
        
        # Invoice number
        ttk.Label(header_frame, text="Invoice #:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10), pady=5)
        self.invoice_number_entry = ttk.Entry(header_frame, textvariable=self.invoice_number_var, width=20)
        self.invoice_number_entry.grid(row=0, column=3, sticky=tk.EW, pady=5)
        
        # Dates
        ttk.Label(header_frame, text="Issued Date *:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.issued_date_entry = DateEntry(header_frame, width=15)
        self.issued_date_entry.set_date(self.issued_date_obj)
        self.issued_date_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        ttk.Label(header_frame, text="Due Date *:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=5)
        self.due_date_entry = DateEntry(header_frame, width=15)
        self.due_date_entry.set_date(self.due_date_obj)
        self.due_date_entry.grid(row=1, column=3, sticky=tk.W, pady=5)
        
        # Status
        ttk.Label(header_frame, text="Status:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        status_combo = ttk.Combobox(
            header_frame,
            textvariable=self.status_var,
            values=["draft", "sent", "paid", "overdue"],
            state="readonly",
            width=15
        )
        status_combo.grid(row=2, column=1, sticky=tk.W, pady=5)

    def create_line_items_section(self, parent):
        """Create line items section."""
        items_frame = ttk.LabelFrame(parent, text="Line Items", padding=15)
        items_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Header row
        header_frame = ttk.Frame(items_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Description", font=FONTS["base"]).grid(row=0, column=0, padx=5)
        ttk.Label(header_frame, text="Hours", font=FONTS["base"]).grid(row=0, column=1, padx=5)
        ttk.Label(header_frame, text="Rate", font=FONTS["base"]).grid(row=0, column=2, padx=5)
        ttk.Label(header_frame, text="Parts", font=FONTS["base"]).grid(row=0, column=3, padx=5)
        ttk.Label(header_frame, text="Tax %", font=FONTS["base"]).grid(row=0, column=4, padx=5)
        ttk.Label(header_frame, text="Total", font=FONTS["base"]).grid(row=0, column=5, padx=5)
        
        # Scrollable frame for line items
        canvas = tk.Canvas(items_frame, height=200)
        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add item button
        add_button_frame = ttk.Frame(items_frame)
        add_button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            add_button_frame,
            text="+ Add Line Item",
            command=self.add_line_item
        ).pack(side=tk.LEFT)

    def create_total_section(self, parent):
        """Create total section."""
        total_frame = ttk.Frame(parent)
        total_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(total_frame, text="Total:", font=FONTS["lg"]).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Label(total_frame, textvariable=self.total_var, font=FONTS["lg"]).pack(side=tk.RIGHT)

    def create_buttons_section(self, parent):
        """Create action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        # Cancel button
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.on_cancel
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Save button
        save_text = "Update Invoice" if self.invoice else "Create Invoice"
        ttk.Button(
            button_frame,
            text=save_text,
            command=self.on_save,
            style="Primary.TButton"
        ).pack(side=tk.RIGHT)

    def add_line_item(self):
        """Add a new line item row."""
        row_frame = ttk.Frame(self.scrollable_frame)
        row_frame.pack(fill=tk.X, pady=2)
        
        # Description
        desc_entry = ttk.Entry(row_frame, width=25)
        desc_entry.grid(row=0, column=0, padx=2, sticky=tk.EW)
        
        # Hours
        hours_var = tk.StringVar(value="0")
        hours_entry = ttk.Entry(row_frame, textvariable=hours_var, width=8)
        hours_entry.grid(row=0, column=1, padx=2)
        
        # Rate
        rate_var = tk.StringVar(value="0.00")
        rate_entry = ttk.Entry(row_frame, textvariable=rate_var, width=10)
        rate_entry.grid(row=0, column=2, padx=2)
        
        # Parts
        parts_var = tk.StringVar(value="0.00")
        parts_entry = ttk.Entry(row_frame, textvariable=parts_var, width=10)
        parts_entry.grid(row=0, column=3, padx=2)
        
        # Tax
        tax_var = tk.StringVar(value="0.00")
        tax_entry = ttk.Entry(row_frame, textvariable=tax_var, width=8)
        tax_entry.grid(row=0, column=4, padx=2)
        
        # Line total (calculated)
        line_total_var = tk.StringVar(value="0.00")
        line_total_label = ttk.Label(row_frame, textvariable=line_total_var, width=10)
        line_total_label.grid(row=0, column=5, padx=2)
        
        # Remove button
        remove_btn = ttk.Button(
            row_frame,
            text="Remove",
            command=lambda: self.remove_line_item(row_frame),
            width=8
        )
        remove_btn.grid(row=0, column=6, padx=2)
        
        # Store line item data
        line_item = {
            'frame': row_frame,
            'description': desc_entry,
            'hours': hours_var,
            'rate': rate_var,
            'parts': parts_var,
            'tax': tax_var,
            'total': line_total_var
        }
        
        self.line_items.append(line_item)
        
        # Bind calculation events
        for var in [hours_var, rate_var, parts_var, tax_var]:
            var.trace('w', self.calculate_totals)
        
        # Configure grid weights
        row_frame.columnconfigure(0, weight=2)
        
        self.calculate_totals()

    def remove_line_item(self, frame):
        """Remove a line item."""
        # Find and remove from line_items list
        self.line_items = [item for item in self.line_items if item['frame'] != frame]
        
        # Destroy the frame
        frame.destroy()
        
        # Recalculate totals
        self.calculate_totals()

    def calculate_totals(self, *args):
        """Calculate line totals and grand total."""
        grand_total = 0.0
        
        for item in self.line_items:
            try:
                hours = float(item['hours'].get() or 0)
                rate = float(item['rate'].get() or 0)
                parts = float(item['parts'].get() or 0)
                tax = float(item['tax'].get() or 0)
                
                # Calculate line total: (hours * rate + parts) * (1 + tax/100)
                subtotal = (hours * rate) + parts
                line_total = subtotal * (1 + tax / 100)
                
                item['total'].set(f"{line_total:.2f}")
                grand_total += line_total
                
            except ValueError:
                item['total'].set("0.00")
        
        self.total_var.set(f"{grand_total:.2f}")

    def populate_form(self):
        """Populate form with existing invoice data."""
        if not self.invoice:
            return
        
        try:
            # Set basic fields
            self.customer_var.set(self.invoice.customer.name)
            self.invoice_number_var.set(self.invoice.invoice_number)
            self.issued_date_entry.set_date(self.invoice.issued_date)
            self.due_date_entry.set_date(self.invoice.due_date)
            self.status_var.set(self.invoice.status)
            
            # Clear existing line items
            for item in self.line_items:
                item['frame'].destroy()
            self.line_items.clear()
            
            # Add invoice line items
            for line_item in self.invoice.line_items:
                self.add_line_item()
                current_item = self.line_items[-1]
                
                current_item['description'].insert(0, line_item.get('description', ''))
                current_item['hours'].set(str(line_item.get('hours', line_item.get('quantity', 0))))
                current_item['rate'].set(str(line_item.get('rate', 0)))
                current_item['parts'].set(str(line_item.get('parts', 0)))
                current_item['tax'].set(str(line_item.get('tax', 0)))
            
            # If no line items, add one empty one
            if not self.line_items:
                self.add_line_item()
                
            self.calculate_totals()
            
        except Exception as e:
            logger.error(f"Error populating form: {e}")
            messagebox.showerror("Error", f"Error loading invoice data: {e}")

    def validate_form(self):
        """Validate form data."""
        errors = []
        
        # Check customer
        if not self.customer_var.get():
            errors.append("Please select a customer")
        
        # Check dates
        try:
            issued_date = self.issued_date_entry.get_date()
            due_date = self.due_date_entry.get_date()
            
            if due_date < issued_date:
                errors.append("Due date cannot be before issued date")
                
        except Exception as e:
            errors.append(f"Invalid date format: {e}")
        
        # Check line items
        valid_items = 0
        for item in self.line_items:
            if item['description'].get().strip():
                valid_items += 1
        
        if valid_items == 0:
            errors.append("Please add at least one line item with a description")
        
        return errors

    def get_form_data(self):
        """Get form data as dictionary."""
        # Get line items
        line_items = []
        for item in self.line_items:
            if item['description'].get().strip():
                line_items.append({
                    'description': item['description'].get().strip(),
                    'hours': float(item['hours'].get() or 0),
                    'rate': float(item['rate'].get() or 0),
                    'parts': float(item['parts'].get() or 0),
                    'tax': float(item['tax'].get() or 0)
                })
        
        return {
            'customer': self.customer_var.get(),
            'invoice_number': self.invoice_number_var.get().strip() if self.invoice_number_var.get().strip() else None,
            'issued_date': self.issued_date_entry.get_date(),
            'due_date': self.due_date_entry.get_date(),
            'status': self.status_var.get(),
            'line_items': line_items
        }

    def on_save(self):
        """Handle save button click."""
        try:
            # Validate form
            errors = self.validate_form()
            if errors:
                messagebox.showerror("Validation Error", "\n".join(errors))
                return
            
            # Get form data
            form_data = self.get_form_data()
            
            # Save invoice
            if self.invoice:
                # Update existing invoice
                success = self.invoice_service.update_invoice(self.invoice.id, form_data)
                action = "updated"
            else:
                # Create new invoice
                invoice = self.invoice_service.create_invoice(self.user, form_data)
                success = invoice is not None
                action = "created"
            
            if success:
                self.result = action
                messagebox.showinfo("Success", f"Invoice {action} successfully!")
                self.destroy()
            else:
                messagebox.showerror("Error", f"Failed to {action[:-1]} invoice")
                
        except Exception as e:
            logger.error(f"Error saving invoice: {e}")
            messagebox.showerror("Error", f"Failed to save invoice: {e}")

    def on_cancel(self):
        """Handle cancel button click."""
        self.result = None
        self.destroy()

    def show(self):
        """Show dialog and return result."""
        self.wait_window()
        return self.result


# For backwards compatibility
class InvoiceForm(InvoiceFormDialog):
    """Alias for InvoiceFormDialog to maintain compatibility."""
    pass