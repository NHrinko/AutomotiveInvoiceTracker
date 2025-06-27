# automotive_invoice_manager/ui/help_tab.py - Comprehensive Help Tab

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import logging

from .theme import COLORS, FONTS
from .tooltips import add_tooltip

logger = logging.getLogger(__name__)


class HelpTab(tk.Frame):
    """Comprehensive help tab with step-by-step instructions."""

    def __init__(self, parent, main_interface):
        super().__init__(parent, bg=COLORS["background"])
        self.main_interface = main_interface
        
        self.setup_ui()

    def setup_ui(self):
        """Setup the help interface."""
        # Header
        header_frame = tk.Frame(self, bg=COLORS["background"])
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        header_label = tk.Label(
            header_frame,
            text="📚 Help & User Guide",
            font=FONTS["lg"],
            fg=COLORS["text"],
            bg=COLORS["background"],
        )
        header_label.pack(side=tk.LEFT)

        # Quick action buttons
        self.create_quick_actions(header_frame)

        # Main content with notebook for different sections
        self.create_help_notebook()

    def create_quick_actions(self, parent):
        """Create responsive quick action buttons."""
        actions_frame = tk.Frame(parent, bg=COLORS["background"])
        actions_frame.pack(side=tk.RIGHT, padx=5)

        # Configure for responsive button layout
        actions_frame.columnconfigure((0, 1, 2), weight=1)

        # Quick start button
        quick_start_btn = tk.Button(
            actions_frame,
            text="🚀 Quick\nStart",
            command=self.show_quick_start,
            font=('Arial', 9, 'bold'),
            bg=COLORS["primary"],
            fg="white",
            relief="flat",
            padx=10,
            pady=8,
            cursor="hand2",
            wraplength=60,
            justify=tk.CENTER
        )
        quick_start_btn.grid(row=0, column=0, padx=2, sticky="ew")
        add_tooltip(quick_start_btn, "Show quick start guide")

        # Video tutorials button (placeholder)
        video_btn = tk.Button(
            actions_frame,
            text="🎥 Video\nGuide",
            command=self.show_video_guide,
            font=('Arial', 9, 'bold'),
            bg=COLORS["secondary"],
            fg="white",
            relief="flat",
            padx=10,
            pady=8,
            cursor="hand2",
            wraplength=60,
            justify=tk.CENTER
        )
        video_btn.grid(row=0, column=1, padx=2, sticky="ew")
        add_tooltip(video_btn, "Video tutorials (coming soon)")

        # FAQ button
        faq_btn = tk.Button(
            actions_frame,
            text="❓ FAQ",
            command=self.show_faq,
            font=('Arial', 9, 'bold'),
            bg=COLORS["highlight"],
            fg="white",
            relief="flat",
            padx=10,
            pady=8,
            cursor="hand2",
            wraplength=60,
            justify=tk.CENTER
        )
        faq_btn.grid(row=0, column=2, padx=2, sticky="ew")
        add_tooltip(faq_btn, "Frequently asked questions")

    def create_help_notebook(self):
        """Create tabbed help content."""
        # Create notebook for different help sections
        self.help_notebook = ttk.Notebook(self)
        self.help_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Create different help sections
        self.create_getting_started_tab()
        self.create_customers_help_tab()
        self.create_invoices_help_tab()
        self.create_dashboard_help_tab()
        self.create_troubleshooting_tab()
        self.create_keyboard_shortcuts_tab()

    def create_getting_started_tab(self):
        """Create getting started help tab."""
        tab_frame = ttk.Frame(self.help_notebook)
        self.help_notebook.add(tab_frame, text="🚀 Getting Started")

        content = self.create_scrollable_content(tab_frame)
        
        getting_started_text = """
GETTING STARTED WITH INVOICE MANAGER

Welcome to Invoice Manager! This guide will help you get up and running quickly.

═══════════════════════════════════════════════════════════════════

STEP 1: FIRST LOGIN
═══════════════════════════════════════════════════════════════════

1. When you first open the application, you'll see the login screen
2. If this is your first time:
   • Click "Create Account" 
   • Enter your email address
   • Create a secure password (8+ characters with letters and numbers)
   • Click "CREATE ACCOUNT"
3. For future logins:
   • Enter your email and password
   • Click "Sign In" or press Enter

TIP: Use the "👁" button to show/hide your password while typing.

═══════════════════════════════════════════════════════════════════

STEP 2: DASHBOARD OVERVIEW
═══════════════════════════════════════════════════════════════════

After logging in, you'll see the Dashboard with:

📊 STATISTICS CARDS:
   • Total Customers - How many customers you have
   • Total Invoices - How many invoices you've created
   • Pending Invoices - Invoices awaiting payment
   • Overdue Invoices - Invoices past due date

🎯 QUICK ACTIONS:
   • New Customer - Add a customer instantly
   • New Invoice - Create an invoice quickly
   • Refresh - Update all statistics

═══════════════════════════════════════════════════════════════════

STEP 3: YOUR FIRST CUSTOMER
═══════════════════════════════════════════════════════════════════

Before creating invoices, you need customers:

1. Click the "Customers" tab
2. Click "New Customer" button
3. Fill in customer information:
   • Name (required) - Customer or company name
   • Email (optional) - For sending invoices
   • Phone (optional) - Contact number
   • Address (optional) - Billing address
   • Notes (optional) - Any special notes
4. Click "Create Customer"

BEST PRACTICES:
✓ Always fill in at least name and email
✓ Use consistent naming (e.g., "ABC Company" not "abc co")
✓ Include phone numbers for important customers
✓ Use notes for special payment terms or preferences

═══════════════════════════════════════════════════════════════════

STEP 4: YOUR FIRST INVOICE
═══════════════════════════════════════════════════════════════════

Now create your first invoice:

1. Click the "Invoices" tab
2. Click "New Invoice" button
3. Fill in invoice details:
   • Customer - Select from dropdown
   • Invoice # - Auto-generated or custom
   • Issued Date - When invoice is created
   • Due Date - When payment is due
   • Status - Draft, Sent, Paid, or Overdue

4. Add line items:
   • Description - What you're billing for
   • Hours - Time spent (can use decimals like 2.5)
   • Rate - Hourly rate or fixed amount
   • Parts - Cost of parts/materials
   • Tax % - Tax percentage (e.g., 8.5 for 8.5%)

5. Review the auto-calculated total
6. Click "Create Invoice"

CALCULATION EXAMPLE:
Description: "Oil Change Service"
Hours: 1.0
Rate: $75.00
Parts: $25.00
Tax: 8.5%
Total: (1.0 × $75.00 + $25.00) × 1.085 = $108.50

═══════════════════════════════════════════════════════════════════

STEP 5: MANAGING YOUR DATA
═══════════════════════════════════════════════════════════════════

🔍 SEARCHING:
   • Use search boxes to find customers or invoices quickly
   • Search works on names, emails, phone numbers, and invoice numbers
   • Search is case-insensitive

📋 SORTING:
   • Click column headers in tables to sort
   • Click again to reverse sort order

📊 FILTERING:
   • Use status dropdowns to filter invoices by status
   • "All" shows everything

🔄 REFRESHING:
   • Click refresh buttons to update data
   • Data refreshes automatically when you make changes

═══════════════════════════════════════════════════════════════════

STEP 6: GENERATING PDFS
═══════════════════════════════════════════════════════════════════

To create PDF invoices:

1. Go to Invoices tab
2. Double-click an invoice to open details
3. Click "Generate PDF"
4. Choose save location
5. PDF is created instantly!

PDF FEATURES:
✓ Professional formatting
✓ Company logo (if uploaded in Logo tab)
✓ All invoice details and line items
✓ Automatic calculations
✓ Print-ready format

═══════════════════════════════════════════════════════════════════

STEP 7: CUSTOMIZING YOUR EXPERIENCE
═══════════════════════════════════════════════════════════════════

🎨 LOGO TAB:
   • Upload your company logo
   • Appears on login screen and PDFs
   • Supports PNG, JPG, and other formats

⌨️ KEYBOARD SHORTCUTS:
   • F5 - Refresh current tab
   • Ctrl+F - Focus search box
   • Enter - Default action (save, login, etc.)
   • Escape - Cancel/close dialogs

🔒 LOGOUT:
   • Click "Logout" in top-right corner
   • Secure logout protects your data

═══════════════════════════════════════════════════════════════════

NEXT STEPS
═══════════════════════════════════════════════════════════════════

Now you're ready to:
✓ Add more customers
✓ Create professional invoices
✓ Track payments and overdue accounts
✓ Generate PDFs for your clients
✓ Customize with your company logo

Need more help? Check the other help tabs for detailed information!
        """
        
        self.insert_formatted_text(content, getting_started_text)

    def create_customers_help_tab(self):
        """Create customers help tab."""
        tab_frame = ttk.Frame(self.help_notebook)
        self.help_notebook.add(tab_frame, text="👥 Customers")

        content = self.create_scrollable_content(tab_frame)
        
        customers_text = """
CUSTOMER MANAGEMENT GUIDE

Everything you need to know about managing customers effectively.

═══════════════════════════════════════════════════════════════════

CREATING CUSTOMERS
═══════════════════════════════════════════════════════════════════

📝 BASIC INFORMATION:
   • Name (Required) - Customer or company name
   • Email (Optional) - Primary contact email
   • Phone (Optional) - Contact phone number
   • Address (Optional) - Full billing address
   • Notes (Optional) - Special instructions or notes

💡 BEST PRACTICES:
   ✓ Use consistent naming conventions
   ✓ Include email addresses for electronic invoicing
   ✓ Add complete addresses for professional invoices
   ✓ Use notes for payment terms, preferences, or special instructions

🚨 REQUIRED FIELDS:
   • Only "Name" is required
   • All other fields are optional but recommended

═══════════════════════════════════════════════════════════════════

CUSTOMER LIST FEATURES
═══════════════════════════════════════════════════════════════════

🔍 SEARCH FUNCTIONALITY:
   • Real-time search as you type
   • Searches: names, emails, phone numbers, notes
   • Case-insensitive (finds "JOHN" when you type "john")
   • Partial matches work ("ABC" finds "ABC Company")

📊 CUSTOMER STATISTICS:
   • Invoice Count - Total invoices for each customer
   • Total Billed - Sum of all invoice amounts
   • Created Date - When customer was added

🔄 SORTING OPTIONS:
   • Click column headers to sort
   • Available sorts: Name, Email, Phone, Invoices, Total Billed, Created
   • Click again to reverse order

⚡ QUICK ACTIONS:
   • Double-click customer to edit
   • Right-click for context menu:
     - Edit Customer
     - View Invoices
     - New Invoice
     - Delete Customer

═══════════════════════════════════════════════════════════════════

EDITING CUSTOMERS
═══════════════════════════════════════════════════════════════════

✏️ TO EDIT A CUSTOMER:
1. Go to Customers tab
2. Double-click the customer in the list
   OR click customer and press Enter
   OR right-click and select "Edit Customer"
3. Make your changes
4. Click "Update Customer"

📈 CUSTOMER STATISTICS (shown in edit dialog):
   • Total Invoices - Number of invoices created
   • Total Billed - Sum of all invoice amounts  
   • Customer Since - Date customer was added

⚠️ VALIDATION:
   • Name cannot be empty
   • Email must be valid format (if provided)
   • Phone number format is flexible
   • Real-time validation shows errors immediately

═══════════════════════════════════════════════════════════════════

DELETING CUSTOMERS
═══════════════════════════════════════════════════════════════════

🗑️ DELETION RULES:
   • Can only delete customers with NO invoices
   • This protects your financial records
   • If customer has invoices, deletion is blocked

📋 TO DELETE A CUSTOMER:
1. Make sure customer has no invoices
2. Edit the customer
3. Click "Delete Customer"
4. Confirm deletion
5. Customer is permanently removed

🔒 PROTECTION MEASURES:
   • Confirmation dialog prevents accidental deletion
   • Customers with invoices cannot be deleted
   • This maintains data integrity

═══════════════════════════════════════════════════════════════════

CUSTOMER-INVOICE INTEGRATION
═══════════════════════════════════════════════════════════════════

🔗 CREATING INVOICES FOR CUSTOMERS:
   • Right-click customer → "New Invoice"
   • Customer is pre-selected in invoice form
   • Saves time and prevents errors

📊 VIEWING CUSTOMER INVOICES:
   • Right-click customer → "View Invoices"
   • Automatically filters invoice list
   • Shows all invoices for that customer

💰 CUSTOMER FINANCIAL OVERVIEW:
   • See total amounts billed per customer
   • Track which customers generate most revenue
   • Identify your best customers

═══════════════════════════════════════════════════════════════════

CUSTOMER DATA BEST PRACTICES
═══════════════════════════════════════════════════════════════════

📝 NAMING CONVENTIONS:
   ✓ "ABC Company Inc." (consistent business suffixes)
   ✓ "Smith, John" (last name first for individuals)
   ✓ "City Auto Repair" (descriptive names)
   ✗ "abc co" (inconsistent capitalization)
   ✗ "Customer #1" (non-descriptive names)

📧 EMAIL GUIDELINES:
   ✓ Use primary business contact email
   ✓ Keep emails updated
   ✓ Verify email addresses are correct
   ✗ Don't use personal emails for businesses

📞 PHONE NUMBER TIPS:
   ✓ Include area codes: "(555) 123-4567"
   ✓ Use consistent formatting
   ✓ Include extensions: "(555) 123-4567 ext 101"
   ✓ International: "+1 (555) 123-4567"

📍 ADDRESS FORMATTING:
   ✓ Complete addresses for professional invoices
   ✓ Include ZIP/postal codes
   ✓ Use standard abbreviations (St, Ave, Blvd)

═══════════════════════════════════════════════════════════════════

KEYBOARD SHORTCUTS
═══════════════════════════════════════════════════════════════════

⌨️ CUSTOMER TAB SHORTCUTS:
   • Ctrl+F - Focus search box
   • F5 - Refresh customer list
   • Enter - Edit selected customer
   • Delete - Delete selected customer
   • Ctrl+N - New customer (if implemented)

⌨️ CUSTOMER FORM SHORTCUTS:
   • Enter - Save customer
   • Escape - Cancel and close
   • Tab - Move to next field

═══════════════════════════════════════════════════════════════════

TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════

❌ CUSTOMER NOT APPEARING IN LIST:
   • Check search filters
   • Click "Refresh" button
   • Clear search box and try again

❌ CANNOT DELETE CUSTOMER:
   • Customer has associated invoices
   • Delete or reassign invoices first
   • Check customer statistics for invoice count

❌ CUSTOMER STATISTICS NOT UPDATING:
   • Click "Refresh" in customer list
   • Close and reopen customer edit dialog
   • Check if invoices are properly associated

❌ SEARCH NOT WORKING:
   • Clear search box completely
   • Type slowly to allow real-time search
   • Check spelling and try partial matches

Need more help? Check other help tabs or contact support!
        """
        
        self.insert_formatted_text(content, customers_text)

    def create_invoices_help_tab(self):
        """Create invoices help tab."""
        tab_frame = ttk.Frame(self.help_notebook)
        self.help_notebook.add(tab_frame, text="📄 Invoices")

        content = self.create_scrollable_content(tab_frame)
        
        invoices_text = """
INVOICE MANAGEMENT GUIDE

Complete guide to creating, managing, and tracking invoices.

═══════════════════════════════════════════════════════════════════

CREATING INVOICES
═══════════════════════════════════════════════════════════════════

📝 INVOICE HEADER INFORMATION:
   • Customer (Required) - Select from dropdown list
   • Invoice Number - Auto-generated or enter custom
   • Issued Date (Required) - When invoice is created
   • Due Date (Required) - Payment deadline
   • Status - Draft, Sent, Paid, or Overdue

💡 INVOICE NUMBER TIPS:
   ✓ Auto-generated numbers ensure uniqueness
   ✓ Custom numbers: "INV-2024-001" or "24-001"
   ✓ Keep numbering consistent
   ✗ Don't reuse invoice numbers

📅 DATE GUIDELINES:
   • Issued Date: Usually today's date
   • Due Date: Common terms: Net 30, Net 15, Due on Receipt
   • Due Date cannot be before Issued Date

═══════════════════════════════════════════════════════════════════

LINE ITEMS EXPLAINED
═══════════════════════════════════════════════════════════════════

Each invoice can have multiple line items with these fields:

📋 DESCRIPTION:
   • What work was performed or product sold
   • Be specific: "Oil change and filter replacement"
   • Include model numbers or specifications if relevant

⏰ HOURS:
   • Time spent on this line item
   • Supports decimals: 1.5 hours, 0.25 hours (15 minutes)
   • For fixed-price items, use 1.0 and put price in Rate

💰 RATE:
   • Hourly rate or fixed price
   • Enter as decimal: 75.00 for $75
   • Can be different for different types of work

🔧 PARTS:
   • Cost of parts, materials, or supplies
   • Separate from labor costs
   • Enter as decimal: 25.50 for $25.50

📊 TAX %:
   • Tax percentage applied to this line item
   • Enter as percentage: 8.5 for 8.5% tax
   • Applied to (Hours × Rate + Parts)

💡 CALCULATION EXAMPLE:
Description: "Brake pad replacement"
Hours: 2.0
Rate: $85.00
Parts: $120.00
Tax: 8.5%

Line Total = (2.0 × $85.00 + $120.00) × 1.085
Line Total = ($170.00 + $120.00) × 1.085
Line Total = $290.00 × 1.085 = $314.65

═══════════════════════════════════════════════════════════════════

INVOICE STATUSES
═══════════════════════════════════════════════════════════════════

📌 STATUS MEANINGS:
   • DRAFT - Invoice being created, not sent yet
   • SENT - Invoice sent to customer, awaiting payment
   • PAID - Payment received, invoice complete
   • OVERDUE - Past due date and still unpaid

🔄 STATUS WORKFLOW:
   1. Create invoice (starts as DRAFT)
   2. Review and finalize
   3. Send to customer (change to SENT)
   4. Receive payment (change to PAID)
   5. If payment late (automatically becomes OVERDUE)

⚠️ OVERDUE DETECTION:
   • Automatically identified when Due Date < Today
   • Only applies to SENT or DRAFT invoices
   • PAID invoices are never overdue

═══════════════════════════════════════════════════════════════════

INVOICE LIST FEATURES
═══════════════════════════════════════════════════════════════════

🔍 SEARCH AND FILTER:
   • Search Box: Find invoices by number or customer name
   • Status Filter: Show only Draft, Sent, Paid, or Overdue
   • Real-time search as you type

📊 TABLE COLUMNS:
   • Invoice Number - Unique identifier
   • Customer - Customer name
   • Issued Date - When invoice was created
   • Status - Current payment status
   • Total - Final amount including tax

📄 PAGINATION:
   • 10 invoices per page by default
   • Use "Previous" and "Next" buttons to navigate
   • Page indicator shows current position

⚡ QUICK ACTIONS:
   • Double-click invoice to view details
   • Details window shows full invoice information

═══════════════════════════════════════════════════════════════════

EDITING INVOICES
═══════════════════════════════════════════════════════════════════

✏️ WHEN TO EDIT:
   ✓ Invoice is still DRAFT status
   ✓ Need to correct errors before sending
   ✓ Adding forgotten line items
   ✓ Updating customer information

⚠️ EDITING CONSIDERATIONS:
   • Be careful editing SENT invoices
   • Major changes may require new invoice
   • Always notify customer of changes

📝 EDITING PROCESS:
   1. Find invoice in invoice list
   2. Double-click to open details
   3. Click "Edit" button
   4. Make changes in form
   5. Click "Update Invoice"

═══════════════════════════════════════════════════════════════════

PDF GENERATION
═══════════════════════════════════════════════════════════════════

🖨️ CREATING PDF INVOICES:
   1. Open invoice details window
   2. Click "Generate PDF" button
   3. Choose save location
   4. PDF is created instantly

📄 PDF FEATURES:
   ✓ Professional formatting
   ✓ Company logo (if uploaded)
   ✓ Complete invoice details
   ✓ Line-by-line breakdown
   ✓ Tax calculations
   ✓ Grand total
   ✓ Print-ready format

💡 PDF BEST PRACTICES:
   • Generate PDFs for all sent invoices
   • Save PDFs in organized folders
   • Include invoice number in filename
   • Keep copies for your records

═══════════════════════════════════════════════════════════════════

DELETING INVOICES
═══════════════════════════════════════════════════════════════════

🗑️ WHEN TO DELETE:
   • Duplicate invoices created by mistake
   • Test invoices during setup
   • Invoices with major errors that can't be edited

⚠️ DELETION WARNING:
   • Deletion is permanent and cannot be undone
   • Affects customer statistics and totals
   • Use with extreme caution

📋 DELETION PROCESS:
   1. Open invoice details
   2. Click "Delete" button
   3. Confirm deletion
   4. Invoice is permanently removed

═══════════════════════════════════════════════════════════════════

INVOICE BEST PRACTICES
═══════════════════════════════════════════════════════════════════

💼 PROFESSIONAL INVOICING:
   ✓ Include detailed descriptions
   ✓ Use consistent numbering system
   ✓ Set clear payment terms
   ✓ Include your contact information
   ✓ Generate PDFs for customer records

🕐 TIMING BEST PRACTICES:
   ✓ Create invoices promptly after work completion
   ✓ Send invoices immediately when finished
   ✓ Follow up on overdue invoices
   ✓ Update statuses when payments received

💰 PRICING GUIDELINES:
   ✓ Be transparent about rates and charges
   ✓ Separate labor and parts clearly
   ✓ Include applicable taxes
   ✓ Round to reasonable precision (usually 2 decimal places)

═══════════════════════════════════════════════════════════════════

TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════

❌ CANNOT CREATE INVOICE:
   • Must have at least one customer first
   • Check that customer list is not empty
   • Refresh customer data if needed

❌ TOTAL NOT CALCULATING:
   • Check that Hours and Rate are valid numbers
   • Verify Tax % is numeric (not text)
   • Remove any special characters from amounts

❌ PDF GENERATION FAILS:
   • Check file permissions in save location
   • Try saving to a different folder
   • Ensure invoice has all required data

❌ CUSTOMER NOT IN DROPDOWN:
   • Customer may have been deleted
   • Refresh the invoice form
   • Check customer list to verify customer exists

❌ SEARCH NOT WORKING:
   • Clear search box completely
   • Check spelling of invoice numbers
   • Try searching by customer name instead

Need more specific help? Check other tabs or contact support!
        """
        
        self.insert_formatted_text(content, invoices_text)

    def create_dashboard_help_tab(self):
        """Create dashboard help tab."""
        tab_frame = ttk.Frame(self.help_notebook)
        self.help_notebook.add(tab_frame, text="📊 Dashboard")

        content = self.create_scrollable_content(tab_frame)
        
        dashboard_text = """
DASHBOARD GUIDE

Your dashboard provides a quick overview of your business at a glance.

═══════════════════════════════════════════════════════════════════

DASHBOARD OVERVIEW
═══════════════════════════════════════════════════════════════════

The dashboard is your business control center, showing key metrics and providing quick access to common tasks.

📊 STATISTICS CARDS:
Four main cards show your business health:
   • Total Customers
   • Total Invoices  
   • Pending Invoices
   • Overdue Invoices

🎯 QUICK ACTIONS:
Buttons for the most common tasks:
   • New Customer
   • New Invoice
   • Refresh

═══════════════════════════════════════════════════════════════════

STATISTICS CARDS EXPLAINED
═══════════════════════════════════════════════════════════════════

👥 TOTAL CUSTOMERS:
   • Shows count of all customers in your database
   • Includes all customers regardless of status
   • Updates automatically when customers are added/removed

📄 TOTAL INVOICES:
   • Shows count of all invoices ever created
   • Includes all statuses: Draft, Sent, Paid, Overdue
   • Gives you overall business activity level

⏳ PENDING INVOICES:
   • Shows invoices awaiting payment
   • Includes: Draft and Sent invoices not yet paid
   • Excludes: Paid invoices and overdue ones
   • Key metric for cash flow management

🚨 OVERDUE INVOICES:
   • Shows invoices past their due date
   • Only includes Sent or Draft invoices where Due Date < Today
   • Critical for following up on late payments
   • Helps maintain healthy cash flow

═══════════════════════════════════════════════════════════════════

USING QUICK ACTIONS
═══════════════════════════════════════════════════════════════════

👥 NEW CUSTOMER BUTTON:
   • Opens customer creation dialog instantly
   • Same as going to Customers tab → New Customer
   • Saves navigation time for frequent use
   • After creating customer, dashboard updates automatically

📄 NEW INVOICE BUTTON:
   • Opens invoice creation dialog instantly
   • Requires at least one customer to exist
   • If no customers exist, prompts to create one first
   • After creating invoice, dashboard updates automatically

🔄 REFRESH BUTTON:
   • Updates all statistics immediately
   • Use if numbers seem outdated
   • Automatically happens when you make changes
   • Useful after bulk operations or data imports

═══════════════════════════════════════════════════════════════════

INTERPRETING YOUR DASHBOARD
═══════════════════════════════════════════════════════════════════

💼 HEALTHY BUSINESS INDICATORS:
   ✓ Growing customer count over time
   ✓ Regular invoice creation activity
   ✓ Low overdue invoice count
   ✓ Reasonable pending invoices (normal cash flow)

⚠️ WARNING SIGNS:
   ⚠ High overdue invoice count
   ⚠ Many pending invoices piling up
   ⚠ No new invoices being created
   ⚠ Customer count not growing

📈 DASHBOARD ANALYTICS:
   • Use dashboard as daily health check
   • Compare numbers week-to-week
   • Set goals for customer growth
   • Monitor overdue trends

═══════════════════════════════════════════════════════════════════

DASHBOARD BEST PRACTICES
═══════════════════════════════════════════════════════════════════

🌅 DAILY ROUTINE:
   1. Check dashboard first thing each day
   2. Review overdue invoices (take action if needed)
   3. Note pending invoice count
   4. Plan day based on business needs

📊 WEEKLY REVIEW:
   • Compare this week's numbers to last week
   • Track customer growth trends
   • Monitor invoice creation patterns
   • Assess payment collection effectiveness

🎯 GOAL SETTING:
   • Set targets for customer count
   • Aim to minimize overdue invoices
   • Track invoice creation consistency
   • Monitor business growth metrics

═══════════════════════════════════════════════════════════════════

DASHBOARD WORKFLOW INTEGRATION
═══════════════════════════════════════════════════════════════════

🔄 MORNING WORKFLOW:
   1. Open application to dashboard
   2. Check overdue invoices (red card)
   3. If overdue > 0, go to Invoices tab to follow up
   4. Review pending invoices for expected payments
   5. Plan new invoice creation for completed work

💰 CASH FLOW MANAGEMENT:
   • Pending Invoices = Money coming in
   • Overdue Invoices = Money at risk
   • Total Invoices = Business activity level
   • Use these metrics for financial planning

📞 CUSTOMER FOLLOW-UP:
   • High overdue count = need customer communication
   • Use customer phone numbers from customer tab
   • Update invoice status after payment received
   • Dashboard reflects improvements immediately

═══════════════════════════════════════════════════════════════════

DASHBOARD SHORTCUTS
═══════════════════════════════════════════════════════════════════

⌨️ KEYBOARD SHORTCUTS:
   • F5 - Refresh dashboard
   • Ctrl+1 - Go to Dashboard tab (if implemented)
   • Click cards to drill down to related data

🖱️ MOUSE SHORTCUTS:
   • Click statistics cards for more details
   • Right-click quick action buttons for options
   • Hover over cards for tooltips with additional info

═══════════════════════════════════════════════════════════════════

CUSTOMIZING YOUR DASHBOARD
═══════════════════════════════════════════════════════════════════

🎨 VISUAL CUSTOMIZATION:
   • Dashboard colors match your theme
   • Logo uploads (Logo tab) appear throughout app
   • Consistent branding across all views

📊 DATA CUSTOMIZATION:
   • Statistics update based on your actual data
   • No configuration needed - automatic calculation
   • Real-time updates as you work

═══════════════════════════════════════════════════════════════════

TROUBLESHOOTING DASHBOARD ISSUES
═══════════════════════════════════════════════════════════════════

❌ STATISTICS NOT UPDATING:
   • Click "Refresh" button
   • Close and reopen application
   • Check that database connection is working

❌ INCORRECT NUMBERS:
   • Verify by checking actual data in other tabs
   • Use Refresh button to recalculate
   • Check that invoice dates are correct

❌ SLOW LOADING:
   • Large databases may take longer
   • Close other applications to free memory
   • Consider archiving old invoices

❌ QUICK ACTIONS NOT WORKING:
   • Ensure you have necessary permissions
   • Check that customer database has data
   • Try refreshing and attempting again

═══════════════════════════════════════════════════════════════════

DASHBOARD SUCCESS TIPS
═══════════════════════════════════════════════════════════════════

🎯 DAILY GOALS:
   • Check dashboard every morning
   • Keep overdue invoices at zero when possible
   • Maintain steady invoice creation
   • Grow customer base consistently

📈 GROWTH TRACKING:
   • Take weekly screenshots of your dashboard
   • Track month-over-month improvements
   • Set realistic targets for each metric
   • Celebrate milestones and achievements

💡 EFFICIENCY TIPS:
   • Use quick actions instead of navigating tabs
   • Bookmark application for easy access
   • Keep dashboard open as your business hub
   • Train team members on dashboard interpretation

Your dashboard is designed to give you instant insight into your business health. Use it daily for maximum benefit!
        """
        
        self.insert_formatted_text(content, dashboard_text)

    def create_troubleshooting_tab(self):
        """Create troubleshooting help tab."""
        tab_frame = ttk.Frame(self.help_notebook)
        self.help_notebook.add(tab_frame, text="🔧 Troubleshooting")

        content = self.create_scrollable_content(tab_frame)
        
        troubleshooting_text = """
TROUBLESHOOTING GUIDE

Solutions to common problems and error messages.

═══════════════════════════════════════════════════════════════════

COMMON PROBLEMS & SOLUTIONS
═══════════════════════════════════════════════════════════════════

🔐 LOGIN ISSUES
═══════════════════════════════════════════════════════════════════

❌ "Invalid email or password":
   ✓ Check that Caps Lock is off
   ✓ Verify email address spelling
   ✓ Use "👁" button to reveal password and check
   ✓ Try typing password slowly and carefully

❌ "User not found":
   ✓ Make sure you're using the correct email
   ✓ Check if you need to create an account first
   ✓ Email addresses are case-sensitive

❌ Can't create account:
   ✓ Password must be 8+ characters
   ✓ Password must contain letters AND numbers
   ✓ Email address must be valid format
   ✓ Email cannot already be registered

🔧 RESET PASSWORD:
   ✓ Click "Reset Password" on login screen
   ✓ Enter master passcode: 0713
   ✓ Enter email address to reset
   ✓ Create new password following requirements

═══════════════════════════════════════════════════════════════════

DATABASE ISSUES
═══════════════════════════════════════════════════════════════════

❌ "Database connection error":
   ✓ Close and restart the application
   ✓ Check that database file isn't corrupted
   ✓ Ensure you have write permissions to app folder
   ✓ Try running as administrator (Windows)

❌ Data not appearing:
   ✓ Click "Refresh" buttons
   ✓ Clear search filters
   ✓ Check that you're logged in correctly
   ✓ Verify data exists by checking other tabs

❌ "Cannot save data":
   ✓ Check available disk space
   ✓ Ensure app folder isn't read-only
   ✓ Close other applications using database
   ✓ Restart application and try again

═══════════════════════════════════════════════════════════════════

CUSTOMER MANAGEMENT ISSUES
═══════════════════════════════════════════════════════════════════

❌ Cannot delete customer:
   ✓ Customer has associated invoices (by design)
   ✓ Delete or reassign invoices first
   ✓ Check customer statistics for invoice count

❌ Customer not in invoice dropdown:
   ✓ Refresh the invoice form
   ✓ Check that customer still exists
   ✓ Verify you're logged in as correct user

❌ Search not working:
   ✓ Clear search box completely
   ✓ Type search terms slowly
   ✓ Check spelling and try partial matches
   ✓ Click "Refresh" button

❌ "Validation Error" when saving:
   ✓ Name field cannot be empty
   ✓ Email must be valid format (if provided)
   ✓ Check for special characters in fields
   ✓ Review error messages for specific guidance

═══════════════════════════════════════════════════════════════════

INVOICE MANAGEMENT ISSUES
═══════════════════════════════════════════════════════════════════

❌ Cannot create invoice:
   ✓ Must have at least one customer first
   ✓ Check customer dropdown is populated
   ✓ Refresh customer data
   ✓ Create customer before invoice

❌ Calculations are wrong:
   ✓ Verify Hours and Rate are numbers (not text)
   ✓ Check tax percentage format (8.5 not 8.5%)
   ✓ Ensure no special characters in amounts
   ✓ Use decimal points, not commas

❌ Invoice total shows as $0.00:
   ✓ Add line items with descriptions
   ✓ Enter valid hours and rates
   ✓ Click in different field to trigger calculation
   ✓ Check that all numbers are properly formatted

❌ Due date validation error:
   ✓ Due date cannot be before issued date
   ✓ Use date picker or valid date format
   ✓ Check that dates are realistic

❌ "Duplicate invoice number":
   ✓ Invoice numbers must be unique
   ✓ Use auto-generated numbers
   ✓ If using custom numbers, make them unique

═══════════════════════════════════════════════════════════════════

PDF GENERATION ISSUES
═══════════════════════════════════════════════════════════════════

❌ "PDF generation failed":
   ✓ Check that save location has write permissions
   ✓ Try saving to a different folder
   ✓ Ensure filename doesn't contain special characters
   ✓ Close PDF if already open in another program

❌ "Cannot find template":
   ✓ PDF templates should be in templates/pdf folder
   ✓ Check application installation integrity
   ✓ Try different template if available
   ✓ Reinstall application if needed

❌ PDF shows placeholder data:
   ✓ Ensure invoice has all required data
   ✓ Check that customer information is complete
   ✓ Verify line items have descriptions
   ✓ Refresh invoice data before generating

❌ Logo not appearing in PDF:
   ✓ Upload logo through Logo tab
   ✓ Check logo file format (PNG, JPG supported)
   ✓ Verify logo file isn't corrupted
   ✓ Try regenerating PDF after logo upload

═══════════════════════════════════════════════════════════════════

INTERFACE ISSUES
═══════════════════════════════════════════════════════════════════

❌ Application won't start:
   ✓ Check that all dependencies are installed
   ✓ Try running from command line to see errors
   ✓ Check system requirements
   ✓ Reinstall application

❌ Slow performance:
   ✓ Close other memory-intensive applications
   ✓ Restart the application
   ✓ Check available system memory
   ✓ Archive old data if database is very large

❌ Interface elements missing:
   ✓ Check screen resolution and scaling
   ✓ Maximize application window
   ✓ Reset window size (F11 or Escape)
   ✓ Check display settings

❌ Keyboard shortcuts not working:
   ✓ Ensure focus is on correct window
   ✓ Check that fields aren't in edit mode
   ✓ Try clicking in empty area first
   ✓ Some shortcuts are context-specific

═══════════════════════════════════════════════════════════════════

LOGO UPLOAD ISSUES
═══════════════════════════════════════════════════════════════════

❌ "Cannot upload logo":
   ✓ Check file format (PNG, JPG, JPEG, GIF, BMP)
   ✓ Ensure file size is under 10MB
   ✓ Verify write permissions to assets folder
   ✓ Try a different image file

❌ Logo appears distorted:
   ✓ Use square images (same width and height)
   ✓ Minimum recommended size: 200x200 pixels
   ✓ Try PNG format for best quality
   ✓ Avoid very wide or tall images

❌ "Logo not found" error:
   ✓ Logo file may have been moved or deleted
   ✓ Try uploading logo again
   ✓ Check assets folder permissions
   ✓ Use "Reset to Default" if needed

═══════════════════════════════════════════════════════════════════

SYSTEM REQUIREMENTS ISSUES
═══════════════════════════════════════════════════════════════════

💾 MINIMUM REQUIREMENTS:
   • Windows 10 or newer (or Linux/Mac equivalent)
   • 4GB RAM minimum (8GB recommended)
   • 500MB available disk space
   • Python 3.8 or newer (if running from source)

🔧 DEPENDENCY ISSUES:
   ✓ Ensure all required Python packages are installed
   ✓ Check requirements.txt file
   ✓ Try reinstalling dependencies
   ✓ Use virtual environment to avoid conflicts

═══════════════════════════════════════════════════════════════════

DATA BACKUP & RECOVERY
═══════════════════════════════════════════════════════════════════

💾 BACKING UP YOUR DATA:
   1. Locate database file (usually invoices.db)
   2. Copy file to safe location regularly
   3. Include assets folder (contains logos)
   4. Export data occasionally using export features

🔄 RESTORING DATA:
   1. Close application completely
   2. Replace database file with backup
   3. Restart application
   4. Verify data integrity

⚠️ PREVENTING DATA LOSS:
   ✓ Regular backups (weekly recommended)
   ✓ Multiple backup locations
   ✓ Test restores occasionally
   ✓ Don't modify database files directly

═══════════════════════════════════════════════════════════════════

GETTING ADDITIONAL HELP
═══════════════════════════════════════════════════════════════════

📞 WHEN TO SEEK HELP:
   • Error messages not covered in this guide
   • Data corruption or loss
   • Installation problems
   • Performance issues persisting after troubleshooting

💡 BEFORE CONTACTING SUPPORT:
   ✓ Try solutions in this guide first
   ✓ Note exact error messages
   ✓ Document steps that led to the problem
   ✓ Check if problem is reproducible

📋 INFORMATION TO PROVIDE:
   • Operating system version
   • Application version
   • Exact error message
   • Steps to reproduce the problem
   • Whether data backup is available

Remember: Most issues can be resolved with the solutions above. Take your time and follow steps carefully!
        """
        
        self.insert_formatted_text(content, troubleshooting_text)

    def create_keyboard_shortcuts_tab(self):
        """Create keyboard shortcuts tab."""
        tab_frame = ttk.Frame(self.help_notebook)
        self.help_notebook.add(tab_frame, text="⌨️ Shortcuts")

        content = self.create_scrollable_content(tab_frame)
        
        shortcuts_text = """
KEYBOARD SHORTCUTS REFERENCE

Speed up your work with these keyboard shortcuts.

═══════════════════════════════════════════════════════════════════

GLOBAL SHORTCUTS (WORK EVERYWHERE)
═══════════════════════════════════════════════════════════════════

🌐 APPLICATION LEVEL:
   F5             - Refresh current tab/data
   F11            - Toggle fullscreen mode
   Escape         - Exit fullscreen mode
   Ctrl+Q         - Quit application (if implemented)
   Alt+F4         - Close application (Windows)

🔐 LOGIN SCREEN:
   Enter          - Login with entered credentials
   Escape         - Clear form or exit
   Tab            - Move between email and password fields

═══════════════════════════════════════════════════════════════════

NAVIGATION SHORTCUTS
═══════════════════════════════════════════════════════════════════

📑 TAB NAVIGATION:
   Ctrl+1         - Dashboard tab (if implemented)
   Ctrl+2         - Customers tab (if implemented)
   Ctrl+3         - Invoices tab (if implemented)
   Ctrl+4         - Reports tab (if implemented)
   Ctrl+5         - Logo tab (if implemented)
   Ctrl+6         - Help tab (if implemented)

🖱️ GENERAL NAVIGATION:
   Tab            - Move to next field/button
   Shift+Tab      - Move to previous field/button
   Enter          - Activate default button/action
   Escape         - Cancel current operation/close dialog
   Space          - Activate focused button
   Arrow Keys     - Navigate lists and tables

═══════════════════════════════════════════════════════════════════

CUSTOMERS TAB SHORTCUTS
═══════════════════════════════════════════════════════════════════

👥 CUSTOMER MANAGEMENT:
   Ctrl+F         - Focus search box
   F5             - Refresh customer list
   Enter          - Edit selected customer
   Delete         - Delete selected customer (with confirmation)
   Ctrl+N         - New customer (if implemented)
   Escape         - Clear search filter

📋 CUSTOMER LIST:
   ↑↓ Arrow Keys  - Select customer in list
   Home           - Go to first customer
   End            - Go to last customer
   Page Up        - Scroll up one page
   Page Down      - Scroll down one page

✏️ CUSTOMER FORM:
   Enter          - Save customer
   Escape         - Cancel and close form
   Tab            - Move to next field
   Shift+Tab      - Move to previous field

═══════════════════════════════════════════════════════════════════

INVOICES TAB SHORTCUTS
═══════════════════════════════════════════════════════════════════

📄 INVOICE MANAGEMENT:
   Ctrl+F         - Focus search box
   F5             - Refresh invoice list
   Enter          - View selected invoice details
   Ctrl+N         - New invoice (if implemented)
   Delete         - Delete selected invoice (with confirmation)

📊 INVOICE LIST:
   ↑↓ Arrow Keys  - Select invoice in list
   Home           - Go to first invoice
   End            - Go to last invoice
   Page Up        - Previous page of invoices
   Page Down      - Next page of invoices

✏️ INVOICE FORM:
   Enter          - Save invoice
   Escape         - Cancel and close form
   Tab            - Move to next field
   Shift+Tab      - Move to previous field
   Ctrl+L         - Add new line item (if implemented)
   Ctrl+D         - Delete current line item (if implemented)

═══════════════════════════════════════════════════════════════════

DIALOG BOX SHORTCUTS
═══════════════════════════════════════════════════════════════════

💬 COMMON DIALOGS:
   Enter          - OK/Yes/Save button
   Escape         - Cancel/No/Close button
   Alt+Y          - Yes button
   Alt+N          - No button
   Alt+C          - Cancel button
   Alt+S          - Save button

📁 FILE DIALOGS:
   Enter          - Open/Save selected file
   Escape         - Cancel file operation
   F2             - Rename file (if applicable)
   Delete         - Delete file (if applicable)
   Backspace      - Go up one directory level

═══════════════════════════════════════════════════════════════════

FORM FIELD SHORTCUTS
═══════════════════════════════════════════════════════════════════

📝 TEXT FIELDS:
   Ctrl+A         - Select all text
   Ctrl+C         - Copy selected text
   Ctrl+V         - Paste text
   Ctrl+X         - Cut selected text
   Ctrl+Z         - Undo last change
   Home           - Go to beginning of field
   End            - Go to end of field

📅 DATE FIELDS:
   Today's Date   - T key (in some date pickers)
   ↑↓ Arrow Keys  - Increment/decrement date
   Page Up/Down   - Change month
   Home           - Go to first day of month
   End            - Go to last day of month

🔢 NUMERIC FIELDS:
   ↑↓ Arrow Keys  - Increment/decrement value
   Page Up/Down   - Larger increment/decrement
   Home           - Minimum value
   End            - Maximum value

═══════════════════════════════════════════════════════════════════

TABLE/LIST SHORTCUTS
═══════════════════════════════════════════════════════════════════

📊 DATA TABLES:
   ↑↓ Arrow Keys  - Navigate rows
   ←→ Arrow Keys  - Navigate columns (if applicable)
   Home           - First row
   End            - Last row
   Ctrl+Home      - First row, first column
   Ctrl+End       - Last row, last column
   Page Up        - Previous page
   Page Down      - Next page

🔍 SEARCH IN TABLES:
   Ctrl+F         - Focus search box
   F3             - Find next (if implemented)
   Shift+F3       - Find previous (if implemented)
   Escape         - Clear search

═══════════════════════════════════════════════════════════════════

HELP TAB SHORTCUTS
═══════════════════════════════════════════════════════════════════

📚 HELP NAVIGATION:
   Ctrl+F         - Search within help content
   F1             - Go to help tab (if implemented)
   ↑↓ Arrow Keys  - Scroll help content
   Page Up/Down   - Scroll by page
   Home           - Go to top of current help section
   End            - Go to bottom of current help section

📑 HELP TABS:
   Ctrl+Tab       - Next help section
   Ctrl+Shift+Tab - Previous help section

═══════════════════════════════════════════════════════════════════

LOGO TAB SHORTCUTS
═══════════════════════════════════════════════════════════════════

🖼️ LOGO MANAGEMENT:
   Ctrl+O         - Open file dialog to upload logo
   F5             - Refresh logo preview
   Delete         - Reset to default logo (with confirmation)
   Escape         - Cancel upload operation

═══════════════════════════════════════════════════════════════════

ACCESSIBILITY SHORTCUTS
═══════════════════════════════════════════════════════════════════

♿ ACCESSIBILITY FEATURES:
   Tab            - Navigate to next interactive element
   Shift+Tab      - Navigate to previous interactive element
   Enter/Space    - Activate buttons and links
   Arrow Keys     - Navigate menus and lists
   Alt            - Access menu bar (if available)

🔍 ZOOM/DISPLAY:
   Ctrl++         - Zoom in (if implemented)
   Ctrl+-         - Zoom out (if implemented)
   Ctrl+0         - Reset zoom (if implemented)

═══════════════════════════════════════════════════════════════════

PRODUCTIVITY TIPS
═══════════════════════════════════════════════════════════════════

⚡ SPEED UP YOUR WORKFLOW:
   • Learn 3-5 shortcuts you use most often
   • Practice shortcuts until they become muscle memory
   • Use Tab to navigate forms instead of mouse
   • Keep hands on keyboard when entering data
   • Use Enter to save instead of clicking Save button

🎯 MOST USEFUL SHORTCUTS:
   1. F5 (Refresh) - Use constantly for updated data
   2. Ctrl+F (Find) - Quick search in any list
   3. Enter (Save/OK) - Faster than clicking buttons
   4. Escape (Cancel) - Quick way to close dialogs
   5. Tab (Navigate) - Move between fields efficiently

📝 CUSTOM SHORTCUTS:
   Some shortcuts may be customizable in future versions. 
   Check application preferences or settings menu.

═══════════════════════════════════════════════════════════════════

TROUBLESHOOTING SHORTCUTS
═══════════════════════════════════════════════════════════════════

❌ SHORTCUTS NOT WORKING:
   ✓ Ensure focus is on correct window/field
   ✓ Check that Num Lock/Caps Lock aren't interfering
   ✓ Try clicking in empty area first
   ✓ Some shortcuts only work in specific contexts
   ✓ Check if field is in edit mode (may block shortcuts)

🔧 RESET SHORTCUTS:
   ✓ Restart application
   ✓ Check keyboard settings in OS
   ✓ Try different keyboard if wireless
   ✓ Update keyboard drivers if needed

Remember: Not all shortcuts may be implemented in current version. This list shows planned and available shortcuts.
        """
        
        self.insert_formatted_text(content, shortcuts_text)

    def create_scrollable_content(self, parent):
        """Create a scrollable text widget for help content."""
        # Create frame for text and scrollbar
        text_frame = tk.Frame(parent, bg=COLORS["background"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Create text widget
        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Courier New", 10),  # Monospace font for better formatting
            bg=COLORS["section"],
            fg=COLORS["text"],
            relief="sunken",
            bd=1,
            padx=15,
            pady=15,
            state=tk.NORMAL
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=scrollbar.set)

        return text_widget

    def insert_formatted_text(self, text_widget, content):
        """Insert formatted text with basic styling."""
        text_widget.delete("1.0", tk.END)
        
        # Configure text tags for formatting
        text_widget.tag_configure("header", font=("Arial", 12, "bold"), foreground=COLORS["primary"])
        text_widget.tag_configure("subheader", font=("Arial", 11, "bold"), foreground=COLORS["secondary"])
        text_widget.tag_configure("code", font=("Courier New", 10), background=COLORS["background"])
        text_widget.tag_configure("highlight", background="#FFFFCC")

        lines = content.split('\n')
        for line in lines:
            # Apply basic formatting based on content
            if line.startswith('═══'):
                text_widget.insert(tk.END, line + '\n', "header")
            elif line.strip() and line.strip()[0] in ['🔐', '👥', '📄', '📊', '⚡', '💡', '🎯']:
                text_widget.insert(tk.END, line + '\n', "subheader")
            elif '✓' in line or '❌' in line or '⚠️' in line:
                text_widget.insert(tk.END, line + '\n', "highlight")
            else:
                text_widget.insert(tk.END, line + '\n')

        text_widget.configure(state=tk.DISABLED)  # Make read-only

    def show_quick_start(self):
        """Show quick start popup."""
        quick_start_text = """
🚀 QUICK START GUIDE

1. CREATE ACCOUNT:
   • Click "Create Account" on login screen
   • Enter email and secure password
   • Click "CREATE ACCOUNT"

2. ADD FIRST CUSTOMER:
   • Go to Customers tab
   • Click "New Customer"
   • Enter name and contact info
   • Click "Create Customer"

3. CREATE FIRST INVOICE:
   • Go to Invoices tab
   • Click "New Invoice"
   • Select customer
   • Add line items (description, hours, rate)
   • Click "Create Invoice"

4. GENERATE PDF:
   • Double-click invoice
   • Click "Generate PDF"
   • Choose save location
   • Done!

Need more help? Check the detailed help tabs above.
        """
        
        messagebox.showinfo("Quick Start Guide", quick_start_text)

    def show_video_guide(self):
        """Show video guide placeholder."""
        messagebox.showinfo(
            "Video Tutorials",
            "Video tutorials are coming soon!\n\n"
            "For now, please use the detailed written guides "
            "in the help tabs above.\n\n"
            "Check back in future updates for video content."
        )

    def show_faq(self):
        """Show frequently asked questions."""
        faq_text = """
❓ FREQUENTLY ASKED QUESTIONS

Q: How do I backup my data?
A: Your data is stored in a database file. Regularly copy the entire application folder to a safe location.

Q: Can I use this on multiple computers?
A: Yes! Copy the entire application folder to move your data and settings.

Q: What if I forget my password?
A: Use "Reset Password" on login screen with master code: 0713

Q: Can I customize invoice templates?
A: PDF templates can be customized by editing HTML files in the templates folder.

Q: Is my data secure?
A: Data is stored locally on your computer. Use your OS security features to protect the application folder.

Q: How many customers/invoices can I have?
A: No built-in limits. Performance depends on your computer's capabilities.

Q: Can I export my data?
A: Export features are planned for future updates. Currently, backup the database file.

Q: Does this work offline?
A: Yes! This is a fully offline application. No internet connection required.

Need more specific help? Check the other help tabs!
        """
        
        messagebox.showinfo("Frequently Asked Questions", faq_text)

    def get_status(self):
        """Get current tab status for debugging."""
        return {
            'help_notebook_tabs': self.help_notebook.tabs(),
            'current_tab': self.help_notebook.select(),
            'has_help_content': hasattr(self, 'help_notebook')
        }