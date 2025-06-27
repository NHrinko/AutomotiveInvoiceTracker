"""
Customer UI module - Your existing customer components
"""

# Import your existing components if available
try:
    from .customer_list import CustomerListFrame
except ImportError:
    CustomerListFrame = None

try:
    from .customer_form import CustomerFormDialog
except ImportError:
    CustomerFormDialog = None


__all__ = [
    'CustomerListFrame',
    'CustomerFormDialog'
]
