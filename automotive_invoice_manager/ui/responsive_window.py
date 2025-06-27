
# automotive_invoice_manager/ui/responsive_window.py - Window Management Fix

import tkinter as tk
import platform
import logging

logger = logging.getLogger(__name__)


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
            
            # Set default window size (80% of usable screen)
            default_width = int(screen_width * 0.8)
            default_height = int(usable_height * 0.8)
            
            # Center the window
            x = (screen_width - default_width) // 2
            y = (usable_height - default_height) // 2
            
            # Apply geometry
            self.root.geometry(f"{default_width}x{default_height}+{x}+{y}")
            
            # Configure background
            self.root.configure(bg="#F7F9FC")
            
            # Bind window events
            self.setup_window_events()
            
            logger.info(f"Window setup: {default_width}x{default_height}+{x}+{y}")
            logger.info(f"Screen: {screen_width}x{screen_height}, Usable: {screen_width}x{usable_height}")
            
        except Exception as e:
            logger.error(f"Error setting up responsive window: {e}")
            # Fallback to basic window setup
            self.root.geometry("1200x800")
            self.root.minsize(800, 600)
    
    def get_taskbar_height(self):
        """Calculate taskbar height based on platform."""
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows taskbar is typically 40-48 pixels
                return 48
            elif system == "Darwin":  # macOS
                # macOS dock and menu bar combined
                return 70
            else:  # Linux/Unix
                # Linux panel height varies
                return 40
                
        except Exception:
            # Default fallback
            return 40
    
    def setup_window_events(self):
        """Setup window event handlers for responsive behavior."""
        # Bind keyboard shortcuts
        self.root.bind('<F11>', self.toggle_maximize)
        self.root.bind('<Escape>', self.restore_window)
        self.root.bind('<Control-minus>', self.zoom_out)
        self.root.bind('<Control-plus>', self.zoom_in)
        self.root.bind('<Control-0>', self.reset_zoom)
        
        # Bind window state events
        self.root.bind('<Configure>', self.on_window_configure)
        
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
                logger.info("Window maximized (respecting taskbar)")
                
            else:
                # Restore to saved geometry
                if self.saved_geometry:
                    self.root.geometry(self.saved_geometry)
                else:
                    self.root.geometry("1200x800")
                self.is_maximized = False
                logger.info("Window restored to normal size")
                
        except Exception as e:
            logger.error(f"Error toggling maximize: {e}")
    
    def restore_window(self, event=None):
        """Restore window to normal size."""
        if self.is_maximized:
            self.toggle_maximize()
    
    def zoom_in(self, event=None):
        """Increase window size by 10%."""
        try:
            current_geo = self.root.geometry()
            width, height, x, y = self.parse_geometry(current_geo)
            
            new_width = int(width * 1.1)
            new_height = int(height * 1.1)
            
            # Check screen bounds
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight() - self.get_taskbar_height()
            
            if new_width <= screen_width and new_height <= screen_height:
                # Center the enlarged window
                new_x = max(0, (screen_width - new_width) // 2)
                new_y = max(0, (screen_height - new_height) // 2)
                
                self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
                logger.info(f"Zoomed in to: {new_width}x{new_height}")
            
        except Exception as e:
            logger.error(f"Error zooming in: {e}")
    
    def zoom_out(self, event=None):
        """Decrease window size by 10%."""
        try:
            current_geo = self.root.geometry()
            width, height, x, y = self.parse_geometry(current_geo)
            
            new_width = int(width * 0.9)
            new_height = int(height * 0.9)
            
            # Check minimum size
            min_width = 800
            min_height = 600
            
            if new_width >= min_width and new_height >= min_height:
                # Center the smaller window
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight() - self.get_taskbar_height()
                
                new_x = (screen_width - new_width) // 2
                new_y = (screen_height - new_height) // 2
                
                self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
                logger.info(f"Zoomed out to: {new_width}x{new_height}")
            
        except Exception as e:
            logger.error(f"Error zooming out: {e}")
    
    def reset_zoom(self, event=None):
        """Reset window to default size."""
        try:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight() - self.get_taskbar_height()
            
            default_width = int(screen_width * 0.8)
            default_height = int(screen_height * 0.8)
            
            x = (screen_width - default_width) // 2
            y = (screen_height - default_height) // 2
            
            self.root.geometry(f"{default_width}x{default_height}+{x}+{y}")
            self.is_maximized = False
            logger.info(f"Reset zoom to: {default_width}x{default_height}")
            
        except Exception as e:
            logger.error(f"Error resetting zoom: {e}")
    
    def on_window_configure(self, event):
        """Handle window configure events."""
        # Only handle events for the root window
        if event.widget == self.root:
            # Check if window is too small and adjust if needed
            current_width = self.root.winfo_width()
            current_height = self.root.winfo_height()
            
            min_width = 800
            min_height = 600
            
            if current_width < min_width or current_height < min_height:
                self.root.after_idle(lambda: self.root.minsize(min_width, min_height))
    
    def on_window_close(self):
        """Handle window close event."""
        try:
            # Save window state for next startup
            geometry = self.root.geometry()
            logger.info(f"Saving window geometry: {geometry}")
            
            # Close the application
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error closing window: {e}")
            self.root.destroy()
    
    def parse_geometry(self, geometry_string):
        """Parse geometry string into components."""
        try:
            # Format: "widthxheight+x+y"
            size_part, position_part = geometry_string.split('+', 1)
            width, height = map(int, size_part.split('x'))
            
            if '+' in position_part:
                x, y = map(int, position_part.split('+'))
            else:
                x, y = map(int, position_part.split('-'))
                y = -y  # Handle negative y coordinates
            
            return width, height, x, y
            
        except Exception as e:
            logger.error(f"Error parsing geometry: {e}")
            return 1200, 800, 100, 100  # Default values
    
    def get_window_info(self):
        """Get current window information for debugging."""
        try:
            return {
                'geometry': self.root.geometry(),
                'width': self.root.winfo_width(),
                'height': self.root.winfo_height(),
                'x': self.root.winfo_x(),
                'y': self.root.winfo_y(),
                'screen_width': self.root.winfo_screenwidth(),
                'screen_height': self.root.winfo_screenheight(),
                'is_maximized': self.is_maximized,
                'saved_geometry': self.saved_geometry,
                'taskbar_height': self.get_taskbar_height()
            }
        except Exception as e:
            logger.error(f"Error getting window info: {e}")
            return {}
