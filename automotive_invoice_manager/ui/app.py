# Modified main application with customized login screen and responsive window management
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
import sys
import logging
import platform

# Base directory for bundled assets
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

from automotive_invoice_manager.ui.theme import COLORS, setup_styles
from automotive_invoice_manager.ui.main_interface import TabbedMainInterface

# Try to import PIL for logo support
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Import your existing services
try:
    from ..services import AuthManager, CustomerService, InvoiceService
    from ..backend.database.models import init_database
    from ..backend.database.connection import DatabaseManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the correct directory")


class ResponsiveWindowManager:
    """Manages responsive window sizing that respects taskbar and maintains UI elements."""
    
    def __init__(self, root):
        self.root = root
        self.is_maximized = False
        self.saved_geometry = None
        
    def setup_responsive_window(self):
        """Setup window with proper sizing that respects taskbar."""
        try:
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Calculate taskbar height and usable area
            taskbar_height = self.get_taskbar_height()
            usable_height = screen_height - taskbar_height
            
            # Set minimum window size to ensure UI elements are always visible
            min_width = 1000
            min_height = 700
            self.root.minsize(min_width, min_height)
            
            # Set default window size (95% of usable screen for better fit)
            default_width = int(screen_width * 0.95)
            default_height = int(usable_height * 0.95)
            
            # Center the window on usable area
            x = (screen_width - default_width) // 2
            y = (usable_height - default_height) // 2
            
            # Apply geometry
            self.root.geometry(f"{default_width}x{default_height}+{x}+{y}")
            
            # Configure background
            self.root.configure(bg=COLORS["background"])
            
            # Setup window events
            self.setup_window_events()
            
            logging.info(f"Responsive window setup: {default_width}x{default_height}+{x}+{y}")
            logging.info(f"Screen: {screen_width}x{screen_height}, Usable: {screen_width}x{usable_height}, Taskbar: {taskbar_height}")
            
        except Exception as e:
            logging.error(f"Error setting up responsive window: {e}")
            # Fallback to basic window setup
            self.root.geometry("1200x800")
            self.root.minsize(800, 600)
    
    def get_taskbar_height(self):
        """Calculate taskbar height based on platform."""
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows taskbar is typically 40-48 pixels, using safe margin
                return 50
            elif system == "Darwin":  # macOS
                # macOS dock and menu bar combined
                return 70
            else:  # Linux/Unix
                # Linux panel height varies
                return 45
                
        except Exception:
            # Default fallback with safe margin
            return 50
    
    def setup_window_events(self):
        """Setup window event handlers for responsive behavior."""
        # Bind keyboard shortcuts
        self.root.bind('<F11>', self.toggle_maximize)
        self.root.bind('<Escape>', self.restore_window)
        
        # Handle window close properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
    
    def toggle_maximize(self, event=None):
        """Toggle between maximized and normal window state."""
        try:
            if not self.is_maximized:
                # Save current geometry
                self.saved_geometry = self.root.geometry()
                
                # Maximize window (respecting taskbar)
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                taskbar_height = self.get_taskbar_height()
                usable_height = screen_height - taskbar_height
                
                self.root.geometry(f"{screen_width}x{usable_height}+0+0")
                self.is_maximized = True
                logging.info("Window maximized (respecting taskbar)")
                
            else:
                # Restore to saved geometry
                if self.saved_geometry:
                    self.root.geometry(self.saved_geometry)
                else:
                    self.setup_responsive_window()
                self.is_maximized = False
                logging.info("Window restored to normal size")
                
        except Exception as e:
            logging.error(f"Error toggling maximize: {e}")
    
    def restore_window(self, event=None):
        """Restore window to normal size."""
        if self.is_maximized:
            self.toggle_maximize()
    
    def on_window_close(self):
        """Handle window close event."""
        self.root.quit()


class FullScreenLoginApp:
    """Main application with customized full-screen login."""
    
    def __init__(self):
        self.root = tk.Tk()
        setup_styles()
        self.current_user = None
        self.password_visible = False  # Track password visibility
        
        # Initialize responsive window manager
        self.window_manager = ResponsiveWindowManager(self.root)
        
        # Image references to prevent garbage collection
        self.logo_image = None
        self.bg_photo = None
        self.login_bg_photo = None
        self.login_image = None
        self.login_pressed_image = None
        self.create_image = None
        self.create_pressed_image = None
        
        # Initialize services
        try:
            init_database()
            self.db_manager = DatabaseManager.get_instance()
            self.auth_service = AuthManager()
            self.customer_service = CustomerService()
            self.invoice_service = InvoiceService()
        except Exception as e:
            print(f"Error initializing services: {e}")
            messagebox.showerror("Initialization Error", 
                               f"Could not initialize application services: {e}")
            return
        
        # Setup window with responsive management
        self.setup_window()
        
        # Show login interface
        self.show_login_interface()
    
    def setup_window(self):
        """Setup the main window with responsive management."""
        self.root.title("Invoice Manager - Full Screen")
        
        # Use responsive window manager for proper setup
        self.window_manager.setup_responsive_window()
        
        # Additional window bindings
        self.root.bind('<Return>', lambda e: self.handle_login() if hasattr(self, 'email_entry') else None)
    
    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def load_logo(self, parent, size=(400, 400)):
        """Load and display the company logo."""
        if not PIL_AVAILABLE:
            # Fallback text logo
            logo_label = tk.Label(
                parent,
                text="INVOICE\nMANAGER",
                font=('Arial', 32, 'bold'),
                fg=COLORS["brand_purple"],
                bg=COLORS["background"],
                justify=tk.CENTER
            )
            logo_label.pack()
            return
        
        logo_path = ASSETS_DIR / 'logo.png'
        
        try:
            if logo_path.exists():
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize(size, Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(logo_img)
                
                logo_label = tk.Label(
                    parent,
                    image=self.logo_image,
                    bg=COLORS["background"]
                )
                logo_label.pack()
                print("Logo loaded successfully")
            else:
                # Fallback text logo
                logo_label = tk.Label(
                    parent,
                    text="INVOICE\nMANAGER",
                    font=('Arial', 32, 'bold'),
                    fg=COLORS["brand_purple"],
                    bg=COLORS["background"],
                    justify=tk.CENTER
                )
                logo_label.pack()
                print("Logo file not found, using text logo")
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback text logo
            logo_label = tk.Label(
                parent,
                text="INVOICE\nMANAGER",
                font=('Arial', 32, 'bold'),
                fg=COLORS["brand_purple"],
                bg=COLORS["background"],
                justify=tk.CENTER
            )
            logo_label.pack()
    
    def load_background_image(self, parent):
        """Load and set background image if available."""
        if not PIL_AVAILABLE:
            return
        
        bg_path = ASSETS_DIR / 'background.png'
        
        try:
            if bg_path.exists():
                # Get parent dimensions
                parent.update_idletasks()
                width = parent.winfo_width() or 1200
                height = parent.winfo_height() or 800
                
                bg_img = Image.open(bg_path)
                bg_img = bg_img.resize((width, height), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(bg_img)
                
                bg_label = tk.Label(parent, image=self.bg_photo)
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                print("Background image loaded")
        except Exception as e:
            print(f"Error loading background image: {e}")
    
    def load_button_images(self):
        """Load button images for login interface."""
        self.login_image = None
        self.login_pressed_image = None
        self.create_image = None
        self.create_pressed_image = None
        
        if not PIL_AVAILABLE:
            print("PIL not available - using text buttons")
            return
        
        button_paths = {
            'login': ASSETS_DIR / 'login.png',
            'login_pressed': ASSETS_DIR / 'login_pressed.png',
            'create': ASSETS_DIR / 'create.png',
            'create_pressed': ASSETS_DIR / 'create_pressed.png'
        }
        
        try:
            if button_paths['login'].exists():
                login_img = Image.open(button_paths['login'])
                self.login_image = ImageTk.PhotoImage(login_img)
                print("Login button image loaded")
            
            if button_paths['login_pressed'].exists():
                login_pressed_img = Image.open(button_paths['login_pressed'])
                self.login_pressed_image = ImageTk.PhotoImage(login_pressed_img)
                
            if button_paths['create'].exists():
                create_img = Image.open(button_paths['create'])
                self.create_image = ImageTk.PhotoImage(create_img)
                
            if button_paths['create_pressed'].exists():
                create_pressed_img = Image.open(button_paths['create_pressed'])
                self.create_pressed_image = ImageTk.PhotoImage(create_pressed_img)
                
        except Exception as e:
            print(f"Error loading button images: {e}")
    
    def show_login_interface(self):
        """Show the customized login interface."""
        self.clear_window()
        
        # Main container with background
        main_container = tk.Frame(self.root, bg=COLORS["background"])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Load and set background image
        self.load_background_image(main_container)
        
        # Center frame for login content
        center_frame = tk.Frame(main_container, bg=COLORS["background"])
        center_frame.pack(fill=tk.BOTH, expand=True)
        
        # Main login container (centered)
        login_container = tk.Frame(center_frame, bg=COLORS["background"])
        login_container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo section in CENTER-LEFT
        logo_frame = tk.Frame(login_container, bg=COLORS["background"], width=600, height=600)
        logo_frame.pack(side=tk.LEFT, padx=(0, 40))
        logo_frame.pack_propagate(False)
        
        # Center the logo within the frame
        logo_content_frame = tk.Frame(logo_frame, bg=COLORS["background"])
        logo_content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        self.load_logo(logo_content_frame, size=(400, 400))
        
        # Login area container on RIGHT side
        login_area_frame = tk.Frame(login_container, bg=COLORS["background"])
        login_area_frame.pack(side=tk.RIGHT)
        
        # Background image area
        bg_image_frame = tk.Frame(login_area_frame, bd=0, highlightthickness=0, relief='flat')
        bg_image_frame.pack()
        
        # Create the login background area with embedded buttons
        self.create_enhanced_login_area(bg_image_frame)
        
        # Footer with NHrinko on the right
        footer_frame = tk.Frame(main_container, bg=COLORS["footer_bg"], height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        # Footer content frame
        footer_content = tk.Frame(footer_frame, bg=COLORS["footer_bg"])
        footer_content.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Left side - Instructions
        footer_left = tk.Label(
            footer_content,
            text="Press F11 for fullscreen • Press Escape to restore • Enter to login",
            font=('Arial', 10),
            fg=COLORS["footer_text"],
            bg=COLORS["footer_bg"]
        )
        footer_left.pack(side=tk.LEFT, pady=20)
        
        # Right side - Company name
        footer_right = tk.Label(
            footer_content,
            text="NHrinko",
            font=('Arial', 10, 'bold'),
            fg=COLORS["footer_text"],
            bg=COLORS["footer_bg"]
        )
        footer_right.pack(side=tk.RIGHT, pady=20)
        
        # Key bindings
        self.root.bind('<Return>', lambda e: self.handle_login())
        
        # Focus on email entry
        self.root.after(100, lambda: self.email_entry.focus_set() if hasattr(self, 'email_entry') else None)
    
    def create_enhanced_login_area(self, parent_frame):
        """Create enhanced login area with embedded buttons and password controls."""
        # Load button images
        self.load_button_images()
        
        # Create login background frame
        if PIL_AVAILABLE:
            login_bg_path = ASSETS_DIR / 'login_bg.png'
            if login_bg_path.exists():
                try:
                    login_bg_img = Image.open(login_bg_path)
                    self.login_bg_photo = ImageTk.PhotoImage(login_bg_img)
                    
                    bg_canvas = tk.Canvas(
                        parent_frame,
                        width=login_bg_img.width,
                        height=login_bg_img.height,
                        bd=0,
                        highlightthickness=0
                    )
                    bg_canvas.pack()
                    bg_canvas.create_image(0, 0, anchor=tk.NW, image=self.login_bg_photo)
                    
                    # Create login form on canvas
                    self.create_login_form_on_canvas(bg_canvas, login_bg_img.width, login_bg_img.height)
                    return
                except Exception as e:
                    print(f"Error loading login background: {e}")
        
        # Fallback to standard login form
        self.create_standard_login_form(parent_frame)
    
    def create_login_form_on_canvas(self, canvas, bg_width, bg_height):
        """Create login form positioned on the background canvas."""
        # Calculate form position (centered on canvas)
        form_x = bg_width // 2
        form_y = bg_height // 2 - 50
        
        # Email field
        self.email_var = tk.StringVar()
        email_entry = tk.Entry(
            canvas,
            textvariable=self.email_var,
            font=('Arial', 12),
            width=25,
            relief='flat',
            bd=1
        )
        canvas.create_window(form_x, form_y - 40, window=email_entry)
        self.email_entry = email_entry
        
        # Password field with visibility toggle
        password_frame = tk.Frame(canvas, bg=COLORS["background"])
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            password_frame,
            textvariable=self.password_var,
            font=('Arial', 12),
            width=20,
            show="*",
            relief='flat',
            bd=1
        )
        self.password_entry.pack(side=tk.LEFT)
        
        # Eye button for password visibility
        eye_btn = tk.Button(
            password_frame,
            text="👁",
            font=('Arial', 10),
            command=self.toggle_password_visibility,
            relief='flat',
            bd=0,
            padx=2
        )
        eye_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        canvas.create_window(form_x, form_y, window=password_frame)
        
        # Login button
        if self.login_image:
            self.login_btn = tk.Button(
                canvas,
                image=self.login_image,
                command=self.handle_login,
                relief='flat',
                bd=0,
                bg=COLORS["background"]
            )
            # Bind press events for button animation
            self.login_btn.bind('<Button-1>', self.on_login_press)
            self.login_btn.bind('<ButtonRelease-1>', self.on_login_release)
        else:
            self.login_btn = tk.Button(
                canvas,
                text="LOGIN",
                command=self.handle_login,
                font=('Arial', 12, 'bold'),
                bg=COLORS["primary"],
                fg="white",
                relief='raised',
                bd=2,
                padx=20,
                pady=5
            )
        
        canvas.create_window(form_x, form_y + 50, window=self.login_btn)
        
        # Create Account button
        if self.create_image:
            self.register_btn = tk.Button(
                canvas,
                image=self.create_image,
                command=self.handle_register,
                relief='flat',
                bd=0,
                bg=COLORS["background"]
            )
            # Bind press events for button animation
            self.register_btn.bind('<Button-1>', self.on_register_press)
            self.register_btn.bind('<ButtonRelease-1>', self.on_register_release)
        else:
            self.register_btn = tk.Button(
                canvas,
                text="CREATE ACCOUNT",
                command=self.handle_register,
                font=('Arial', 12, 'bold'),
                bg=COLORS["secondary"],
                fg="white",
                relief='raised',
                bd=2,
                padx=20,
                pady=5
            )
        
        canvas.create_window(form_x, form_y + 100, window=self.register_btn)
        
        # Reset password link
        reset_btn = tk.Button(
            canvas,
            text="Reset Password",
            command=self.show_reset_password_dialog,
            font=('Arial', 10, 'underline'),
            fg=COLORS["brand_purple"],
            bg=COLORS["background"],
            relief='flat',
            bd=0
        )
        canvas.create_window(form_x, form_y + 140, window=reset_btn)
    
    def create_standard_login_form(self, parent_frame):
        """Create standard login form as fallback."""
        form_frame = tk.Frame(parent_frame, bg=COLORS["section"], padx=40, pady=40)
        form_frame.pack()
        
        # Title
        title_label = tk.Label(
            form_frame,
            text="Login",
            font=('Arial', 24, 'bold'),
            fg=COLORS["brand_purple"],
            bg=COLORS["section"]
        )
        title_label.pack(pady=(0, 30))
        
        # Email field
        tk.Label(
            form_frame,
            text="Email:",
            font=('Arial', 12),
            bg=COLORS["section"]
        ).pack(anchor='w', pady=(0, 5))
        
        self.email_var = tk.StringVar()
        self.email_entry = tk.Entry(
            form_frame,
            textvariable=self.email_var,
            font=('Arial', 12),
            width=30,
            relief='solid',
            bd=1
        )
        self.email_entry.pack(pady=(0, 15))
        
        # Password field with visibility toggle
        tk.Label(
            form_frame,
            text="Password:",
            font=('Arial', 12),
            bg=COLORS["section"]
        ).pack(anchor='w', pady=(0, 5))
        
        password_frame = tk.Frame(form_frame, bg=COLORS["section"])
        password_frame.pack(pady=(0, 20))
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            password_frame,
            textvariable=self.password_var,
            font=('Arial', 12),
            width=25,
            show="*",
            relief='solid',
            bd=1
        )
        self.password_entry.pack(side=tk.LEFT)
        
        # Eye button for password visibility
        eye_btn = tk.Button(
            password_frame,
            text="👁",
            font=('Arial', 10),
            command=self.toggle_password_visibility,
            relief='flat',
            bd=0,
            padx=5
        )
        eye_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=COLORS["section"])
        button_frame.pack(pady=10)
        
        self.login_btn = tk.Button(
            button_frame,
            text="LOGIN",
            command=self.handle_login,
            font=('Arial', 12, 'bold'),
            bg=COLORS["primary"],
            fg="white",
            relief='raised',
            bd=2,
            padx=20,
            pady=8
        )
        self.login_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.register_btn = tk.Button(
            button_frame,
            text="CREATE ACCOUNT",
            command=self.handle_register,
            font=('Arial', 12, 'bold'),
            bg=COLORS["secondary"],
            fg="white",
            relief='raised',
            bd=2,
            padx=20,
            pady=8
        )
        self.register_btn.pack(side=tk.LEFT)
        
        # Reset password link
        reset_btn = tk.Button(
            form_frame,
            text="Reset Password",
            command=self.show_reset_password_dialog,
            font=('Arial', 10, 'underline'),
            fg=COLORS["brand_purple"],
            bg=COLORS["section"],
            relief='flat',
            bd=0
        )
        reset_btn.pack(pady=(10, 0))
    
    def toggle_password_visibility(self):
        """Toggle password field visibility."""
        if self.password_visible:
            self.password_entry.configure(show="*")
            self.password_visible = False
        else:
            self.password_entry.configure(show="")
            self.password_visible = True
    
    def on_login_press(self, event):
        """Handle login button press."""
        if hasattr(self, 'login_pressed_image') and self.login_pressed_image:
            self.login_btn.configure(image=self.login_pressed_image)
    
    def on_login_release(self, event):
        """Handle login button release."""
        if hasattr(self, 'login_image') and self.login_image:
            self.login_btn.configure(image=self.login_image)
    
    def on_register_press(self, event):
        """Handle register button press."""
        if hasattr(self, 'create_pressed_image') and self.create_pressed_image:
            self.register_btn.configure(image=self.create_pressed_image)
    
    def on_register_release(self, event):
        """Handle register button release."""
        if hasattr(self, 'create_image') and self.create_image:
            self.register_btn.configure(image=self.create_image)
    
    def handle_login(self):
        """Handle login attempt."""
        email = self.email_var.get().strip()
        password = self.password_var.get()
        
        if not email:
            messagebox.showerror("Error", "Please enter your email address.")
            self.email_entry.focus_set()
            return
        
        if not password:
            messagebox.showerror("Error", "Please enter your password.")
            self.password_entry.focus_set()
            return
        
        try:
            user = self.auth_service.login(email, password)
            
            if user:
                self.current_user = user
                self.show_main_application()
            else:
                messagebox.showerror(
                    "Login Failed", 
                    "Invalid email or password. Please try again."
                )
                self.password_var.set("")
                self.password_entry.focus_set()
        except Exception as e:
            messagebox.showerror(
                "Login Error", 
                f"An error occurred during login: {str(e)}"
            )
            logging.error(f"Login error: {e}")
    
    def handle_register(self):
        """Handle registration."""
        self.show_enhanced_registration_dialog()
    
    def show_enhanced_registration_dialog(self):
        """Show enhanced registration dialog with bigger buttons."""
        reg_dialog = tk.Toplevel(self.root)
        reg_dialog.title("Create Account")
        reg_dialog.geometry("500x450")
        reg_dialog.resizable(False, False)
        
        # Center the dialog
        reg_dialog.transient(self.root)
        reg_dialog.grab_set()
        
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (450 // 2)
        reg_dialog.geometry(f"500x450+{x}+{y}")
        
        # Registration form
        main_frame = tk.Frame(reg_dialog, bg=COLORS["section"], padx=40, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Create New Account",
            font=('Arial', 20, 'bold'),
            fg=COLORS["brand_purple"],
            bg=COLORS["section"]
        )
        title_label.pack(pady=(0, 30))
        
        # Form variables
        email_var = tk.StringVar()
        password_var = tk.StringVar()
        confirm_password_var = tk.StringVar()
        
        # Email field
        tk.Label(
            main_frame,
            text="Email Address:",
            font=('Arial', 12, 'bold'),
            bg=COLORS["section"]
        ).pack(anchor='w', pady=(0, 5))
        
        email_entry = tk.Entry(
            main_frame,
            textvariable=email_var,
            font=('Arial', 12),
            width=35,
            relief='solid',
            bd=1
        )
        email_entry.pack(pady=(0, 15))
        
        # Password field
        tk.Label(
            main_frame,
            text="Password:",
            font=('Arial', 12, 'bold'),
            bg=COLORS["section"]
        ).pack(anchor='w', pady=(0, 5))
        
        password_entry = tk.Entry(
            main_frame,
            textvariable=password_var,
            font=('Arial', 12),
            width=35,
            show="*",
            relief='solid',
            bd=1
        )
        password_entry.pack(pady=(0, 15))
        
        # Confirm password field
        tk.Label(
            main_frame,
            text="Confirm Password:",
            font=('Arial', 12, 'bold'),
            bg=COLORS["section"]
        ).pack(anchor='w', pady=(0, 5))
        
        confirm_password_entry = tk.Entry(
            main_frame,
            textvariable=confirm_password_var,
            font=('Arial', 12),
            width=35,
            show="*",
            relief='solid',
            bd=1
        )
        confirm_password_entry.pack(pady=(0, 20))
        
        # Requirements text
        requirements_text = tk.Label(
            main_frame,
            text="Password must be 8+ characters with letters and numbers",
            font=('Arial', 9),
            fg=COLORS["muted"],
            bg=COLORS["section"]
        )
        requirements_text.pack(pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=COLORS["section"])
        button_frame.pack(pady=10)
        
        def submit_registration():
            email = email_var.get().strip()
            password = password_var.get()
            confirm_password = confirm_password_var.get()
            
            if not email:
                messagebox.showerror("Error", "Please enter an email address.")
                return
            
            if len(password) < 8:
                messagebox.showerror("Error", "Password must be at least 8 characters long.")
                return
            
            if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
                messagebox.showerror("Error", "Password must contain both letters and numbers.")
                return
            
            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match.")
                return
            
            try:
                user = self.auth_service.register(email, password)
                if user:
                    messagebox.showinfo("Success", "Account created successfully! You can now log in.")
                    reg_dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to create account. Email may already be registered.")
            except Exception as e:
                messagebox.showerror("Error", f"Registration failed: {str(e)}")
        
        create_btn = tk.Button(
            button_frame,
            text="CREATE ACCOUNT",
            command=submit_registration,
            font=('Arial', 12, 'bold'),
            bg=COLORS["primary"],
            fg="white",
            relief='raised',
            bd=2,
            padx=20,
            pady=10
        )
        create_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(
            button_frame,
            text="CANCEL",
            command=reg_dialog.destroy,
            font=('Arial', 12, 'bold'),
            bg=COLORS["secondary"],
            fg="white",
            relief='raised',
            bd=2,
            padx=20,
            pady=10
        )
        cancel_btn.pack(side=tk.LEFT)
        
        # Set focus and enter key binding
        email_entry.focus_set()
        reg_dialog.bind('<Return>', lambda e: submit_registration())
    
    def show_reset_password_dialog(self):
        """Show reset password dialog."""
        # Master passcode check
        master_passcode = simpledialog.askstring(
            "Master Passcode",
            "Enter master passcode:",
            show='*'
        )
        
        if master_passcode != "0713":
            messagebox.showerror("Error", "Invalid master passcode.")
            return
        
        # Get email to reset
        email = simpledialog.askstring(
            "Reset Password",
            "Enter email address to reset:"
        )
        
        if not email:
            return
        
        # Get new password
        new_password = simpledialog.askstring(
            "New Password",
            "Enter new password (8+ characters):",
            show='*'
        )
        
        if not new_password or len(new_password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long.")
            return
        
        try:
            success = self.auth_service.reset_password(email, new_password)
            if success:
                messagebox.showinfo("Success", "Password reset successfully!")
            else:
                messagebox.showerror("Error", "Failed to reset password. User may not exist.")
        except Exception as e:
            messagebox.showerror("Error", f"Reset failed: {str(e)}")
    
    def show_main_application(self):
        """Show the main application interface."""
        self.clear_window()

        services = {
            'customer_service': self.customer_service,
            'invoice_service': self.invoice_service,
            'auth_service': self.auth_service,
        }

        self.main_interface = TabbedMainInterface(
            self, self.root, self.current_user, services
        )
    
    def handle_logout(self):
        """Handle user logout."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            try:
                self.auth_service.logout()
                self.current_user = None
                self.show_login_interface()
            except Exception as e:
                logging.error(f"Logout error: {e}")
                self.show_login_interface()
    
    def run(self):
        """Run the application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()
        except Exception as e:
            logging.error(f"Application error: {e}")
            messagebox.showerror("Application Error", f"An error occurred: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        app = FullScreenLoginApp()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        messagebox.showerror("Startup Error", f"Could not start application: {e}")