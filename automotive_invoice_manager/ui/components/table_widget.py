import tkinter as tk
from tkinter import ttk


class EnhancedTableWidget(ttk.Treeview):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self["show"] = "headings"
