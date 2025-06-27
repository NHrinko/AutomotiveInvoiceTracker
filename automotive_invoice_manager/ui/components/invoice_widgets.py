# automotive_invoice_manager/ui/components/invoice_widgets.py - FIXED VERSION

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from automotive_invoice_manager.ui.theme import COLORS
except Exception:  # pragma: no cover - theme may not load in tests
    COLORS = {"dark_gray": "#404040"}

try:
    from tkcalendar import DateEntry
except ImportError:
    # Fallback for missing tkcalendar
    class DateEntry(ttk.Entry):
        def __init__(self, master, **kwargs):
            super().__init__(master, **kwargs)
            self._date = None
        
        def get_date(self):
            return self._date
        
        def set_date(self, date_obj):
            self._date = date_obj

from datetime import date, timedelta

from automotive_invoice_manager.ui.components.table_widget import EnhancedTableWidget


class AutocompleteCombobox(ttk.Combobox):
    """Combobox with basic substring filtering for large lists."""

    def __init__(self, master=None, **kwargs):
        values = kwargs.pop("values", [])
        super().__init__(master, values=values, **kwargs)
        self._all_values = list(values)
        # Reset values each time dropdown opens
        self.configure(postcommand=self._reset_values)
        self.bind("<KeyRelease>", self._on_keyrelease)

    def set_completion_list(self, values):
        self._all_values = list(values)
        self._reset_values()

    def _reset_values(self):
        self.configure(values=self._all_values)

    def _on_keyrelease(self, event):
        pattern = self.get().lower()
        filtered = [v for v in self._all_values if pattern in v.lower()]
        self.configure(values=filtered)


class InvoiceListFrame(ttk.Frame):
    """
    Frame showing a searchable, filterable, paginated list of invoices.
    """

    def __init__(self, parent, invoice_service, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.invoice_service = invoice_service
        self.current_page = 1
        self.per_page = 10
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self._build_widgets()
        self.load_data()

    def _build_widgets(self):
        # Search bar
        search_frame = ttk.Frame(self)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, padx=5)
        ttk.Label(search_frame, text="Status:").pack(side=tk.LEFT)
        statuses = ["All", "Draft", "Sent", "Paid", "Overdue"]
        ttk.Combobox(
            search_frame,
            textvariable=self.status_var,
            values=statuses,
            state="readonly",
        ).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="Filter", command=self.on_filter).pack(
            side=tk.LEFT, padx=5
        )
        search_frame.pack(fill=tk.X, pady=5)

        # Table
        columns = ("invoice_number", "customer", "issued_date", "status", "total")
        self.tree = EnhancedTableWidget(self, columns=columns)
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)

        # Pagination
        nav_frame = ttk.Frame(self)
        self.prev_btn = ttk.Button(nav_frame, text="<< Prev", command=self.on_prev)
        self.next_btn = ttk.Button(nav_frame, text="Next >>", command=self.on_next)
        self.page_label = ttk.Label(nav_frame, text=f"Page {self.current_page}")
        self.prev_btn.pack(side=tk.LEFT)
        self.page_label.pack(side=tk.LEFT, padx=10)
        self.next_btn.pack(side=tk.LEFT)
        nav_frame.pack(pady=5)

    def load_data(self):
        search = self.search_var.get()
        status = (
            self.status_var.get().lower()
            if self.status_var.get() and self.status_var.get() != "All"
            else None
        )
        items, total_pages = self.invoice_service.get_invoices(
            page=self.current_page, per_page=self.per_page, search=search, status=status
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

    def on_filter(self):
        self.current_page = 1
        self.load_data()

    def on_prev(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def on_next(self):
        if self.current_page < getattr(self, "total_pages", 1):
            self.current_page += 1
            self.load_data()

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        inv_number = self.tree.item(item, "values")[0]
        self.handle_open_detail(inv_number)

    def handle_open_detail(self, invoice_number):
        # To be bound by parent: open detail window
        pass


class InvoiceFormDialog(tk.Toplevel):
    """
    Dialog for creating/editing an invoice with dynamic line items.
    NOTE: This is the OLD version kept for compatibility with existing code.
    The NEW version is in automotive_invoice_manager/ui/invoices/invoice_form.py
    """

    def __init__(self, parent, invoice_service, user, customers=None, invoice=None):
        """FIXED: Now accepts user parameter and customers list."""
        super().__init__(parent)
        self.configure(bg=COLORS["dark_gray"])
        # Make dialog wider to fit more content
        self.geometry("800x600")
        self.invoice_service = invoice_service
        self.user = user
        self.customer_list = customers or []
        self.invoice = invoice
        self.line_items = []
        self.total_var = tk.StringVar(value="0.00")
        self._build_widgets()
        if invoice:
            self._populate_fields()

    def show(self):
        """Show dialog and return result (for compatibility)."""
        self.wait_window()
        return getattr(self, 'result', None)

    def _build_widgets(self):
        self.title("Invoice Form")
        # Customer selection
        ttk.Label(self, text="Customer:").grid(row=0, column=0, sticky=tk.W)
        names = [c.name for c in self.customer_list]
        self.customer_cb = AutocompleteCombobox(self, values=names)
        self.customer_cb.grid(row=0, column=1, sticky=tk.EW)

        # Dates
        ttk.Label(self, text="Issued Date:").grid(row=1, column=0, sticky=tk.W)
        self.issued_date = DateEntry(self)
        self.issued_date.grid(row=1, column=1, sticky=tk.EW)
        ttk.Label(self, text="Due Date:").grid(row=2, column=0, sticky=tk.W)
        self.due_date = DateEntry(self)
        self.due_date.grid(row=2, column=1, sticky=tk.EW)
        today = date.today()
        self.issued_date.set_date(today)
        self.due_date.set_date(today + timedelta(days=30))

        # Line items container
        self.items_frame = ttk.LabelFrame(self, text="Line Items")
        self.items_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW)

        # Total
        ttk.Label(self, text="Total:").grid(row=99, column=0, sticky=tk.E)
        ttk.Label(self, textvariable=self.total_var).grid(row=99, column=1, sticky=tk.W)

        # Buttons
        btn_frame = ttk.Frame(self)
        ttk.Button(btn_frame, text="Save", command=self.on_save).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Add Item", command=self._add_line).pack(
            side=tk.LEFT, padx=5
        )
        btn_frame.grid(row=100, column=0, columnspan=2, pady=10)

        self.columnconfigure(1, weight=1)

    def _add_line(self):
        frame = ttk.Frame(self.items_frame)

        ttk.Label(frame, text="Item").grid(row=0, column=0, padx=2)
        desc = ttk.Entry(frame)
        desc.grid(row=1, column=0, padx=2)

        ttk.Label(frame, text="Hours").grid(row=0, column=1, padx=2)
        hours = ttk.Spinbox(frame, from_=0.0, to=1000.0, increment=0.25, width=6)
        hours.grid(row=1, column=1, padx=2)

        ttk.Label(frame, text="Rate").grid(row=0, column=2, padx=2)
        rate = ttk.Spinbox(frame, from_=0.0, to=10000.0, increment=0.01, width=8)
        rate.grid(row=1, column=2, padx=2)

        ttk.Label(frame, text="Parts").grid(row=0, column=3, padx=2)
        parts = ttk.Spinbox(frame, from_=0.0, to=100000.0, increment=0.01, width=8)
        parts.grid(row=1, column=3, padx=2)

        ttk.Label(frame, text="Tax").grid(row=0, column=4, padx=2)
        tax = ttk.Spinbox(frame, from_=0.0, to=100.0, increment=0.01, width=6)
        tax.grid(row=1, column=4, padx=2)

        ttk.Button(
            frame, text="Remove", command=lambda f=frame: self._remove_line(f)
        ).grid(row=1, column=5, padx=2)

        frame.pack(fill=tk.X, pady=2)
        self.line_items.append((desc, hours, rate, parts, tax))
        for widget in (hours, rate, parts, tax):
            widget.bind("<<Increment>>", lambda e: self._recalculate_total())
            widget.bind("<KeyRelease>", lambda e: self._recalculate_total())
        self._recalculate_total()

    def _remove_line(self, frame):
        for widgets in frame.winfo_children():
            widgets.destroy()
        frame.destroy()
        # Rebuild internal list
        self.line_items = [li for li in self.line_items if li[0].winfo_exists()]
        self._recalculate_total()

    def _recalculate_total(self):
        total = 0
        for desc, hours, rate, parts, tax in self.line_items:
            try:
                base = float(hours.get()) * float(rate.get()) + float(parts.get())
                total += base * (1 + float(tax.get()) / 100)
            except ValueError:
                continue
        self.total_var.set(f"{total:.2f}")

    def _populate_fields(self):
        # Populate existing invoice data
        self.customer_cb.set(self.invoice.customer.name)
        self.issued_date.set_date(self.invoice.issued_date)
        self.due_date.set_date(self.invoice.due_date)
        # Populate line items
        for item in self.invoice.line_items:
            self._add_line()
            desc, hours, rate, parts, tax = self.line_items[-1]
            desc.insert(0, item.get("description", ""))
            hours.set(item.get("hours", item.get("quantity", 0)))
            rate.set(item.get("rate", 0))
            parts.set(item.get("parts", 0))
            tax.set(item.get("tax", 0))
        self._recalculate_total()

    def on_save(self):
        data = {
            "customer": self.customer_cb.get(),
            "issued_date": self.issued_date.get_date(),
            "due_date": self.due_date.get_date(),
            "line_items": [],
        }
        for desc, hours, rate, parts, tax in self.line_items:
            if desc.get():
                data["line_items"].append(
                    {
                        "description": desc.get(),
                        "hours": float(hours.get()),
                        "rate": float(rate.get()),
                        "parts": float(parts.get()),
                        "tax": float(tax.get()),
                    }
                )
        try:
            if self.invoice:
                self.invoice_service.update_invoice(self.invoice.id, data)
            else:
                self.invoice_service.create_invoice(self.user, data)  # FIXED: pass user
            self.master.event_generate("<<InvoiceUpdated>>")
            self.result = "saved"
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


class InvoiceDetailWindow(tk.Toplevel):
    """Display an invoice in read-only mode."""

    def __init__(self, parent, invoice_service, invoice_id, *, show_actions=True):
        super().__init__(parent)
        self.invoice_service = invoice_service
        self.invoice_id = invoice_id
        self.invoice = invoice_service.get_invoice(invoice_id)
        self.show_actions = show_actions
        self._build_widgets()

    def _build_widgets(self):
        self.title(f"Invoice {self.invoice.invoice_number}")
        # Display fields
        row = 0
        for field in [
            "invoice_number",
            "customer",
            "issued_date",
            "due_date",
            "status",
            "total",
        ]:
            ttk.Label(self, text=field.replace("_", " ").title() + ":").grid(
                row=row, column=0, sticky=tk.W
            )
            value = (
                getattr(self.invoice, field)
                if field != "customer"
                else self.invoice.customer.name
            )
            ttk.Label(self, text=value).grid(row=row, column=1, sticky=tk.W)
            row += 1
        # Line items
        items_frame = ttk.LabelFrame(self, text="Line Items")
        items_frame.grid(row=row, column=0, columnspan=2, pady=10)
        for item in self.invoice.line_items:
            hours = item.get("hours", item.get("quantity", 0))
            rate = item.get("rate", 0)
            parts = item.get("parts", 0)
            tax = item.get("tax", 0)
            text = (
                f"{item.get('description','')} - {hours}h @ {rate} + parts {parts}"
                f" (tax {tax}%)"
            )
            ttk.Label(items_frame, text=text).pack(anchor=tk.W)
        # Actions
        action_frame = ttk.Frame(self)
        ttk.Button(
            action_frame, text="Generate PDF", command=self.on_generate_pdf
        ).pack(side=tk.LEFT, padx=5)

        if self.show_actions:
            ttk.Button(action_frame, text="Edit", command=self.on_edit).pack(side=tk.LEFT)
            ttk.Button(action_frame, text="Delete", command=self.on_delete).pack(
                side=tk.LEFT, padx=5
            )
        else:
            ttk.Button(action_frame, text="Close", command=self.destroy).pack(side=tk.LEFT)

        action_frame.grid(row=row + 1, column=0, columnspan=2, pady=10)

    def on_generate_pdf(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save PDF as...",
        )
        if not path:
            return
        try:
            saved = self.invoice_service.generate_pdf(self.invoice_id, path)
            messagebox.showinfo("PDF Generated", f"Saved to {saved}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_edit(self):
        """FIXED: Check if parent has the required attributes and user info."""
        if hasattr(self.master, 'open_invoice_form'):
            self.master.open_invoice_form(self.invoice)
        elif hasattr(self.master, 'user') and hasattr(self.master, 'customer_service'):
            # Try to create the form directly
            try:
                from automotive_invoice_manager.ui.invoices.invoice_form import InvoiceFormDialog
                customers = self.master.customer_service.get_all_customers(self.master.user.id)
                dialog = InvoiceFormDialog(
                    self, 
                    self.invoice_service, 
                    self.master.user,
                    customers, 
                    self.invoice
                )
                result = dialog.show()
                if result:
                    messagebox.showinfo("Success", "Invoice updated successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to edit invoice: {e}")
        else:
            messagebox.showinfo("Info", "Edit functionality not available in this context")
        
        self.destroy()

    def on_delete(self):
        if messagebox.askyesno(
            "Confirm", "Delete this invoice? This cannot be undone."
        ):
            try:
                self.invoice_service.delete_invoice(self.invoice_id)
                self.master.event_generate("<<InvoiceDeleted>>")
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))