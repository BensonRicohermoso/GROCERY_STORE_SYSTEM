from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
from typing import List, Dict
import config


class PDFGenerator:
    """Handles PDF generation for receipts and reports"""
    
    @staticmethod
    def generate_receipt(sale_data: Dict, filename: str = None) -> str:
        """
        Generate sale receipt PDF
        
        Args:
            sale_data: Dictionary containing sale information
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to generated PDF file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{config.BASE_DIR}/receipts/receipt_{sale_data['sale_number']}_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor(config.COLORS['primary']),
            alignment=TA_CENTER,
            spaceAfter=12
        )
        
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=6
        )
        
        # Header
        story.append(Paragraph(config.PDF_CONFIG['company_name'], title_style))
        story.append(Paragraph(config.PDF_CONFIG['company_address'], header_style))
        story.append(Paragraph(f"Tel: {config.PDF_CONFIG['company_phone']}", header_style))
        story.append(Paragraph(f"Email: {config.PDF_CONFIG['company_email']}", header_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Receipt info
        receipt_info = [
            ['SALES RECEIPT', ''],
            ['Receipt No:', sale_data['sale_number']],
            ['Date:', sale_data['sale_date'].strftime("%Y-%m-%d %H:%M:%S")],
            ['Cashier:', sale_data.get('cashier_name', 'N/A')],
        ]
        
        if sale_data.get('customer_name'):
            receipt_info.append(['Customer:', sale_data['customer_name']])
        
        info_table = Table(receipt_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('SPAN', (0, 0), (1, 0)),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Items table
        items_data = [['Item', 'Qty', 'Price', 'Total']]
        
        for item in sale_data['items']:
            items_data.append([
                item['product_name'],
                str(item['quantity']),
                f"{config.BUSINESS_CONFIG['currency_symbol']}{item['unit_price']:.2f}",
                f"{config.BUSINESS_CONFIG['currency_symbol']}{item['subtotal']:.2f}"
            ])
        
        items_table = Table(items_data, colWidths=[3*inch, 0.7*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(config.COLORS['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Totals
        currency = config.BUSINESS_CONFIG['currency_symbol']
        totals_data = [
            ['', '', 'Subtotal:', f"{currency}{sale_data['subtotal']:.2f}"],
        ]
        
        if sale_data['discount_amount'] > 0:
            totals_data.append([
                '', '', 'Discount:', f"({currency}{sale_data['discount_amount']:.2f})"
            ])
        
        totals_data.extend([
            ['', '', 'Tax:', f"{currency}{sale_data['tax_amount']:.2f}"],
            ['', '', 'TOTAL:', f"{currency}{sale_data['total_amount']:.2f}"],
        ])
        
        totals_table = Table(totals_data, colWidths=[2.5*inch, 1.2*inch, 1*inch, 1*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (2, 0), (2, -2), 'Helvetica'),
            ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (2, 0), (-1, -2), 10),
            ('FONTSIZE', (2, -1), (-1, -1), 14),
            ('LINEABOVE', (2, -1), (-1, -1), 2, colors.black),
            ('TOPPADDING', (2, -1), (-1, -1), 12),
        ]))
        
        story.append(totals_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        
        story.append(Paragraph("Thank you for your business!", footer_style))
        story.append(Paragraph("Please keep this receipt for your records", footer_style))
        
        # Build PDF
        doc.build(story)
        return filename
    
    @staticmethod
    def generate_sales_report(report_data: Dict, filename: str = None) -> str:
        """
        Generate sales report PDF
        
        Args:
            report_data: Dictionary containing report information
            filename: Output filename
            
        Returns:
            Path to generated PDF file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{config.BASE_DIR}/reports/sales_report_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor(config.COLORS['primary']),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        story.append(Paragraph("Sales Report", title_style))
        
        # Report period
        if report_data.get('start_date') and report_data.get('end_date'):
            period = f"Period: {report_data['start_date']} to {report_data['end_date']}"
        else:
            period = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        story.append(Paragraph(period, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary statistics
        currency = config.BUSINESS_CONFIG['currency_symbol']
        summary_data = [
            ['Metric', 'Value'],
            ['Total Orders', str(report_data.get('total_orders', 0))],
            ['Total Revenue', f"{currency}{report_data.get('total_revenue', 0):.2f}"],
            ['Total Tax Collected', f"{currency}{report_data.get('total_tax', 0):.2f}"],
            ['Total Discounts', f"{currency}{report_data.get('total_discounts', 0):.2f}"],
            ['Average Order Value', f"{currency}{report_data.get('average_order_value', 0):.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(config.COLORS['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(summary_table)
        
        # Build PDF
        doc.build(story)
        return filename