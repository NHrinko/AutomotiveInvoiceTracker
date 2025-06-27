# ui/customers/customer_list.py - Customer List Frame
import tkinter as tk
from tkinter import ttk, messagebox

from automotive_invoice_manager.ui.components.table_helpers import (
    create_table_with_scrollbars,
    create_context_menu,
)
import logging
from datetime import datetime


class CustomerListFrame(ttk.Frame):
    """Frame for displaying and managing customer list with search functionality."""

# FIX for CustomerListFrame __init__ method
# File: automotive_invoice_manager/ui/customers/customer_list.py

# FIND the __init__ method in CustomerListFrame class and REPLACE it with this:

    def __init__(
        self,
        parent,
        user,
        customer_service,
        *,
        main_interface=None,
        status_callback=None,
        new_customer_callback=None,
    ):
        # CRITICAL FIX: Only pass parent to Frame.__init__()
        super().__init__(parent)  # <-- Only parent, not other args
        
        # Store all the custom parameters as instance attributes
        self.user = user
        self.customer_service = customer_service
        self.main_interface = main_interface
        self.status_callback = status_callback or (lambda _msg: None)
        self.new_customer_callback = new_customer_callback or (lambda: None)

        # Search state
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_changed)
        self.current_search = ""

        # Sort state
        self.sort_column = "name"
        self.sort_reverse = False

        self.setup_ui()
        self.load_customers()

    # The issue was that the original __init__ was probably calling:
    # super().__init__(parent, user, customer_service, ...)
    # 
    # But ttk.Frame.__init__() only accepts (self, master, **kwargs)
    # So we need to only pass the parent (master) to super().__init__()

    # ALTERNATIVE: If you can't find the exact __init__ method, 
    # look for any line that looks like:
    #   super().__init__(parent, user, customer_service, ...)
    # 
    # And change it to:
    #   super().__init__(parent)
    def setup_ui(self):
        """Setup the customer list interface."""
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Title and action buttons
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(fill=tk.X)

        ttk.Label(title_frame, text="Customers", style="Heading.TLabel").pack(
            side=tk.LEFT
        )

        # Action buttons
        action_frame = ttk.Frame(title_frame)
        action_frame.pack(side=tk.RIGHT)

        ttk.Button(
            action_frame,
            text="New Customer",
            command=self.new_customer,
            style="Primary.TButton",
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Button(action_frame, text="Export", command=self.export_customers).pack(
            side=tk.LEFT, padx=2
        )

        # Search frame
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))

        self.search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var, width=30
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(
            side=tk.LEFT, padx=2
        )

        # Results info
        self.results_var = tk.StringVar()
        ttk.Label(
            search_frame,
            textvariable=self.results_var,
            font=("Arial", 9),
            foreground="gray",
        ).pack(side=tk.RIGHT)

        # Customer table frame
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Setup customer table
        self.setup_customer_table(table_frame)

        # Context menu
        self.setup_context_menu()

        
    def refresh_data(self, callback=None):
        """Public method to refresh customer data with optional callback."""
        try:
            self.load_customers(self.current_search)
            if callback:
                callback()
        except Exception as e:
            logging.error(f"Error refreshing customer data: {e}")
            # Still execute callback even if refresh fails
            if callback:
                callback()

    def export_customers(self):
        """Export customers to CSV file."""
        try:
            import csv
            from tkinter import filedialog
            
            # Get all customers
            customers = self.customer_service.get_all_customers(self.user.id)
            
            if not customers:
                messagebox.showinfo("Export", "No customers to export.")
                return
            
            # Ask user where to save
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Customers"
            )
            
            if not filename:
                return
            
            # Write CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Name', 'Email', 'Phone', 'Address', 'Notes', 'Created'])
                
                # Write customer data
                for customer in customers:
                    writer.writerow([
                        customer.name,
                        customer.email or '',
                        customer.phone or '',
                        customer.address or '',
                        customer.notes or '',
                        customer.created_at.strftime('%Y-%m-%d') if customer.created_at else ''
                    ])
            
            messagebox.showinfo("Export Complete", f"Exported {len(customers)} customers to {filename}")
            self.status_callback(f"Exported {len(customers)} customers")
            
        except Exception as e:
            logging.error(f"Error exporting customers: {e}")
            messagebox.showerror("Export Error", f"Failed to export customers: {e}")

    def setup_customer_table(self, parent):
        """Setup the customer data table with scrollbars."""
        columns = ("name", "email", "phone", "invoices", "total_billed", "created")

        column_configs = {
            "name": ("Customer Name", 200, tk.W),
            "email": ("Email", 180, tk.W),
            "phone": ("Phone", 120, tk.W),
            "invoices": ("Invoices", 80, tk.CENTER),
            "total_billed": ("Total Billed", 100, tk.E),
            "created": ("Created", 100, tk.CENTER),
        }

        self.customer_tree = create_table_with_scrollbars(
            parent,
            columns=columns,
            column_configs=column_configs,
            sort_callback=self.sort_by_column,
            selectmode="extended",
        )

        # Bind events
        self.customer_tree.bind("<Double-1>", self.on_customer_double_click)
        self.customer_tree.bind("<Button-3>", self.show_context_menu)  # Right click
        self.customer_tree.bind("<Return>", self.edit_selected_customer)
        self.customer_tree.bind("<Delete>", self.delete_selected_customers)

        # Bind keyboard shortcuts
        self.bind_all("<F5>", lambda e: self.refresh_data())
        self.bind_all("<Control-f>", lambda e: self.focus_search())

    def setup_context_menu(self):
        """Setup right-click context menu."""
        self.context_menu = create_context_menu(
            self,
            [
                ("Edit Customer", self.edit_selected_customer),
                ("View Invoices", self.view_customer_invoices),
                None,
                ("New Invoice", self.new_invoice_for_customer),
                None,
                ("Delete Customer", self.delete_selected_customers),
            ],
        )

    def load_customers(self, search_term=""):
        """Load customers from backend.database with optional search."""
        try:
            self.status_callback("Loading customers...")

            # Get customers from service
            customers = self.customer_service.search_customers(
                user_id=self.user.id,
                search_term=search_term,
                sort_by=self.sort_column,
                sort_desc=self.sort_reverse,
            )

            # Clear existing items
            for item in self.customer_tree.get_children():
                self.customer_tree.delete(item)

            # Add customers to tree
            for customer in customers:
                # Get customer statistics (invoice count and total billed)
                stats = self.customer_service.get_customer_stats(customer.id)

                values = (
                    customer.name,
                    customer.email or "",
                    customer.phone or "",
                    stats.get("invoice_count", 0),
                    f"${stats.get('total_billed', 0):.2f}",
                    customer.created_at.strftime("%Y-%m-%d"),
                )

                self.customer_tree.insert(
                    "",
                    tk.END,
                    iid=str(customer.id),
                    values=values,
                )

            # Update results info
            count = len(customers)
            search_text = f" matching '{search_term}'" if search_term else ""
            self.results_var.set(f"{count} customer(s){search_text}")

            self.status_callback(f"Loaded {count} customers")

        except Exception as e:
            logging.error(f"Error loading customers: {e}")
            messagebox.showerror("Error", f"Failed to load customers: {e}")
            self.status_callback("Error loading customers")

    def on_search_changed(self, *args):
        """Handle search text changes with debouncing."""
        search_term = self.search_var.get().strip()

        # Cancel previous scheduled search
        if hasattr(self, "_search_job"):
            self.after_cancel(self._search_job)

        # Schedule new search with 300ms delay
        self._search_job = self.after(300, lambda: self.perform_search(search_term))

    def perform_search(self, search_term):
        """Perform the actual search operation."""
        if search_term != self.current_search:
            self.current_search = search_term
            self.load_customers(search_term)

    def clear_search(self):
        """Clear search and reload all customers."""
        self.search_var.set("")
        self.current_search = ""
        self.load_customers()

    def focus_search(self):
        """Focus the search entry field."""
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)

    def sort_by_column(self, column):
        """Sort customers by specified column."""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        self.load_customers(self.current_search)

    def refresh_data(self, callback=None):
        """Enhanced refresh that forces database reload."""
        try:
            # Clear current search to ensure we see all customers
            current_search = self.current_search
            self.current_search = ""
            
            # Force reload from database
            self.load_customers("")
            
            # Restore search if there was one
            if current_search:
                self.current_search = current_search
                self.search_var.set(current_search)
                self.load_customers(current_search)
            
            # Execute callback
            if callback:
                callback()
                
            self.status_callback("Customer list refreshed")
            
        except Exception as e:
            logging.error(f"Error refreshing customer data: {e}")
            if callback:
                callback()
    def new_customer(self):
        """Create new customer - QUICK FIX."""
        try:
            from automotive_invoice_manager.ui.customers.customer_form import CustomerFormDialog
            
            dialog = CustomerFormDialog(
                self.winfo_toplevel(), 
                self.customer_service, 
                self.user
            )
            result = dialog.show()
            
            if result:
                self.refresh_data()
                self.status_callback("Customer created successfully")
                
                if hasattr(self, 'main_interface') and self.main_interface:
                    self.main_interface.load_dashboard_data()
                    
        except Exception as e:
            logging.error(f"Error creating customer: {e}")
            messagebox.showerror("Error", f"Failed to create customer: {e}")
    def get_selected_customers(self):
        """Get list of selected customer IDs."""
        selected_items = self.customer_tree.selection()
        customer_ids = []

        for item in selected_items:
            try:
                customer_ids.append(int(item))
            except ValueError:
                continue

        return customer_ids

    def on_customer_double_click(self, event):
        """Handle double-click on customer (edit)."""
        self.edit_selected_customer()

    def show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select item under cursor
        item = self.customer_tree.identify_row(event.y)
        if item:
            self.customer_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)


    def edit_selected_customer(self, event=None):
        """Edit selected customer."""
        selected_ids = self.get_selected_customers()

        if not selected_ids:
            messagebox.showwarning("Warning", "Please select a customer to edit.")
            return

        if len(selected_ids) > 1:
            messagebox.showwarning(
                "Warning", "Please select only one customer to edit."
            )
            return

        customer_id = selected_ids[0]

        try:
            customer = self.customer_service.get_customer(customer_id)
            if not customer:
                messagebox.showerror("Error", "Customer not found.")
                return

            from automotive_invoice_manager.ui.customers.customer_form import CustomerFormDialog

            dialog = CustomerFormDialog(
                self.winfo_toplevel(), self.customer_service, self.user, customer
            )
            result = dialog.show()

            if result:
                self.refresh_data()
                self.status_callback("Customer updated successfully")

        except Exception as e:
            logging.error(f"Error editing customer: {e}")
            messagebox.showerror("Error", f"Failed to edit customer: {e}")

    def delete_selected_customers(self, event=None):
        """Delete selected customers."""
        selected_ids = self.get_selected_customers()

        if not selected_ids:
            messagebox.showwarning("Warning", "Please select customer(s) to delete.")
            return

        # Confirm deletion
        count = len(selected_ids)
        message = f"Are you sure you want to delete {count} customer(s)?\n\nThis action cannot be undone."

        if not messagebox.askyesno("Confirm Deletion", message):
            return

        try:
            deleted_count = 0
            errors = []

            for customer_id in selected_ids:
                try:
                    success = self.customer_service.delete_customer(
                        customer_id, self.user.id
                    )
                    if success:
                        deleted_count += 1
                    else:
                        errors.append(
                            f"Customer ID {customer_id}: Cannot delete (has invoices)"
                        )
                except Exception as e:
                    errors.append(f"Customer ID {customer_id}: {str(e)}")

            # Show results
            if deleted_count > 0:
                self.refresh_data()
                self.status_callback(f"Deleted {deleted_count} customer(s)")

            if errors:
                error_message = f"Some customers could not be deleted:\n\n" + "\n".join(
                    errors
                )
                messagebox.showwarning("Partial Success", error_message)

        except Exception as e:
            logging.error(f"Error deleting customers: {e}")
            messagebox.showerror("Error", f"Failed to delete customers: {e}")

    def view_customer_invoices(self):
        """View invoices for selected customer."""
        selected_ids = self.get_selected_customers()

        if not selected_ids:
            messagebox.showwarning("Warning", "Please select a customer.")
            return

        if len(selected_ids) > 1:
            messagebox.showwarning("Warning", "Please select only one customer.")
            return

        customer_id = selected_ids[0]
        if not self.main_interface:
            messagebox.showinfo(
                "Info",
                f"View invoices for customer ID {customer_id} - To be implemented",
            )
            return

        invoice_tab = self.main_interface.tabs.get("invoices")
        if invoice_tab and getattr(invoice_tab, "inner", None):
            customer = self.customer_service.get_customer(customer_id)
            if customer:
                invoice_tab.inner.search_var.set(customer.name)
                invoice_tab.inner.load_data()
            self.main_interface.notebook.select(invoice_tab)
        else:
            messagebox.showinfo(
                "Info",
                f"Invoice tab not available for customer ID {customer_id}",
            )
# PATCH FOR automotive_invoice_manager/ui/customers/customer_list.py
# Replace the new_invoice_for_customer method with this:

    def new_invoice_for_customer(self):
        """Create new invoice for selected customer."""
        selected_ids = self.get_selected_customers()

        if not selected_ids:
            messagebox.showwarning("Warning", "Please select a customer.")
            return

        if len(selected_ids) > 1:
            messagebox.showwarning("Warning", "Please select only one customer.")
            return

        customer_id = selected_ids[0]
        if not self.main_interface:
            messagebox.showinfo(
                "Info",
                f"Create invoice for customer ID {customer_id} - To be implemented",
            )
            return

        try:
            # FIXED: Import the correct InvoiceFormDialog
            from automotive_invoice_manager.ui.components.invoice_widgets import InvoiceFormDialog

            customers = self.customer_service.get_all_customers(self.user.id)
            
            # FIXED: Pass user parameter
            dialog = InvoiceFormDialog(
                self.winfo_toplevel(),
                self.main_interface.invoice_service,
                customers,
                self.user  # <-- This was missing!
            )
            
            # Pre-select the customer
            cust = self.customer_service.get_customer(customer_id)
            if cust:
                dialog.customer_cb.set(cust.name)
                
            self.wait_window(dialog)

            # Refresh invoice tab
            invoice_tab = self.main_interface.tabs.get("invoices")
            if invoice_tab and getattr(invoice_tab, "inner", None):
                invoice_tab.inner.load_data()
                self.main_interface.notebook.select(invoice_tab)
                
        except Exception as e:
            logging.error(f"Error creating invoice for customer {customer_id}: {e}")
            messagebox.showerror("Error", f"Failed to create invoice: {e}")