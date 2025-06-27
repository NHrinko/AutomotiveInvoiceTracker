"""PDF generation service using ReportLab - Simplified Version."""

import os
import logging
from decimal import Decimal
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class PDFService:
    """Simple PDF service for generating invoice PDFs."""

    def __init__(self):
        """Initialize PDF service."""
        pass

    def generate_invoice_pdf(self, invoice_id: int, output_path: str = None) -> str:
        """Generate PDF for an invoice using ReportLab."""
        try:
            # Import ReportLab components
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            # Get database connection
            from automotive_invoice_manager.backend.database.connection import DatabaseManager
            from automotive_invoice_manager.backend.database.models import Invoice
            
            db_manager = DatabaseManager.get_instance()
            
            # Get invoice data
            with db_manager.get_session() as session:
                invoice = session.query(Invoice).get(invoice_id)
                if not invoice:
                    raise ValueError(f"Invoice {invoice_id} not found")
                
                # Access all data within session to avoid lazy loading issues
                invoice_data = {
                    'invoice_number': invoice.invoice_number,
                    'customer_name': invoice.customer.name,
                    'customer_email': invoice.customer.email or '',
                    'customer_phone': invoice.customer.phone or '',
                    'customer_address': invoice.customer.address or '',
                    'issued_date': invoice.issued_date,
                    'due_date': invoice.due_date,
                    'status': invoice.status,
                    'line_items': invoice.line_items or [],
                    'total': float(invoice.total)
                }
            
            # Set output path
            if not output_path:
                output_dir = Path("generated_pdfs")
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / f"invoice_{invoice_data['invoice_number']}.pdf"
            else:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create PDF
            doc = SimpleDocTemplate(str(output_path), pagesize=letter, 
                                  topMargin=72, bottomMargin=72, 
                                  leftMargin=72, rightMargin=72)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#1E3A5F'),
                alignment=1  # Center
            )
            story.append(Paragraph(f"INVOICE #{invoice_data['invoice_number']}", title_style))
            story.append(Spacer(1, 20))
            
            # Invoice info and customer info side by side
            info_data = [
                ['Invoice Information', 'Bill To'],
                [f"Invoice #: {invoice_data['invoice_number']}", invoice_data['customer_name']],
                [f"Issue Date: {invoice_data['issued_date'].strftime('%B %d, %Y')}", invoice_data['customer_email']],
                [f"Due Date: {invoice_data['due_date'].strftime('%B %d, %Y')}", invoice_data['customer_phone']],
                [f"Status: {invoice_data['status'].title()}", invoice_data['customer_address'][:50] + '...' if len(invoice_data['customer_address']) > 50 else invoice_data['customer_address']],
            ]
            
            info_table = Table(info_data, colWidths=[3*inch, 3*inch])
            info_table.setStyle(TableStyle([
                # Header row
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DDE5ED')),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                
                # Data rows
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 30))
            
            # Line items
            if invoice_data['line_items']:
                story.append(Paragraph("ITEMS & SERVICES", styles['Heading3']))
                story.append(Spacer(1, 10))
                
                # Table headers
                line_data = [['Description', 'Hours', 'Rate', 'Parts', 'Tax', 'Amount']]
                
                # Add line items
                total_amount = Decimal('0')
                for item in invoice_data['line_items']:
                    hours = Decimal(str(item.get('hours', item.get('quantity', 0))))
                    rate = Decimal(str(item.get('rate', 0)))
                    parts = Decimal(str(item.get('parts', 0)))
                    tax = Decimal(str(item.get('tax', 0)))
                    amount = (hours * rate + parts) * (Decimal('1') + tax / Decimal('100'))
                    total_amount += amount

                    line_data.append([
                        item.get('description', 'Item'),
                        str(hours),
                        f"${rate:.2f}",
                        f"${parts:.2f}",
                        f"{tax}%",
                        f"${amount:.2f}"
                    ])
                
                # Add subtotal and total
                line_data.append([''] * 6)  # Spacer
                line_data.append(['', '', '', '', 'Subtotal:', f"${total_amount:.2f}"])
                line_data.append(['', '', '', '', 'TOTAL:', f"${total_amount:.2f}"])
                
                # Create table
                line_table = Table(line_data, colWidths=[2.5*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.7*inch, 1*inch])
                line_table.setStyle(TableStyle([
                    # Header row
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A5F')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
                    
                    # Data rows
                    ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -4), 10),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    
                    # Subtotal row
                    ('FONTNAME', (0, -2), (-1, -2), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, -2), (-1, -2), 11),
                    
                    # Total row
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, -1), (-1, -1), 14),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#DDE5ED')),
                    ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1E3A5F')),
                    
                    # Grid (skip spacer row)
                    ('GRID', (0, 0), (-1, -4), 1, colors.black),
                    ('GRID', (2, -2), (-1, -1), 1, colors.black),
                    
                    # Padding
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                ]))
                
                story.append(line_table)
            else:
                story.append(Paragraph("No line items", styles['Normal']))
            
            story.append(Spacer(1, 40))
            
            # Footer
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=1  # Center
            )
            
            footer_text = f"""
            Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
            Invoice Manager - Professional Invoice System
            """
            story.append(Paragraph(footer_text, footer_style))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF generated successfully: {output_path}")
            return str(output_path)
            
        except ImportError as e:
            logger.error(f"ReportLab not available: {e}")
            raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise

    def test_pdf_generation(self) -> bool:
        """Test if PDF generation is working."""
        try:
            import reportlab
            logger.info(f"ReportLab version: {reportlab.Version}")
            return True
        except ImportError:
            logger.error("ReportLab not installed")
            return False
