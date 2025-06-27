# automotive_invoice_manager/ui/logo_tab.py - Logo Upload Tab with Clear Import Button

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from pathlib import Path
import logging

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from .theme import COLORS, FONTS
from .tooltips import add_tooltip

# Add missing color if not defined
if 'muted' not in COLORS:
    COLORS['muted'] = '#666666'
if 'danger' not in COLORS:
    COLORS['danger'] = '#dc3545'
if 'success' not in COLORS:
    COLORS['success'] = '#28a745'

logger = logging.getLogger(__name__)


class LogoTab(tk.Frame):
    """Tab for uploading and managing application logo."""

    def __init__(self, parent, main_interface):
        super().__init__(parent, bg=COLORS["background"])
        self.main_interface = main_interface
        self.current_logo_path = None
        self.preview_image = None
        
        # Define assets directory path and default logo
        self.assets_dir = Path(__file__).parent.parent / "assets"
        self.default_logo_path = Path(r"C:\Users\nickh\OneDrive\Desktop\OfflineManager\automotive_invoice_manager\assets\logo.png")
        self.logo_path = self.assets_dir / "logo.png"
        
        # Use your specific default if our logo doesn't exist
        if not self.logo_path.exists() and self.default_logo_path.exists():
            self.logo_path = self.default_logo_path
        
        # Ensure assets directory exists
        self.assets_dir.mkdir(exist_ok=True)
        
        self.setup_ui()
        self.load_current_logo()

    def setup_ui(self):
        """Setup the logo management interface with two-column layout."""
        # Header
        header_label = tk.Label(
            self,
            text="Logo Management",
            font=FONTS["lg"],
            fg=COLORS["text"],
            bg=COLORS["background"],
        )
        header_label.pack(anchor=tk.W, padx=20, pady=(20, 10))

        # Main content frame with two columns
        main_frame = tk.Frame(self, bg=COLORS["background"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Configure main frame for two columns
        main_frame.columnconfigure(0, weight=1)  # Left column (preview)
        main_frame.columnconfigure(1, weight=1)  # Right column (upload)
        main_frame.rowconfigure(0, weight=1)     # Make rows expandable

        # LEFT COLUMN: Current logo preview
        left_frame = tk.Frame(main_frame, bg=COLORS["background"])
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.create_current_logo_section(left_frame)
        
        # RIGHT COLUMN: Upload options and instructions
        right_frame = tk.Frame(main_frame, bg=COLORS["background"])
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Create paned window for upload and instructions in right column
        right_paned = tk.PanedWindow(right_frame, orient=tk.VERTICAL, bg=COLORS["background"])
        right_paned.pack(fill=tk.BOTH, expand=True)
        
        # Upload section in top pane of right column
        upload_pane = tk.Frame(right_paned, bg=COLORS["background"])
        right_paned.add(upload_pane, minsize=350)
        self.create_upload_section(upload_pane)
        
        # Instructions section in bottom pane of right column
        instructions_pane = tk.Frame(right_paned, bg=COLORS["background"])
        right_paned.add(instructions_pane, minsize=150)
        self.create_instructions_section(instructions_pane)

    def create_current_logo_section(self, parent):
        """Create current logo display section optimized for left column."""
        current_frame = tk.LabelFrame(
            parent,
            text="Current Logo Preview",
            font=FONTS["base"],
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        current_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create container for logo and info
        container = tk.Frame(current_frame, bg=COLORS["background"])
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=0)
        container.rowconfigure(2, weight=0)

        # Logo preview frame - takes most of the space
        preview_container = tk.Frame(container, bg=COLORS["background"])
        preview_container.grid(row=0, column=0, sticky="nsew", pady=(0, 15))

        self.preview_frame = tk.Frame(preview_container, bg=COLORS["section"], relief="sunken", bd=2)
        self.preview_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Logo info section
        info_container = tk.Frame(container, bg=COLORS["background"])
        info_container.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        info_container.columnconfigure(0, weight=1)

        self.logo_info_label = tk.Label(
            info_container,
            text="No logo information available",
            font=FONTS["base"],
            fg=COLORS["text"],
            bg=COLORS["background"],
            wraplength=300,
            justify=tk.CENTER
        )
        self.logo_info_label.grid(row=0, column=0, pady=5, sticky="ew")

        # Control buttons section
        control_container = tk.Frame(container, bg=COLORS["background"])
        control_container.grid(row=2, column=0, sticky="ew")
        control_container.columnconfigure(0, weight=1)
        control_container.columnconfigure(1, weight=1)

        # Refresh button
        refresh_btn = tk.Button(
            control_container,
            text="🔄 Refresh",
            command=self.load_current_logo,
            font=FONTS["base"],
            bg=COLORS["secondary"],
            fg="white",
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        refresh_btn.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        add_tooltip(refresh_btn, "Refresh logo display")

        # Reset to default button
        reset_btn = tk.Button(
            control_container,
            text="🔄 Reset Default",
            command=self.reset_to_default,
            font=FONTS["base"],
            bg=COLORS["highlight"],
            fg="white",
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        reset_btn.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")
        add_tooltip(reset_btn, "Remove custom logo and use default logo")

    def create_upload_section(self, parent):
        """Create logo upload section optimized for right column."""
        upload_frame = tk.LabelFrame(
            parent,
            text="Logo Import Options",
            font=FONTS["base"],
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        upload_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Main container for upload content
        main_container = tk.Frame(upload_frame, bg=COLORS["background"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # === CLEAR IMPORT BUTTON SECTION ===
        # Clear import section (most prominent)
        clear_import_frame = tk.Frame(main_container, bg=COLORS["success"], relief="raised", bd=3)
        clear_import_frame.pack(fill=tk.X, pady=(0, 15))

        # Clear import title
        clear_title = tk.Label(
            clear_import_frame,
            text="🚀 QUICK LOGO IMPORT",
            font=('Arial', 12, 'bold'),
            fg="white",
            bg=COLORS["success"]
        )
        clear_title.pack(pady=(8, 3))

        # Clear import description
        clear_desc = tk.Label(
            clear_import_frame,
            text="One-click: select and apply instantly!",
            font=('Arial', 9),
            fg="white",
            bg=COLORS["success"],
            wraplength=300
        )
        clear_desc.pack(pady=(0, 8))

        # Large clear import button
        self.clear_import_btn = tk.Button(
            clear_import_frame,
            text="📸 IMPORT NEW LOGO\n(Select & Apply)",
            command=self.clear_import_logo,
            font=('Arial', 11, 'bold'),
            bg="white",
            fg=COLORS["success"],
            relief="raised",
            bd=3,
            pady=12,
            cursor="hand2",
            wraplength=200,
            justify=tk.CENTER,
            activebackground=COLORS["success"],
            activeforeground="white"
        )
        self.clear_import_btn.pack(pady=(0, 10), padx=15, fill=tk.X)
        add_tooltip(self.clear_import_btn, "Click to select and immediately apply a new logo image")

        # === SEPARATOR ===
        separator_frame = tk.Frame(main_container, bg=COLORS["background"], height=2)
        separator_frame.pack(fill=tk.X, pady=8)
        
        separator_line = tk.Frame(separator_frame, bg=COLORS["muted"], height=1)
        separator_line.pack(fill=tk.X)

        # Alternative text
        alt_label = tk.Label(
            main_container,
            text="── OR use advanced options ──",
            font=('Arial', 9, 'italic'),
            fg=COLORS["muted"],
            bg=COLORS["background"]
        )
        alt_label.pack(pady=3)

        # === ADVANCED OPTIONS ===
        # Advanced upload instructions
        instruction_text = (
            "ADVANCED: Browse → Upload\n"
            "Step 1: Browse for image file\n"
            "Step 2: Upload to apply\n\n"
            "Formats: PNG, JPG, GIF, BMP\n"
            "Max size: 10MB"
        )
        
        instruction_label = tk.Label(
            main_container,
            text=instruction_text,
            font=('Arial', 9),
            fg=COLORS["text"],
            bg=COLORS["background"],
            wraplength=300,
            justify=tk.LEFT
        )
        instruction_label.pack(anchor=tk.W, pady=(8, 5))

        # File path display
        self.file_path_var = tk.StringVar(value="No file selected")
        path_frame = tk.Frame(main_container, bg=COLORS["section"], relief="sunken", bd=1)
        path_frame.pack(fill=tk.X, pady=(0, 8))
        path_frame.columnconfigure(1, weight=1)

        tk.Label(
            path_frame,
            text="File:",
            font=('Arial', 9),
            bg=COLORS["section"],
            fg=COLORS["text"]
        ).grid(row=0, column=0, padx=8, pady=3, sticky=tk.W)

        self.path_label = tk.Label(
            path_frame,
            textvariable=self.file_path_var,
            font=('Arial', 9),
            bg=COLORS["section"],
            fg=COLORS["muted"],
            anchor=tk.W
        )
        self.path_label.grid(row=0, column=1, padx=(0, 8), pady=3, sticky=tk.EW)

        # Advanced button container
        button_container = tk.Frame(main_container, bg=COLORS["background"])
        button_container.pack(fill=tk.X, pady=(0, 8))

        # Configure button container for responsive layout
        button_container.columnconfigure(0, weight=1)
        button_container.columnconfigure(1, weight=1)

        # Browse button
        browse_btn = tk.Button(
            button_container,
            text="🔍 BROWSE\nFOR IMAGE",
            command=self.browse_for_logo,
            font=('Arial', 9, 'bold'),
            bg=COLORS["primary"],
            fg="white",
            relief="raised",
            bd=2,
            pady=8,
            cursor="hand2",
            wraplength=80,
            justify=tk.CENTER
        )
        browse_btn.grid(row=0, column=0, padx=(0, 4), pady=2, sticky="ew")
        add_tooltip(browse_btn, "Click to select a logo image file")

        # Upload button (enabled only when file selected)
        self.upload_btn = tk.Button(
            button_container,
            text="📤 UPLOAD\nLOGO",
            command=self.upload_selected_logo,
            font=('Arial', 9, 'bold'),
            bg=COLORS["secondary"],
            fg="white",
            relief="raised",
            bd=2,
            pady=8,
            cursor="hand2",
            state="disabled",
            wraplength=80,
            justify=tk.CENTER
        )
        self.upload_btn.grid(row=0, column=1, padx=(4, 0), pady=2, sticky="ew")
        add_tooltip(self.upload_btn, "Upload the selected image as your new logo")

        # Selected file info
        self.selected_file_path = None

        # Status label
        self.status_label = tk.Label(
            main_container,
            text="",
            font=('Arial', 9),
            fg=COLORS["text"],
            bg=COLORS["background"],
            wraplength=300,
            justify=tk.LEFT
        )
        self.status_label.pack(anchor=tk.W, pady=(5, 0))

    def clear_import_logo(self):
        """Clear import functionality - one-click logo import."""
        try:
            # File dialog with better filters
            file_types = [
                ("All Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.PNG *.JPG *.JPEG *.GIF *.BMP"),
                ("PNG files", "*.png *.PNG"),
                ("JPEG files", "*.jpg *.jpeg *.JPG *.JPEG"),
                ("GIF files", "*.gif *.GIF"),
                ("BMP files", "*.bmp *.BMP"),
                ("All files", "*.*")
            ]
            
            # Start browse in user's Pictures folder or Desktop
            initial_dirs = [
                os.path.expanduser("~/Pictures"),
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~")
            ]
            
            initial_dir = os.path.expanduser("~")
            for directory in initial_dirs:
                if os.path.exists(directory):
                    initial_dir = directory
                    break
            
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title="Select Logo Image to Import",
                filetypes=file_types,
                initialdir=initial_dir
            )
            
            if not file_path:
                # User cancelled
                self.status_label.config(text="Import cancelled", fg=COLORS["muted"])
                return
            
            # Validate the selected file
            if not self.validate_image_file(file_path):
                return
            
            # Show import progress
            self.status_label.config(text="⏳ Importing logo...", fg=COLORS["text"])
            self.clear_import_btn.config(state="disabled", text="⏳ IMPORTING...")
            self.update()
            
            # Create backup of current logo if it exists
            if self.logo_path.exists():
                backup_path = self.logo_path.with_suffix('.png.backup')
                shutil.copy2(self.logo_path, backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            # Ensure assets directory exists
            self.assets_dir.mkdir(exist_ok=True)
            
            # Copy new logo to assets directory
            shutil.copy2(file_path, self.logo_path)
            
            # Clear any existing file selection in advanced options
            self.selected_file_path = None
            self.file_path_var.set("No file selected")
            self.path_label.config(fg=COLORS["muted"])
            self.upload_btn.config(state="disabled")
            
            # Reload preview
            self.load_current_logo()
            
            # Show success status
            file_name = os.path.basename(file_path)
            self.status_label.config(
                text=f"✅ Logo imported successfully: {file_name}",
                fg=COLORS["success"]
            )
            
            # Re-enable import button
            self.clear_import_btn.config(
                state="normal", 
                text="📸 IMPORT NEW LOGO\n(Select & Apply Instantly)"
            )
            
            # Show success message
            messagebox.showinfo(
                "Logo Imported Successfully!",
                f"Your new logo '{file_name}' has been imported and applied!\n\n"
                "The new logo will appear:\n"
                "• In the login screen on next startup\n"
                "• Throughout the application interface\n"
                "• In generated PDF invoices\n"
                "• When the app is moved to other computers"
            )
            
        except PermissionError:
            error_msg = "Permission denied. Cannot write to assets directory.\n\nTry running as administrator."
            self.status_label.config(text=f"❌ {error_msg}", fg=COLORS["danger"])
            self.clear_import_btn.config(state="normal", text="📸 IMPORT NEW LOGO\n(Select & Apply Instantly)")
            messagebox.showerror("Permission Error", error_msg)
            
        except Exception as e:
            logger.error(f"Error importing logo: {e}")
            error_msg = f"Failed to import logo: {str(e)}"
            self.status_label.config(text=f"❌ {error_msg}", fg=COLORS["danger"])
            self.clear_import_btn.config(state="normal", text="📸 IMPORT NEW LOGO\n(Select & Apply Instantly)")
            messagebox.showerror("Import Error", error_msg)

    def create_instructions_section(self, parent):
        """Create compact instructions section for right column."""
        instructions_frame = tk.LabelFrame(
            parent,
            text="Quick Reference",
            font=FONTS["base"],
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        instructions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        instructions_text = """
QUICK REFERENCE:

🚀 RECOMMENDED: Use "Quick Import" button
   • One click selects and applies logo instantly
   • No multiple steps needed

📁 SUPPORTED FORMATS:
   • PNG (best quality) • JPG/JPEG • GIF • BMP
   • Max size: 10MB • Recommended: 400x400px

🔄 RESET: Use "Reset Default" to remove custom logo

✅ EFFECTS: New logo appears in:
   • Login screen (next startup)
   • Application interface
   • PDF invoices
   • When moved to other computers

⚠️ TROUBLESHOOTING:
   • Click "Refresh" if logo doesn't appear
   • Square images work best
   • Run as admin if permission errors
        """

        # Create scrollable text widget
        text_frame = tk.Frame(instructions_frame, bg=COLORS["background"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('Arial', 9),
            bg=COLORS["section"],
            fg=COLORS["text"],
            relief="sunken",
            bd=1,
            padx=8,
            pady=8
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=scrollbar.set)

        # Insert instructions
        text_widget.insert(tk.END, instructions_text)
        text_widget.configure(state=tk.DISABLED)  # Make read-only

    def load_current_logo(self):
        """Load and display the current logo in left column preview."""
        # Clear any existing preview
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        try:
            # Determine which logo to display
            logo_to_display = None
            logo_source = ""
            
            if self.logo_path.exists():
                logo_to_display = self.logo_path
                logo_source = "Custom Logo"
            elif self.default_logo_path.exists():
                logo_to_display = self.default_logo_path
                logo_source = "Default Logo"
            
            if logo_to_display and PIL_AVAILABLE:
                try:
                    # Load and resize image for preview
                    img = Image.open(logo_to_display)
                    
                    # Calculate preview size (max 250x250 for column view)
                    max_size = 250
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                    
                    self.preview_image = ImageTk.PhotoImage(img)
                    
                    # Center the logo in the preview frame
                    logo_label = tk.Label(
                        self.preview_frame,
                        image=self.preview_image,
                        bg=COLORS["section"]
                    )
                    logo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                    
                    # Show original dimensions
                    original_img = Image.open(logo_to_display)
                    dimensions = f"{original_img.width}x{original_img.height}"
                    file_size = logo_to_display.stat().st_size
                    if file_size > 1024 * 1024:  # > 1MB
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"
                    else:
                        size_str = f"{file_size / 1024:.1f} KB"
                    
                    info_text = f"{logo_source}\n{logo_to_display.name}\n{dimensions} | {size_str}"

                except Exception as e:
                    logger.error(f"Error loading image: {e}")
                    fallback_label = tk.Label(
                        self.preview_frame,
                        text=f"📷\n\n{logo_source}\n\n{logo_to_display.name}\n\n(Preview not available)",
                        font=('Arial', 10),
                        fg=COLORS["text"],
                        bg=COLORS["section"],
                        justify=tk.CENTER
                    )
                    fallback_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                    
                    file_size = logo_to_display.stat().st_size
                    if file_size > 1024 * 1024:  # > 1MB
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"
                    else:
                        size_str = f"{file_size / 1024:.1f} KB"
                    
                    info_text = f"{logo_source}\n{logo_to_display.name}\n{size_str}"

            else:
                # No logo file exists anywhere
                no_logo_label = tk.Label(
                    self.preview_frame,
                    text="📷\n\nNo Logo Found\n\nUse Quick Import\nto add a logo!",
                    font=('Arial', 12),
                    fg=COLORS["muted"],
                    bg=COLORS["section"],
                    justify=tk.CENTER
                )
                no_logo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                
                info_text = "No logo file found\nUse Quick Import to add one!"

            self.logo_info_label.config(text=info_text)
            
            # Show helpful status
            if logo_to_display == self.default_logo_path:
                self.status_label.config(text="Default logo active - Use Quick Import for custom logo", fg=COLORS["muted"])
            elif logo_to_display == self.logo_path:
                self.status_label.config(text="✅ Custom logo active", fg=COLORS["success"])
            else:
                self.status_label.config(text="No logo - Use Quick Import to add one!", fg=COLORS["muted"])
            
        except Exception as e:
            logger.error(f"Error loading logo: {e}")
            
            error_label = tk.Label(
                self.preview_frame,
                text="❌\n\nError Loading Logo\n\nCheck file permissions\nor try refreshing",
                font=('Arial', 10),
                fg=COLORS["danger"],
                bg=COLORS["section"],
                justify=tk.CENTER
            )
            error_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
            self.logo_info_label.config(text=f"Error: {str(e)}")
            self.status_label.config(text=f"❌ Error loading logo: {e}", fg=COLORS["danger"])

    def browse_for_logo(self):
        """Browse for logo file and display selection (advanced option)."""
        try:
            # File dialog with better filters
            file_types = [
                ("All Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.PNG *.JPG *.JPEG *.GIF *.BMP"),
                ("PNG files", "*.png *.PNG"),
                ("JPEG files", "*.jpg *.jpeg *.JPG *.JPEG"),
                ("GIF files", "*.gif *.GIF"),
                ("BMP files", "*.bmp *.BMP"),
                ("All files", "*.*")
            ]
            
            # Start browse in user's Pictures folder or Desktop
            initial_dirs = [
                os.path.expanduser("~/Pictures"),
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~")
            ]
            
            initial_dir = os.path.expanduser("~")
            for directory in initial_dirs:
                if os.path.exists(directory):
                    initial_dir = directory
                    break
            
            file_path = filedialog.askopenfilename(
                title="Select Logo Image File",
                filetypes=file_types,
                initialdir=initial_dir
            )
            
            if file_path:
                self.selected_file_path = file_path
                self.file_path_var.set(os.path.basename(file_path))
                self.path_label.config(fg=COLORS["text"])
                self.upload_btn.config(state="normal")
                
                # Show file info
                file_size = os.path.getsize(file_path)
                if file_size > 1024 * 1024:  # > 1MB
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
                else:
                    size_str = f"{file_size / 1024:.1f} KB"
                
                self.status_label.config(
                    text=f"📁 Selected: {os.path.basename(file_path)} ({size_str})",
                    fg=COLORS["text"]
                )
                
                # Quick validation
                if self.validate_image_file(file_path):
                    self.status_label.config(
                        text=f"✅ Ready to upload: {os.path.basename(file_path)} ({size_str})",
                        fg=COLORS["text"]
                    )
                else:
                    self.upload_btn.config(state="disabled")
            else:
                self.status_label.config(text="No file selected", fg=COLORS["muted"])
                
        except Exception as e:
            logger.error(f"Error browsing for logo: {e}")
            self.status_label.config(text=f"❌ Error browsing files: {e}", fg=COLORS["danger"])

    def upload_selected_logo(self):
        """Upload the selected logo file (advanced option)."""
        if not self.selected_file_path:
            messagebox.showerror("No File Selected", "Please browse and select an image file first.")
            return
        
        try:
            self.status_label.config(text="⏳ Uploading logo...", fg=COLORS["text"])
            self.update()
            
            # Validate file again
            if not self.validate_image_file(self.selected_file_path):
                return
            
            # Create backup of current logo if it exists
            if self.logo_path.exists():
                backup_path = self.logo_path.with_suffix('.png.backup')
                shutil.copy2(self.logo_path, backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            # Ensure assets directory exists
            self.assets_dir.mkdir(exist_ok=True)
            
            # Copy new logo to assets directory
            shutil.copy2(self.selected_file_path, self.logo_path)
            
            # Clear selection
            self.selected_file_path = None
            self.file_path_var.set("No file selected")
            self.path_label.config(fg=COLORS["muted"])
            self.upload_btn.config(state="disabled")
            
            # Reload preview
            self.load_current_logo()
            
            self.status_label.config(
                text=f"✅ Logo uploaded successfully!",
                fg=COLORS["success"]
            )
            
            messagebox.showinfo(
                "Logo Updated",
                "Logo has been updated successfully!\n\n"
                "The new logo will appear:\n"
                "• In the login screen on next startup\n"
                "• Throughout the application interface\n"
                "• In generated PDF invoices\n"
                "• When the app is moved to other computers"
            )
            
        except PermissionError:
            error_msg = "Permission denied. Cannot write to assets directory.\n\nTry running as administrator."
            self.status_label.config(text=f"❌ {error_msg}", fg=COLORS["danger"])
            messagebox.showerror("Permission Error", error_msg)
            
        except Exception as e:
            logger.error(f"Error uploading logo: {e}")
            error_msg = f"Failed to upload logo: {str(e)}"
            self.status_label.config(text=f"❌ {error_msg}", fg=COLORS["danger"])
            messagebox.showerror("Upload Error", error_msg)

    def reset_to_default(self):
        """Reset logo to default."""
        try:
            if messagebox.askyesno("Reset to Default", "Are you sure you want to reset to the default logo?\n\nThis will remove any custom logo you've uploaded."):
                if self.logo_path.exists():
                    # Create backup before removing
                    backup_path = self.logo_path.with_suffix('.png.removed')
                    shutil.move(self.logo_path, backup_path)
                    logger.info(f"Moved custom logo to backup: {backup_path}")
                
                self.load_current_logo()
                self.status_label.config(text="✅ Reset to default logo", fg=COLORS["success"])
                messagebox.showinfo("Reset Complete", "Logo has been reset to default.")
                
        except Exception as e:
            logger.error(f"Error resetting logo: {e}")
            self.status_label.config(text=f"❌ Error resetting logo: {e}", fg=COLORS["danger"])

    def validate_image_file(self, file_path):
        """Validate the selected image file."""
        try:
            if not os.path.exists(file_path):
                messagebox.showerror("File Error", "Selected file does not exist.")
                return False
            
            # Check file size (10MB limit)
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                messagebox.showerror("File Too Large", "File size must be less than 10MB.\n\nPlease select a smaller image.")
                return False
            
            # Check if it's a valid image using PIL
            if PIL_AVAILABLE:
                try:
                    with Image.open(file_path) as img:
                        img.verify()  # Verify it's a valid image
                    return True
                except Exception as e:
                    messagebox.showerror("Invalid Image", f"Selected file is not a valid image:\n{str(e)}")
                    return False
            else:
                # Basic extension check if PIL not available
                valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
                file_ext = Path(file_path).suffix.lower()
                if file_ext not in valid_extensions:
                    messagebox.showerror("Invalid File", "Please select a valid image file (PNG, JPG, GIF, BMP).")
                    return False
                return True
                
        except Exception as e:
            logger.error(f"Error validating image: {e}")
            messagebox.showerror("Validation Error", f"Error validating image file:\n{str(e)}")
            return False

    def upload_logo(self):
        """Legacy method - now redirects to clear import."""
        self.clear_import_logo()