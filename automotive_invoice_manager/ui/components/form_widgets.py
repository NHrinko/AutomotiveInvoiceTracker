import tkinter as tk
from tkinter import ttk


class LabeledEntry(ttk.Frame):
    def __init__(self, master, label_text, **kwargs):
        super().__init__(master)
        ttk.Label(self, text=label_text).pack(side="left", padx=5)
        self.entry = ttk.Entry(self, **kwargs)
        self.entry.pack(side="left", fill="x", expand=True)
