"""PDF generation utilities using WeasyPrint."""

from __future__ import annotations

import os
import uuid
import jinja2
import weasyprint
from .config import Config

TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "templates", "pdf"
)


def render_invoice_html(invoice: "Invoice", template_name: str = "standard") -> str:
    """Render invoice HTML from Jinja2 template."""
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
    try:
        template = env.get_template(f"invoice_{template_name}.html")
    except jinja2.TemplateNotFound as exc:
        raise FileNotFoundError(f"Template '{template_name}' not found") from exc
    user = getattr(invoice.customer, "user", None)
    return template.render(invoice=invoice, user=user)


def generate_pdf(
    invoice: "Invoice", template_name: str = "standard", output_path: str | None = None
) -> str:
    """Generate a PDF for the given invoice.

    Args:
        invoice: Invoice model instance.
        template_name: Name of the HTML template (without prefix).
        output_path: Optional path to save the PDF. If not provided, the file is
            created inside ``Config.PDF_OUTPUT_DIR``.

    Returns:
        str: Path to the generated PDF file.
    """
    html = render_invoice_html(invoice, template_name)
    pdf_bytes = weasyprint.HTML(string=html, base_url=TEMPLATE_DIR).write_pdf()

    base_dir = os.path.abspath(Config.PDF_OUTPUT_DIR)
    os.makedirs(base_dir, exist_ok=True)

    if output_path is None:
        filename = f"invoice_{invoice.id or uuid.uuid4().hex}.pdf"
        output_path = os.path.join(base_dir, filename)
    else:
        output_path = os.path.abspath(output_path)
        if not output_path.startswith(base_dir):
            output_path = os.path.join(base_dir, os.path.basename(output_path))

    with open(output_path, "wb") as file:
        file.write(pdf_bytes)

    return output_path
