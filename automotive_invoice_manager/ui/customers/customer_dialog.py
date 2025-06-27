# automotive_invoice_manager/ui/dialogs/customer_dialog.py
"""Complete Customer Dialog with validation and modern UI."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime

from ...services.validators import CustomerValidator
from automotive_invoice_manager.config.settings import Settings

logger = logging.getLogger(__name__)
settings = Settings()
COLORS = settings.colors


class CustomerDialog:
    """Complete customer creation/editing dialog."""
    
    def __init__(self, parent, customer_service, user_id, customer=None):
        self.parent = parent
        self.customer_service = customer_service
        self.user_id = user_id
        self.customer = customer  # None for new customer
        self.result = None
        
        # Form variables
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        
        # Validation
        self.validator = CustomerValidator()
        self.validation_errors = {}
        
        self.setup_dialog()
        self.populate_form()
        
    def setup_dialog(self):
        """Setup the dialog window."""
        self.dialog = tk.Toplevel(self.parent)
        title = "Edit Customer" if self.customer else "New Customer"
        self.dialog.title(title)
        self.dialog.geometry("600x700")
        self.dialog.resizable(True, True)
        
        # Center dialog on parent
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center on screen
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 300
        y = (self.dialog.winfo_screenheight() // 2) - 350
        self.dialog.geometry(f"600x700+{x}+{y}")
        
        # Handle dialog closing
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        self.create_form()
        
        # Focus on first field
        self.name_entry.focus_set()
        
    def create_form(self):
        """Create the customer form with validation."""
        # Main container with styling
        main_frame = ttk.Frame(self.dialog, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_text = "Edit Customer" if self.customer else "New Customer"
        title_label = ttk.Label(header_frame, text=title_text, 
                               font=('Arial', 18, 'bold'),
                               foreground=COLORS['primary'])
        title_label.pack(side=tk.LEFT)
        
        if self.customer:
            created_date = self.customer.created_at.strftime("%b %d, %Y")
            subtitle = ttk.Label(header_frame, text=f"Created: {created_date}",
                                font=('Arial', 10),
                                foreground='gray')
            subtitle.pack(side=tk.RIGHT)
        
        # Form container
        form_frame = ttk.LabelFrame(main_frame, text="Customer Information", padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Name field (required)
        self.create_field(form_frame, 0, "Customer Name", self.name_var, 
                         self.name_entry_var, required=True)
        
        # Email field
        self.create_field(form_frame, 1, "Email Address", self.email_var, 
                         self.email_entry_var)
        
        # Phone field
        self.create_field(form_frame, 2, "Phone Number", self.phone_var, 
                         self.phone_entry_var)
        
        # Address field (multiline)
        self.create_text_field(form_frame, 3, "Address", 4)
        
        # Notes field (multiline)
        self.create_text_field(form_frame, 4, "Notes", 4)
        
        # Statistics (for existing customers)
        if self.customer:
            self.create_stats_section(form_frame, 5)
        
        # Button frame
        self.create_buttons(main_frame)
        
        # Bind validation
        self.setup_validation()
        
        # Keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self.on_save())
        self.dialog.bind('<Escape>', lambda e: self.on_cancel())
        
    def create_field(self, parent, row, label_text, var, entry_ref, required=False):
        """Create a standard form field with validation."""
        # Label with required indicator
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=row, column=0, sticky=tk.NW, padx=(0, 10), pady=8)
        
        label = ttk.Label(label_frame, text=label_text)
        label.pack(side=tk.LEFT)
        
        if required:
            req_label = ttk.Label(label_frame, text=" *", foreground='red')
            req_label.pack(side=tk.LEFT)
        
        # Entry field
        entry_frame = ttk.Frame(parent)
        entry_frame.grid(row=row, column=1, sticky=tk.EW, pady=8)
        entry_frame.columnconfigure(0, weight=1)
        
        entry = ttk.Entry(entry_frame, textvariable=var, font=('Arial', 11), width=40)
        entry.grid(row=0, column=0, sticky=tk.EW)
        
        # Error label
        error_label = ttk.Label(entry_frame, text="", foreground='red', 
                               font=('Arial', 9))
        error_label.grid(row=1, column=0, sticky=tk.W)
        
        # Store references
        setattr(self, f"{label_text.lower().replace(' ', '_')}_entry", entry)
        setattr(self, f"{label_text.lower().replace(' ', '_')}_error", error_label)
        
    def create_text_field(self, parent, row, label_text, height):
        """Create a multiline text field."""
        # Label
        ttk.Label(parent, text=f"{label_text}:").grid(row=row, column=0, 
                                                     sticky=tk.NW, padx=(0, 10), pady=8)
        
        # Text field with scrollbar
        text_frame = ttk.Frame(parent)
        text_frame.grid(row=row, column=1, sticky=tk.EW, pady=8)
        text_frame.columnconfigure(0, weight=1)
        
        text_widget = tk.Text(text_frame, height=height, width=40, 
                             font=('Arial', 11), wrap=tk.WORD)
        text_widget.grid(row=0, column=0, sticky=tk.EW)
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                                 command=text_widget.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Store reference
        setattr(self, f"{label_text.lower()}_text", text_widget)
        
        # Bind to update variable
        def update_var(event=None):
            content = text_widget.get("1.0", tk.END).strip()
            if label_text.lower() == "address":
                self.address_var.set(content)
            elif label_text.lower() == "notes":
                self.notes_var.set(content)
                
        text_widget.bind('<KeyRelease>', update_var)
        text_widget.bind('<FocusOut>', update_var)
        
    def create_stats_section(self, parent, row):
        """Create statistics section for existing customers."""
        stats_frame = ttk.LabelFrame(parent, text="Customer Statistics", padding="10")
        stats_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=20)
        stats_frame.columnconfigure((0, 1, 2), weight=1)
        
        try:
            stats = self.customer_service.get_customer_stats(self.customer.id)
            
            # Invoice count
            count_frame = ttk.Frame(stats_frame)
            count_frame.grid(row=0, column=0, padx=10)
            ttk.Label(count_frame, text="Total Invoices", font=('Arial', 10, 'bold')).pack()
            ttk.Label(count_frame, text=str(stats['invoice_count']), 
                     font=('Arial', 14), foreground=COLORS['primary']).pack()
            
            # Total billed
            billed_frame = ttk.Frame(stats_frame)
            billed_frame.grid(row=0, column=1, padx=10)
            ttk.Label(billed_frame, text="Total Billed", font=('Arial', 10, 'bold')).pack()
            ttk.Label(billed_frame, text=f"${stats['total_billed']:.2f}", 
                     font=('Arial', 14), foreground=COLORS['primary']).pack()
            
            # Customer since
            since_frame = ttk.Frame(stats_frame)
            since_frame.grid(row=0, column=2, padx=10)
            ttk.Label(since_frame, text="Customer Since", font=('Arial', 10, 'bold')).pack()
            since_date = self.customer.created_at.strftime("%b %Y")
            ttk.Label(since_frame, text=since_date, 
                     font=('Arial', 14), foreground=COLORS['primary']).pack()
            
        except Exception as e:
            logger.error(f"Error loading customer stats: {e}")
            ttk.Label(stats_frame, text="Statistics unavailable", 
                     foreground='gray').grid(row=0, column=0, columnspan=3)
        
    def create_buttons(self, parent):
        """Create action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Cancel button
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Save button
        save_text = "Update Customer" if self.customer else "Create Customer"
        save_btn = ttk.Button(button_frame, text=save_text, command=self.on_save)
        save_btn.pack(side=tk.RIGHT)
        
        # Delete button (for existing customers)
        if self.customer:
            delete_btn = ttk.Button(button_frame, text="Delete Customer", 
                                   command=self.on_delete)
            delete_btn.pack(side=tk.LEFT)
        
    def populate_form(self):
        """Populate form with customer data if editing."""
        if self.customer:
            self.name_var.set(self.customer.name)
            self.email_var.set(self.customer.email or "")
            self.phone_var.set(self.customer.phone or "")
            
            if self.customer.address:
                self.address_text.insert("1.0", self.customer.address)
                self.address_var.set(self.customer.address)
                
            if self.customer.notes:
                self.notes_text.insert("1.0", self.customer.notes)
                self.notes_var.set(self.customer.notes)
                
    def setup_validation(self):
        """Setup real-time validation."""
        self.name_var.trace('w', lambda *args: self.validate_field('name'))
        self.email_var.trace('w', lambda *args: self.validate_field('email'))
        self.phone_var.trace('w', lambda *args: self.validate_field('phone'))
        
    def validate_field(self, field_name):
        """Validate individual field."""
        error_label = getattr(self, f"{field_name}_error", None)
        if not error_label:
            return True
            
        if field_name == 'name':
            valid, message = self.validator.validate_name(self.name_var.get())
        elif field_name == 'email':
            valid, message = self.validator.validate_email(self.email_var.get())
        elif field_name == 'phone':
            valid, message = self.validator.validate_phone(self.phone_var.get())
        else:
            return True
            
        if valid:
            error_label.config(text="")
            if field_name in self.validation_errors:
                del self.validation_errors[field_name]
        else:
            error_label.config(text=message)
            self.validation_errors[field_name] = message
            
        return valid
        
    def validate_all(self):
        """Validate entire form."""
        # Update text variables
        if hasattr(self, 'address_text'):
            self.address_var.set(self.address_text.get("1.0", tk.END).strip())
        if hasattr(self, 'notes_text'):
            self.notes_var.set(self.notes_text.get("1.0", tk.END).strip())
            
        # Validate all fields
        valid = True
        valid &= self.validate_field('name')
        valid &= self.validate_field('email')
        valid &= self.validate_field('phone')
        
        # Check required fields
        if not self.name_var.get().strip():
            valid = False
            
        return valid and len(self.validation_errors) == 0
        
    def on_save(self):
        """Handle save button click."""
        if not self.validate_all():
            messagebox.showerror("Validation Error", 
                               "Please correct the errors in the form.")
            return
            
        try:
            customer_data = {
                'name': self.name_var.get().strip(),
                'email': self.email_var.get().strip() or None,
                'phone': self.phone_var.get().strip() or None,
                'address': self.address_var.get().strip() or None,
                'notes': self.notes_var.get().strip() or None
            }
            
            if self.customer:
                # Update existing customer
                success = self.customer_service.update_customer(
                    self.customer.id, customer_data, self.user_id
                )
                action = "updated"
            else:
                # Create new customer
                customer = self.customer_service.create_customer(
                    customer_data, self.user_id
                )
                success = customer is not None
                action = "created"
                
            if success:
                self.result = action
                messagebox.showinfo("Success", f"Customer {action} successfully!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", f"Failed to {action[:-1]} customer.")
                
        except Exception as e:
            logger.error(f"Error saving customer: {e}")
            messagebox.showerror("Error", f"Failed to save customer: {e}")
            
    def on_delete(self):
        """Handle delete button click."""
        if not self.customer:
            return
            
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{self.customer.name}'?\n\n"
            "This action cannot be undone. If the customer has invoices, "
            "the deletion will be blocked."
        )
        
        if result:
            try:
                success = self.customer_service.delete_customer(
                    self.customer.id, self.user_id
                )
                
                if success:
                    self.result = "deleted"
                    messagebox.showinfo("Success", "Customer deleted successfully!")
                    self.dialog.destroy()
                else:
                    messagebox.showwarning(
                        "Cannot Delete",
                        "This customer cannot be deleted because they have "
                        "associated invoices. Please remove all invoices first."
                    )
                    
            except Exception as e:
                logger.error(f"Error deleting customer: {e}")
                messagebox.showerror("Error", f"Failed to delete customer: {e}")
                
    def on_cancel(self):
        """Handle cancel button click."""
        self.result = None
        self.dialog.destroy()
        
    def show(self):
        """Show dialog and return result."""
        self.dialog.wait_window()
        return self.result
