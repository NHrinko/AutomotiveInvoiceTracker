import os
import re

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "ui", "auth")
LOGIN_WINDOW_PATH = os.path.join(BASE_DIR, "login_window.py")


def _get_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def test_login_window_tab_order_and_enter_binding():
    lines = _get_lines(LOGIN_WINDOW_PATH)

    email_idx = next(i for i, l in enumerate(lines) if "self.email_entry" in l)
    password_idx = next(i for i, l in enumerate(lines) if "self.password_entry" in l)
    login_btn_idx = next(i for i, l in enumerate(lines) if "login_button" in l)
    register_btn_idx = next(i for i, l in enumerate(lines) if "register_button" in l)

    # Ensure tab order is logical
    assert email_idx < password_idx < login_btn_idx < register_btn_idx

    # Ensure Enter key triggers default login action
    assert any("<Return>" in l and "on_login" in l for l in lines)


def test_login_window_labels_and_button_text():
    lines = _get_lines(LOGIN_WINDOW_PATH)

    # Check entries and comboboxes have preceding labels
    for i, line in enumerate(lines):
        if "ttk.Entry" in line or "ttk.Combobox" in line:
            prev = "\n".join(lines[max(0, i - 3) : i])
            assert "ttk.Label" in prev, f"Input on line {i+1} lacks label"

    # Check all buttons have descriptive text
    for i, line in enumerate(lines):
        if "ttk.Button" in line:
            snippet = line + "".join(lines[i + 1 : i + 4])
            match = re.search(r"text\s*=\s*[\"\'](.+?)[\"\']", snippet)
            assert (
                match and match.group(1).strip()
            ), f"Button on line {i+1} missing text"
