import os
import sys
import tempfile
from unittest import mock
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "stubs"))

# Ensure project root is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


# Patch missing third-party modules before importing dialog
sys.modules.setdefault("tkcalendar", MagicMock(DateEntry=object))
sys.modules.setdefault("weasyprint", MagicMock())
sys.modules.setdefault("sqlalchemy", MagicMock())
sys.modules.setdefault("sqlalchemy.pool", MagicMock())
sys.modules.setdefault(
    "jinja2",
    MagicMock(
        Environment=MagicMock(
            return_value=MagicMock(
                get_template=MagicMock(return_value=MagicMock(render=lambda **kw: ""))
            )
        )
    ),
)

from automotive_invoice_manager.ui.components.widgets import PDFGenerationDialog
from automotive_invoice_manager.utils import pdf_generator


class DummyInvoice:
    template = "standard"
    id = 1
    customer = None


class DummyService:
    def get_invoice(self, invoice_id):
        return DummyInvoice()


class FakeEntry:
    def __init__(self):
        self.text = ""
        self.state = None

    def config(self, state=None):
        if state is not None:
            self.state = state

    def delete(self, start, end):
        self.text = ""

    def insert(self, index, text):
        self.text = text


# Helper PDF writer


def fake_generate_pdf(invoice, template, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(b"%PDF-1.4 test")
    return output_path


def create_dialog():
    with mock.patch(
        "tkinter.Toplevel.__init__", lambda self, parent=None: None
    ), mock.patch.object(
        PDFGenerationDialog, "_build_widgets", lambda self: None
    ), mock.patch(
        "tkinter.StringVar", lambda *a, **kw: MagicMock(get=lambda: "standard")
    ):
        return PDFGenerationDialog(None, DummyService(), 1)


def test_template_list_matches_directory():
    dialog = create_dialog()
    files = [
        f
        for f in os.listdir(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "templates", "pdf"
            )
        )
        if f.endswith(".html")
    ]
    expected = sorted([f.replace("invoice_", "").replace(".html", "") for f in files])
    assert sorted(dialog.templates) == expected


def test_select_output_updates_entry():
    dialog = create_dialog()
    entry = FakeEntry()
    with mock.patch(
        "automotive_invoice_manager.ui.components.widgets.filedialog.asksaveasfilename",
        return_value="/tmp/test.pdf",
    ):
        dialog._select_output(entry)
    assert dialog.output_path == "/tmp/test.pdf"
    assert entry.text == "/tmp/test.pdf"
    assert entry.state == "readonly"


def test_generate_writes_pdf(tmp_path):
    dialog = create_dialog()
    dialog.output_path = str(tmp_path / "out.pdf")
    dialog.invoice = DummyInvoice()
    dialog.template_var = MagicMock(get=lambda: "standard")
    with mock.patch(
        "automotive_invoice_manager.ui.components.widgets.pdf_generator.generate_pdf",
        side_effect=fake_generate_pdf,
    ) as gen, mock.patch("automotive_invoice_manager.ui.components.widgets.messagebox.showinfo") as info:
        dialog._generate()
    gen.assert_called_once()
    assert os.path.exists(dialog.output_path)
    with open(dialog.output_path, "rb") as f:
        assert f.read(4) == b"%PDF"
    info.assert_called()


def test_preview_spawns_viewer(tmp_path):
    dialog = create_dialog()
    dialog.invoice = DummyInvoice()
    dialog.template_var = MagicMock(get=lambda: "standard")
    temp_file = str(tmp_path / "preview.pdf")
    with mock.patch(
        "automotive_invoice_manager.ui.components.widgets.tempfile.mkstemp",
        return_value=(os.open(temp_file, os.O_RDWR | os.O_CREAT), temp_file),
    ), mock.patch(
        "automotive_invoice_manager.ui.components.widgets.pdf_generator.generate_pdf",
        side_effect=fake_generate_pdf,
    ) as gen, mock.patch(
        "automotive_invoice_manager.ui.components.widgets.platform.system", return_value="Linux"
    ), mock.patch(
        "automotive_invoice_manager.ui.components.widgets.subprocess.call"
    ) as call:
        dialog._preview()
    gen.assert_called_once()
    call.assert_called_with(("xdg-open", temp_file))


def test_print_sends_to_printer(tmp_path):
    dialog = create_dialog()
    dialog.output_path = str(tmp_path / "print.pdf")
    dialog.invoice = DummyInvoice()
    dialog.template_var = MagicMock(get=lambda: "standard")
    with mock.patch(
        "automotive_invoice_manager.ui.components.widgets.pdf_generator.generate_pdf",
        side_effect=fake_generate_pdf,
    ) as gen, mock.patch(
        "automotive_invoice_manager.ui.components.widgets.platform.system", return_value="Linux"
    ), mock.patch(
        "automotive_invoice_manager.ui.components.widgets.subprocess.call"
    ) as call, mock.patch(
        "automotive_invoice_manager.ui.components.widgets.messagebox.showinfo"
    ) as info:
        dialog._print()
    gen.assert_called_once()
    call.assert_called_with(["lp", dialog.output_path])
    info.assert_called()
