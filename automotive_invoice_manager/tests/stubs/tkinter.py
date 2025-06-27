"""Minimal Tkinter stubs for tests."""

from unittest.mock import MagicMock


class Widget:
    def __init__(self, master=None, **kwargs):
        self.master = master
        self._text = kwargs.get("text", "")
        self.children = []

    def pack(self, *a, **kw):
        return None

    def grid(self, *a, **kw):
        return None

    def bind(self, *a, **kw):
        return None

    def config(self, **kw):
        if "text" in kw:
            self._text = kw["text"]

    def cget(self, opt):
        if opt == "text":
            return self._text
        return None


class Tk(Widget):
    def withdraw(self):
        pass

    def destroy(self):
        pass

    def event_generate(self, event):
        handler = getattr(self, "_event_" + event, None)
        if handler:
            handler(None)

    def bind(self, event, func):
        setattr(self, "_event_" + event, func)


class Toplevel(Tk):
    pass


class Entry(Widget):
    def delete(self, *a, **kw):
        pass

    def insert(self, index, text):
        self._text = text


class Button(Widget):
    def __init__(self, master=None, command=None, **kw):
        super().__init__(master, **kw)
        self.command = command

    def invoke(self):
        if self.command:
            self.command()


class Label(Widget):
    pass


class Frame(Widget):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)


class Spinbox(Widget):
    def __init__(self, master=None, from_=0, to=0, increment=1.0, **kw):
        super().__init__(master, **kw)
        self.value = 0

    def get(self):
        return str(self.value)

    def set(self, value):
        self.value = value


class StringVar:
    def __init__(self, value=""):
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value


class ttk:
    class Frame(Frame):
        pass

    class Label(Label):
        pass

    class Entry(Entry):
        pass

    class Button(Button):
        pass

    class Combobox(Widget):
        def __init__(self, master=None, values=None, textvariable=None, **kw):
            super().__init__(master, **kw)
            self.values = values or []
            self.textvariable = textvariable

        def configure(self, **kw):
            pass

    class LabelFrame(Frame):
        pass

    class Spinbox(Spinbox):
        pass

    class Treeview(Widget):
        def __init__(self, master=None, columns=(), show=None, **kw):
            super().__init__(master, **kw)
            self._columns = columns
            self._items = {}
            self._next = 1
            self._selection = []

        def heading(self, col, text):
            pass

        def column(self, col, width=None):
            pass

        def insert(self, parent, index, values=()):
            iid = f"I{self._next}"
            self._next += 1
            self._items[iid] = values
            return iid

        def item(self, item, option=None):
            if option == "values":
                return self._items[item]
            return None

        def selection_set(self, item):
            self._selection = [item]

        def selection(self):
            return self._selection

        def delete(self, *items):
            for i in items:
                self._items.pop(i, None)

        def get_children(self):
            return list(self._items.keys())

        def bind(self, event, func):
            setattr(self, "_event_" + event, func)

        def event_generate(self, event):
            handler = getattr(self, "_event_" + event, None)
            if handler:
                handler(None)


messagebox = MagicMock(
    askyesno=MagicMock(return_value=True), showerror=MagicMock(), showinfo=MagicMock()
)

filedialog = MagicMock(
    askopenfilename=MagicMock(return_value=""),
    asksaveasfilename=MagicMock(return_value=""),
)
