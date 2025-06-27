"""Simple login window for authentication UI tests."""

import tkinter as tk
from tkinter import ttk


class LoginWindow(tk.Tk):
    """Standalone login window widget."""

    def __init__(self):
        super().__init__()
        self.title("Login")
        self._build_widgets()
        # Bind Enter key to default login action
        self.bind("<Return>", lambda e: self.on_login())

    def _build_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Email
        ttk.Label(frame, text="Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(frame)
        self.email_entry.grid(row=0, column=1, pady=5)

        # Password
        ttk.Label(frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        # Buttons
        self.login_button = ttk.Button(frame, text="Login", command=self.on_login)
        self.login_button.grid(row=2, column=0, padx=(0, 10), pady=10)

        self.register_button = ttk.Button(
            frame, text="Create Account", command=self.on_register
        )
        self.register_button.grid(row=2, column=1, pady=10)

    # Stub handlers used by tests
    def on_login(self):
        pass

    def on_register(self):
        pass


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
