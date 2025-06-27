# automotive_invoice_manager/ui/main_interface.py - UPDATED WITH LOGO AND HELP TABS

import tkinter as tk
from tkinter import ttk, messagebox
from automotive_invoice_manager.ui.popout_tabs import PopoutNotebook
from automotive_invoice_manager.ui.tooltips import add_tooltip
import logging
from typing import Optional

from automotive_invoice_manager.ui.theme import COLORS, FONTS

logger = logging.getLogger(__name__)


class TabbedMainInterface:
    """Main interface with working tab colors and Logo/Help tabs."""
    
    def __init__(self, parent_app, root, user, services):
        self.parent_app = parent_app
        self.root = root
        self.user = user
        self.customer_service = services['customer_service']
        self.invoice_service = services['invoice_service']
        self.auth_service = services['auth_service']
        
        # Tab references
        self.tabs = {}
        self.current_tab = None
        
        # Use parent app's status_var if it exists
        self.status_var = getattr(parent_app, 'status_var', tk.StringVar(value="Ready"))
        
        self.setup_interface()
        
    def setup_interface(self):
        """Setup the main tabbed interface."""
        # Main container - matches your existing styling
        self.main_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section - preserve your existing header style
        self.create_header()
        
        # CRITICAL: Setup theme and styles BEFORE creating notebook
        self.setup_working_tab_styling()
        
        # Notebook widget for tabs - use PopoutNotebook to allow detaching
        self.notebook = PopoutNotebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        # Create tabs
        self.create_tabs()
        
        # Bind notebook events
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    def setup_working_tab_styling(self):
        """Setup tab styling that actually works."""
        style = ttk.Style()
        
        # CRITICAL: Switch to 'clam' theme which allows custom tab colors
        style.theme_use('clam')
        print(f"Switched to theme: {style.theme_use()}")
        
        # Configure the notebook container
        style.configure(
            'TNotebook', 
            background=COLORS['background'],
            borderwidth=1,
            tabmargins=[2, 5, 2, 0]
        )
        
        # Configure tab styling - this will now work!
        style.configure(
            'TNotebook.Tab',
            padding=[20, 12, 20, 12],        # left, top, right, bottom padding
            background=COLORS['secondary'],   # Default tab background
            foreground='white',              # Tab text color
            font=FONTS['base'],              # Tab font
            borderwidth=1,
            focuscolor='none',
            lightcolor=COLORS['secondary'],
            darkcolor=COLORS['secondary']
        )
        
        # Configure tab states (hover, selected, etc.)
        style.map(
            'TNotebook.Tab',
            background=[
                ('selected', COLORS['primary']),     # Selected tab - dark blue
                ('active', COLORS['highlight']),     # Hovered tab - medium gray
                ('!active', COLORS['secondary'])     # Normal tab - medium blue
            ],
            foreground=[
                ('selected', 'white'),               # Selected tab text
                ('active', 'white'),                 # Hovered tab text
                ('!active', 'white')                 # Normal tab text
            ],
            lightcolor=[
                ('selected', COLORS['primary']),
                ('!selected', COLORS['secondary'])
            ],
            darkcolor=[
                ('selected', COLORS['primary']),
                ('!selected', COLORS['secondary'])
            ]
        )
        
        print("Applied tab styling successfully!")
        
    def create_header(self):
        """Create header that matches your existing app styling."""
        # Header frame - same styling as your existing app
        header_frame = tk.Frame(self.main_frame, bg=COLORS["primary"], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg=COLORS["primary"]) 
        header_content.pack(fill=tk.BOTH, padx=20, pady=10)
        
        # App title - same as your existing app
        title_label = tk.Label(
            header_content,
            text="Invoice Manager",
            font=FONTS["xl"],
            fg="white",
            bg=COLORS["primary"],
        )
        title_label.pack(side=tk.LEFT)
        
        # User info and logout - same as your existing app
        user_frame = tk.Frame(header_content, bg=COLORS["primary"])
        user_frame.pack(side=tk.RIGHT)
        
        user_label = tk.Label(
            user_frame,
            text=f"Welcome, {self.user.email}",
            font=FONTS["base"],
            fg="white",
            bg=COLORS["primary"],
        )
        user_label.pack(side=tk.LEFT, padx=(0, 20))
        
        logout_btn = tk.Button(
            user_frame,
            text="Logout",
            command=self.logout,
            font=FONTS["sm"],
            bg=COLORS["secondary"],
            fg="white",
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2',
        )
        logout_btn.pack(side=tk.RIGHT)
        add_tooltip(logout_btn, "Logout of the application")
        
    def create_tabs(self):
        """Instantiate and add all primary tabs with proper error handling."""
        try:
            from automotive_invoice_manager.ui.dashboard_view import DashboardView
            from automotive_invoice_manager.ui.customer_tab import CustomerTab  
            from automotive_invoice_manager.ui.invoice_tab import InvoiceTab
            from automotive_invoice_manager.ui.logo_tab import LogoTab
            from automotive_invoice_manager.ui.help_tab import HelpTab

            # Create dashboard tab with error handling
            try:
                self.dashboard_tab = DashboardView(self.notebook, self)
                self.notebook.add(self.dashboard_tab, text="📊 Dashboard")
                self.tabs["dashboard"] = self.dashboard_tab
                print("Dashboard tab created successfully")
            except Exception as e:
                logger.error(f"Error creating dashboard tab: {e}")
                self.create_fallback_dashboard_tab()

            # Create customer tab
            try:
                self.customer_tab = CustomerTab(self.notebook, self)
                self.notebook.add(self.customer_tab, text="👥 Customers")
                self.tabs["customers"] = self.customer_tab
                print("Customer tab created successfully")
            except Exception as e:
                logger.error(f"Error creating customer tab: {e}")
                self.create_fallback_tab("customers", "👥 Customers")

            # Create invoice tab
            try:
                self.invoice_tab = InvoiceTab(self.notebook, self)
                self.notebook.add(self.invoice_tab, text="📄 Invoices")
                self.tabs["invoices"] = self.invoice_tab
                print("Invoice tab created successfully")
            except Exception as e:
                logger.error(f"Error creating invoice tab: {e}")
                self.create_fallback_tab("invoices", "📄 Invoices")

            # Create reports tab
            self.create_reports_tab()
            
            # NEW: Create logo tab
            try:
                self.logo_tab = LogoTab(self.notebook, self)
                self.notebook.add(self.logo_tab, text="🎨 Logo")
                self.tabs["logo"] = self.logo_tab
                print("Logo tab created successfully")
            except Exception as e:
                logger.error(f"Error creating logo tab: {e}")
                self.create_fallback_tab("logo", "🎨 Logo")
            
            # NEW: Create help tab
            try:
                self.help_tab = HelpTab(self.notebook, self)
                self.notebook.add(self.help_tab, text="📚 Help")
                self.tabs["help"] = self.help_tab
                print("Help tab created successfully")
            except Exception as e:
                logger.error(f"Error creating help tab: {e}")
                self.create_fallback_tab("help", "📚 Help")
            
            print(f"Created {len(self.tabs)} tabs with working colors!")
            
        except ImportError as e:
            logger.error(f"Import error creating tabs: {e}")
            self.create_basic_tabs()

    def create_fallback_dashboard_tab(self):
        """Create a basic dashboard tab if the main one fails."""
        dashboard_frame = tk.Frame(self.notebook, bg=COLORS['background'])
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        self.tabs['dashboard'] = dashboard_frame
        
        # Basic dashboard content
        tk.Label(
            dashboard_frame,
            text="Dashboard (Basic Mode)",
            font=FONTS['lg'],
            fg=COLORS['text'],
            bg=COLORS['background'],
        ).pack(pady=20)
        
        tk.Label(
            dashboard_frame,
            text="Dashboard is running in basic mode due to a loading error.\nCheck the console for details.",
            font=FONTS['base'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            justify=tk.CENTER
        ).pack(expand=True)

    def create_fallback_tab(self, tab_id, tab_name):
        """Create a fallback tab for when the main tab fails to load."""
        tab_frame = tk.Frame(self.notebook, bg=COLORS['background'])
        self.notebook.add(tab_frame, text=tab_name)
        self.tabs[tab_id] = tab_frame
        
        tk.Label(
            tab_frame,
            text=f"{tab_name} (Basic Mode)",
            font=FONTS['lg'],
            fg=COLORS['text'],
            bg=COLORS['background'],
        ).pack(pady=20)
        
        tk.Label(
            tab_frame,
            text=f"{tab_name} tab is running in basic mode due to a loading error.\nCheck the console for details.",
            font=FONTS['base'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            justify=tk.CENTER
        ).pack(expand=True)
        
    def create_reports_tab(self):
        """Create reports tab."""
        reports_frame = tk.Frame(self.notebook, bg=COLORS['background'])
        self.notebook.add(reports_frame, text="📊 Reports")
        self.tabs['reports'] = reports_frame
        
        # Reports header
        header_label = tk.Label(
            reports_frame,
            text="Reports & Analytics",
            font=FONTS['lg'],
            fg=COLORS['text'],
            bg=COLORS['background'],
        )
        header_label.pack(anchor=tk.W, padx=20, pady=(20, 20))
        
        # Placeholder content
        tk.Label(
            reports_frame,
            text="📈 Reports functionality coming soon...\n\n"
                 "Future features will include:\n"
                 "• Customer revenue reports\n"
                 "• Invoice status summaries\n" 
                 "• Monthly/yearly analytics\n"
                 "• Payment tracking\n"
                 "• Tax reporting\n"
                 "• Data exports",
            font=FONTS['base'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            justify=tk.LEFT
        ).pack(expand=True, padx=40, pady=40)

    def on_tab_changed(self, event):
        """Handle tab change events with proper error handling."""
        try:
            selection = event.widget.select()
            tab_text = event.widget.tab(selection, "text")
            self.current_tab = tab_text.lower()
            self.status_var.set(f"Viewing {tab_text}")
            
            # Refresh data when switching to specific tabs
            if self.current_tab == "customers":
                self.refresh_customers()
            elif self.current_tab == "dashboard":
                self.load_dashboard_data()
        except Exception as e:
            logger.error(f"Error in tab change: {e}")
            self.status_var.set("Error switching tabs")
    
    # Event handlers with defensive programming
    def new_customer(self):
        """Create a new customer using your existing dialog."""
        try:
            from automotive_invoice_manager.ui.customers.customer_form import CustomerFormDialog
            dialog = CustomerFormDialog(
                self.root, 
                self.customer_service, 
                self.user
            )
            result = dialog.show()
            
            if result:
                self.status_var.set("Customer created successfully")
                self.refresh_customers()
            return
        except Exception as e:
            logger.error(f"Error with CustomerFormDialog: {e}")
        
        # Fallback: simple dialog
        from tkinter import simpledialog
        name = simpledialog.askstring("New Customer", "Enter customer name:")
        if name:
            try:
                customer_data = {'name': name.strip()}
                customer = self.customer_service.create_customer(customer_data, self.user.id)
                if customer:
                    messagebox.showinfo("Success", "Customer created successfully!")
                    self.refresh_customers()
                else:
                    messagebox.showerror("Error", "Failed to create customer")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create customer: {e}")
    
    def new_invoice(self):
        """Create a new invoice using the fixed invoice form dialog."""
        try:
            # Get customers first
            customers = self.customer_service.get_all_customers(self.user.id)
            
            if not customers:
                result = messagebox.askyesno(
                    "No Customers", 
                    "You need at least one customer to create an invoice.\n\nWould you like to create a customer first?"
                )
                if result:
                    self.new_customer()
                return
            
            # Import the correct invoice form
            from automotive_invoice_manager.ui.invoices.invoice_form import InvoiceFormDialog
            
            # Create dialog with correct parameters: parent, invoice_service, user, customers
            dialog = InvoiceFormDialog(
                self.root,
                self.invoice_service,
                self.user,
                customers
            )
            
            result = dialog.show()
            
            if result:
                self.status_var.set("Invoice created successfully")
                # Refresh invoice tab if it exists
                invoice_tab = self.tabs.get("invoices")
                if invoice_tab and hasattr(invoice_tab, "load_data"):
                    invoice_tab.load_data()
                elif invoice_tab and hasattr(invoice_tab, "inner") and invoice_tab.inner:
                    if hasattr(invoice_tab.inner, "load_data"):
                        invoice_tab.inner.load_data()
                
                # Refresh dashboard
                self.load_dashboard_data()

        except ImportError as e:
            logger.error(f"Error importing invoice form: {e}")
            messagebox.showerror("Error", "Invoice form is not available. Please check your installation.")
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            messagebox.showerror("Error", f"Failed to create invoice: {e}")
    
    def refresh_customers(self):
        """Refresh customer data safely with defensive programming."""
        try:
            if 'customers' in self.tabs and hasattr(self.tabs['customers'], 'refresh_data'):
                try:
                    self.tabs['customers'].refresh_data(callback=self.load_dashboard_data)
                except TypeError:
                    # Fallback if callback not supported
                    self.tabs['customers'].refresh_data()
                    self.load_dashboard_data()
            else:
                self.load_dashboard_data()
            self.status_var.set("Customer data refreshed")
        except Exception as e:
            logger.error(f"Error refreshing customers: {e}")
            self.status_var.set("Error refreshing customers")
    
    def load_dashboard_data(self):
        """Load dashboard statistics with proper error handling."""
        try:
            # Check if we have a dashboard tab and it has the required method
            if hasattr(self, "dashboard_tab"):
                if hasattr(self.dashboard_tab, "load_dashboard_stats"):
                    self.dashboard_tab.load_dashboard_stats()
                    self.status_var.set("Dashboard loaded")
                else:
                    logger.warning("Dashboard tab exists but load_dashboard_stats method not found")
                    self.status_var.set("Dashboard loaded (basic mode)")
            else:
                logger.warning("Dashboard tab not found")
                self.status_var.set("Dashboard not available")
                
        except Exception as e:
            logger.error(f"Error loading dashboard data: {e}")
            self.status_var.set("Error loading dashboard")
    
    def logout(self):
        """Handle user logout - delegates to parent app."""
        try:
            self.parent_app.handle_logout()
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            # Fallback: just show login interface
            if hasattr(self.parent_app, 'show_login_interface'):
                self.parent_app.show_login_interface()