"""
Certificate PDF Generator using ReportLab
"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import qrcode
from io import BytesIO
from datetime import datetime
import os


def generate_certificate_pdf(certificate, request=None):
    """
    Generate a professional certificate PDF
    
    Args:
        certificate: Certificate model instance
        request: Django request object (optional, for building absolute URLs)
    
    Returns:
        BytesIO object containing the PDF
    """
    # Create PDF in memory
    buffer = BytesIO()
    
    # Use landscape A4
    page_width, page_height = landscape(A4)
    
    # Create canvas
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    
    # Colors
    primary_color = HexColor('#6366f1')
    secondary_color = HexColor('#a855f7')
    gold_color = HexColor('#f59e0b')
    text_color = HexColor('#1e293b')
    
    # Draw border
    c.setStrokeColor(primary_color)
    c.setLineWidth(3)
    c.rect(1.5*cm, 1.5*cm, page_width-3*cm, page_height-3*cm)
    
    # Inner decorative border
    c.setStrokeColor(gold_color)
    c.setLineWidth(1)
    c.rect(2*cm, 2*cm, page_width-4*cm, page_height-4*cm)
    
    # Title
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(page_width/2, page_height-5*cm, "CERTIFICATE")
    
    c.setFont("Helvetica", 24)
    c.drawCentredString(page_width/2, page_height-6.5*cm, "OF COMPLETION")
    
    # Decorative line
    c.setStrokeColor(gold_color)
    c.setLineWidth(2)
    c.line(page_width/2-8*cm, page_height-7*cm, page_width/2+8*cm, page_height-7*cm)
    
    # "This certifies that"
    c.setFillColor(text_color)
    c.setFont("Helvetica", 16)
    c.drawCentredString(page_width/2, page_height-9*cm, "This certifies that")
    
    # Student name
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(page_width/2, page_height-11*cm, certificate.user.get_full_name() or certificate.user.username)
    
    # Decorative line under name
    c.setStrokeColor(gold_color)
    c.setLineWidth(1)
    c.line(page_width/2-10*cm, page_height-11.5*cm, page_width/2+10*cm, page_height-11.5*cm)
    
    # "has successfully completed"
    c.setFillColor(text_color)
    c.setFont("Helvetica", 16)
    c.drawCentredString(page_width/2, page_height-13*cm, "has successfully completed the course")
    
    # Course name
    c.setFillColor(secondary_color)
    c.setFont("Helvetica-Bold", 28)
    
    # Handle long course names
    course_title = certificate.course.title
    if len(course_title) > 50:
        # Split into two lines
        words = course_title.split()
        mid = len(words) // 2
        line1 = ' '.join(words[:mid])
        line2 = ' '.join(words[mid:])
        c.drawCentredString(page_width/2, page_height-14.5*cm, line1)
        c.drawCentredString(page_width/2, page_height-15.5*cm, line2)
        y_offset = 16.5
    else:
        c.drawCentredString(page_width/2, page_height-15*cm, course_title)
        y_offset = 16
    
    # Date and Certificate ID
    c.setFillColor(text_color)
    c.setFont("Helvetica", 12)
    
    # Date (left side)
    date_str = certificate.completion_date.strftime("%B %d, %Y")
    c.drawString(5*cm, 4*cm, f"Date: {date_str}")
    
    # Certificate ID (right side)
    c.drawRightString(page_width-5*cm, 4*cm, f"Certificate ID: {certificate.certificate_id}")
    
    # Generate QR Code for verification
    if request:
        verify_url = request.build_absolute_uri(f'/certificates/verify/{certificate.certificate_id}/')
    else:
        verify_url = f"Certificate ID: {certificate.certificate_id}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to BytesIO
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    # Draw QR code (bottom right)
    c.drawImage(ImageReader(qr_buffer), page_width-7*cm, 2.5*cm, width=3*cm, height=3*cm)
    
    # QR code label
    c.setFont("Helvetica", 8)
    c.drawCentredString(page_width-5.5*cm, 2*cm, "Scan to verify")
    
    # Signature line (optional - can be customized)
    c.setStrokeColor(text_color)
    c.setLineWidth(1)
    c.line(8*cm, 5*cm, 14*cm, 5*cm)
    c.setFont("Helvetica", 10)
    c.drawCentredString(11*cm, 4.5*cm, "Authorized Signature")
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(HexColor('#64748b'))
    c.drawCentredString(page_width/2, 1*cm, "مدونتي - Educational Platform")
    
    # Finalize PDF
    c.showPage()
    c.save()
    
    # Get PDF from buffer
    buffer.seek(0)
    return buffer
