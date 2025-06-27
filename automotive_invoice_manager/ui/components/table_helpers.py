"""Helper utilities for creating common table widgets and context menus."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .table_widget import EnhancedTableWidget


def create_table_with_scrollbars(
    parent: tk.Widget,
    *,
    columns: tuple[str, ...],
    column_configs: dict[str, tuple[str, int, str]],
    sort_callback=None,
    selectmode: str = "extended",
) -> EnhancedTableWidget:
    """Create an ``EnhancedTableWidget`` with scrollbars and basic column setup."""
    tree = EnhancedTableWidget(parent, columns=columns, selectmode=selectmode)

    for col, (heading, width, anchor) in column_configs.items():
        if sort_callback is not None:
            tree.heading(col, text=heading, command=lambda c=col: sort_callback(c))
        else:
            tree.heading(col, text=heading)
        tree.column(col, width=width, anchor=anchor)

    v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
    h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    tree.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")

    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)

    return tree


def create_context_menu(parent: tk.Widget, items: list[tuple[str, callable] | None]) -> tk.Menu:
    """Create a context menu from (label, command) tuples.

    ``None`` values in ``items`` produce menu separators.
    """
    menu = tk.Menu(parent, tearoff=0)
    for item in items:
        if item is None:
            menu.add_separator()
            continue
        label, command = item
        menu.add_command(label=label, command=command)
    return menu

