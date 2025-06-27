import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry

from automotive_invoice_manager.ui.components.table_widget import EnhancedTableWidget
import jinja2
import os
import platform
import subprocess
import tempfile
import weasyprint

from automotive_invoice_manager.utils import pdf_generator


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
    """

    def __init__(self, parent, invoice_service, customer_list, invoice=None):
        super().__init__(parent)
        self.invoice_service = invoice_service
        self.customer_list = customer_list
        self.invoice = invoice
        self.line_items = []
        self.total_var = tk.StringVar(value="0.00")
        self._build_widgets()
        if invoice:
            self._populate_fields()

    def _build_widgets(self):
        self.title("Invoice Form")
        # Customer selection
        ttk.Label(self, text="Customer:").grid(row=0, column=0, sticky=tk.W)
        self.customer_cb = ttk.Combobox(
            self, values=[c.name for c in self.customer_list], state="readonly"
        )
        self.customer_cb.grid(row=0, column=1, sticky=tk.EW)

        # Dates
        ttk.Label(self, text="Issued Date:").grid(row=1, column=0, sticky=tk.W)
        self.issued_date = DateEntry(self)
        self.issued_date.grid(row=1, column=1, sticky=tk.EW)
        ttk.Label(self, text="Due Date:").grid(row=2, column=0, sticky=tk.W)
        self.due_date = DateEntry(self)
        self.due_date.grid(row=2, column=1, sticky=tk.EW)

        # Line items header
        self.items_frame = ttk.LabelFrame(self, text="Line Items")
        self.items_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW)
        ttk.Button(self.items_frame, text="Add Item", command=self._add_line).pack(
            anchor=tk.W, pady=2
        )

        # Total
        ttk.Label(self, text="Total:").grid(row=99, column=0, sticky=tk.E)
        ttk.Label(self, textvariable=self.total_var).grid(row=99, column=1, sticky=tk.W)

        # Buttons
        btn_frame = ttk.Frame(self)
        ttk.Button(btn_frame, text="Save", command=self.on_save).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT)
        btn_frame.grid(row=100, column=0, columnspan=2, pady=10)

        self.columnconfigure(1, weight=1)

    def _add_line(self):
        frame = ttk.Frame(self.items_frame)
        desc = ttk.Entry(frame)
        desc.grid(row=0, column=0)
        qty = ttk.Spinbox(frame, from_=0, to=100)
        qty.grid(row=0, column=1)
        rate = ttk.Spinbox(frame, from_=0.0, to=10000.0, increment=0.01)
        rate.grid(row=0, column=2)
        ttk.Button(
            frame, text="Remove", command=lambda f=frame: self._remove_line(f)
        ).grid(row=0, column=3)
        frame.pack(fill=tk.X, pady=2)
        self.line_items.append((desc, qty, rate))
        for widget in (qty, rate):
            widget.bind("<<Increment>>", lambda e: self._recalculate_total())
            widget.bind("<KeyRelease>", lambda e: self._recalculate_total())
        self._recalculate_total()

    def _remove_line(self, frame):
        for widgets in frame.winfo_children():
            widgets.destroy()
        frame.destroy()
        self.line_items = [li for li in self.line_items if li[0].winfo_ismapped()]
        self._recalculate_total()

    def _recalculate_total(self):
        total = 0
        for desc, qty, rate in self.line_items:
            try:
                total += float(qty.get()) * float(rate.get())
            except ValueError:
                continue
        self.total_var.set(f"{total:.2f}")

    def _populate_fields(self):
        self.customer_cb.set(self.invoice.customer.name)
        self.issued_date.set_date(self.invoice.issued_date)
        self.due_date.set_date(self.invoice.due_date)
        for item in self.invoice.line_items:
            self._add_line()
            desc, qty, rate = self.line_items[-1]
            desc.insert(0, item["description"])
            qty.set(item["quantity"])
            rate.set(item["rate"])
        self._recalculate_total()

    def on_save(self):
        data = {
            "customer": self.customer_cb.get(),
            "issued_date": self.issued_date.get_date(),
            "due_date": self.due_date.get_date(),
            "line_items": [],
        }
        for desc, qty, rate in self.line_items:
            if desc.get():
                data["line_items"].append(
                    {
                        "description": desc.get(),
                        "quantity": float(qty.get()),
                        "rate": float(rate.get()),
                    }
                )
        try:
            if self.invoice:
                self.invoice_service.update_invoice(self.invoice.id, data)
            else:
                self.invoice_service.create_invoice(data)
            self.master.event_generate("<<InvoiceUpdated>>")
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
        items_frame = ttk.LabelFrame(self, text="Line Items")
        items_frame.grid(row=row, column=0, columnspan=2, pady=10)
        for item in self.invoice.line_items:
            ttk.Label(
                items_frame,
                text=f"{item['description']} x{item['quantity']} @{item['rate']}",
            ).pack(anchor=tk.W)
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
        dialog = PDFGenerationDialog(self, self.invoice_service, self.invoice_id)
        self.wait_window(dialog)

    def on_edit(self):
        self.master.open_invoice_form(self.invoice)
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


class PDFGenerationDialog(tk.Toplevel):
    """
    Dialog to generate (and optionally preview/print) a PDF from HTML templates via WeasyPrint.
    """

    def __init__(self, parent, invoice_service, invoice_id):
        super().__init__(parent)
        self.invoice_service = invoice_service
        self.invoice_id = invoice_id
        self.invoice = invoice_service.get_invoice(invoice_id)
        self.templates = ["standard", "modern", "minimal"]
        self.template_var = tk.StringVar(value=self.invoice.template)
        self.output_path = None
        self._build_widgets()

    def _build_widgets(self):
        self.title("Generate PDF")
        ttk.Label(self, text="Template:").grid(row=0, column=0, sticky=tk.W)
        ttk.Combobox(
            self,
            textvariable=self.template_var,
            values=self.templates,
            state="readonly",
        ).grid(row=0, column=1, sticky=tk.EW)

        ttk.Label(self, text="Output File:").grid(row=1, column=0, sticky=tk.W)
        path_entry = ttk.Entry(self, state="readonly")
        path_entry.grid(row=1, column=1, sticky=tk.EW)
        ttk.Button(
            self, text="Browse…", command=lambda: self._select_output(path_entry)
        ).grid(row=1, column=2)

        btn_frame = ttk.Frame(self)
        ttk.Button(btn_frame, text="Generate", command=self._generate).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Preview", command=self._preview).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Print", command=self._print).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=10)

        self.columnconfigure(1, weight=1)

    def _select_output(self, entry_widget):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save PDF as…",
        )
        if path:
            self.output_path = path
            entry_widget.config(state="normal")
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, path)
            entry_widget.config(state="readonly")

    def _render_html(self):
        return pdf_generator.render_invoice_html(self.invoice, self.template_var.get())

    def _generate(self):
        if not self.output_path:
            messagebox.showerror("Error", "Please select an output file first.")
            return
        try:
            pdf_generator.generate_pdf(
                self.invoice, self.template_var.get(), self.output_path
            )
            messagebox.showinfo("Success", f"PDF saved to {self.output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _preview(self):
        # Generate to temp file and open with default system viewer
        try:
            temp_fd, temp_path = tempfile.mkstemp(suffix=".pdf")
            os.close(temp_fd)
            pdf_generator.generate_pdf(self.invoice, self.template_var.get(), temp_path)
            if platform.system() == "Windows":
                os.startfile(temp_path)
            elif platform.system() == "Darwin":
                subprocess.call(("open", temp_path))
            else:
                subprocess.call(("xdg-open", temp_path))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _print(self):
        if not self.output_path:
            # generate to temp if not yet generated
            fd, self.output_path = tempfile.mkstemp(suffix=".pdf")
            os.close(fd)

        pdf_generator.generate_pdf(
            self.invoice, self.template_var.get(), self.output_path
        )
        try:
            if platform.system() == "Windows":
                os.startfile(self.output_path, "print")
            else:
                subprocess.call(["lp", self.output_path])
            messagebox.showinfo("Print", "Sent to printer.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
