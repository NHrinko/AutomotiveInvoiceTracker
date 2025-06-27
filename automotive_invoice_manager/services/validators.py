"""Validation service for customer data."""

from __future__ import annotations

import re
import logging


class CustomerValidator:
    """Validator for customer data."""

    def __init__(self) -> None:
        """Compile regular expressions for validation."""
        self.email_pattern = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        # Allow digits, whitespace and common separators. The previous pattern
        # used double escapes which looked for the literal characters ``\d`` and
        # ``\s`` rather than digits and spaces. This corrected version properly
        # validates numbers like "+1 (555) 123-4567".
        self.phone_pattern = re.compile(r"^[\d\s\-\+\(\).]{10,20}$")

    def validate_name(self, name: str) -> tuple[bool, str]:
        """Validate customer name."""
        if not name or not name.strip():
            return False, "Name is required"

        if len(name.strip()) > 100:
            return False, "Name cannot exceed 100 characters"

        return True, ""

    def validate_email(self, email: str | None) -> tuple[bool, str]:
        """Validate email address."""
        if not email:
            return True, ""  # Email is optional

        if len(email) > 100:
            return False, "Email cannot exceed 100 characters"

        if not self.email_pattern.match(email):
            return False, "Please enter a valid email address"

        return True, ""

    def validate_phone(self, phone: str | None) -> tuple[bool, str]:
        """Validate phone number."""
        if not phone:
            return True, ""  # Phone is optional

        if len(phone) > 20:
            return False, "Phone number cannot exceed 20 characters"

        if not self.phone_pattern.match(phone):
            return False, "Please enter a valid phone number"

        return True, ""

    def validate_customer_data(self, data: dict) -> tuple[bool, dict[str, str]]:
        """Validate complete customer data."""
        errors = {}

        # Validate name
        valid, message = self.validate_name(data.get("name", ""))
        if not valid:
            errors["name"] = message

        # Validate email
        valid, message = self.validate_email(data.get("email", ""))
        if not valid:
            errors["email"] = message

        # Validate phone
        valid, message = self.validate_phone(data.get("phone", ""))
        if not valid:
            errors["phone"] = message

        # Validate text field lengths
        if data.get("address") and len(data["address"]) > 500:
            errors["address"] = "Address cannot exceed 500 characters"

        if data.get("notes") and len(data["notes"]) > 1000:
            errors["notes"] = "Notes cannot exceed 1000 characters"

        return len(errors) == 0, errors


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password length and complexity."""
    if password is None or len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return False, "Password must contain letters and numbers"
    return True, ""
