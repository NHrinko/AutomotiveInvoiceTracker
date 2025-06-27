import tkinter as tk
from tkinter import ttk

class PopoutNotebook(ttk.Notebook):
    """Notebook that pops tabs into independent windows."""

    def __init__(self, master=None, preview_tabs=None, **kwargs):
        super().__init__(master, **kwargs)
        self.preview_tabs = set(preview_tabs or [])
        self._popouts = {}
        self.bind("<<NotebookTabChanged>>", self._maybe_popout)

    def _maybe_popout(self, event):
        tab_id = self.select()
        tab_text = self.tab(tab_id, "text")
        if tab_text in self.preview_tabs:
            return
        if tab_id in self._popouts:
            # already popped out, just raise window
            win, _frame, _index, _text = self._popouts[tab_id]
            win.lift()
            return
        frame = self.nametowidget(tab_id)
        index = self.index(tab_id)
        text = tab_text
        self.forget(tab_id)
        win = tk.Toplevel(self)
        win.title(text)
        frame.pack(fill=tk.BOTH, expand=True)
        def on_close(f=frame, idx=index, txt=text, tid=tab_id):
            f.pack_forget()
            self.insert(idx, f, text=txt)
            self._popouts.pop(tid, None)
        win.protocol("WM_DELETE_WINDOW", on_close)
        self._popouts[tab_id] = (win, frame, index, text)
