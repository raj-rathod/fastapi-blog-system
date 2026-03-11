import os
from io import BytesIO
from datetime import datetime
from pathlib import Path

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    HRFlowable,
    TableStyle
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas as rl_canvas


def generate_agreement_pdf(title: str, body: str, p1: str, p2: str, p3: str):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=60
    )

    elements = []
    styles = getSampleStyleSheet()

    # =========================
    # Styles
    # =========================
    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Normal"],
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        spaceAfter=20
    )

    body_style = ParagraphStyle(
        name="BodyStyle",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        alignment=TA_LEFT
    )

    date_style = ParagraphStyle(
        name="DateStyle",
        parent=styles["Normal"],
        fontSize=10,
        alignment=TA_RIGHT
    )

    signature_style = ParagraphStyle(
        name="SignatureStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_CENTER
    )

    # =========================
    # Top Logo
    # =========================
    BASE_DIR = Path(__file__).resolve().parent.parent
    logo_path = BASE_DIR / "static" / "logo.png"

    if logo_path.exists():
        logo = Image(str(logo_path))
        logo.drawHeight = 0.8 * inch
        logo.drawWidth = logo.drawHeight * logo.imageWidth / logo.imageHeight
        logo.hAlign = "LEFT"
        elements.append(logo)

    elements.append(Spacer(1, 10))

    # =========================
    # Date (Top Right)
    # =========================
    current_date = datetime.now().strftime("%d/%m/%Y")
    elements.append(Paragraph(current_date, date_style))
    elements.append(Spacer(1, 20))

    # =========================
    # Title
    # =========================
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))

    # =========================
    # Body
    # =========================
    elements.append(Paragraph(body, body_style))

    # ====================================================
    # Bottom Signature Section (Last Page Only)
    # ====================================================

    # Logo under p1 only
    if logo_path.exists():
        sign_logo = Image(str(logo_path))
        sign_logo.drawHeight = 0.6 * inch
        sign_logo.drawWidth = sign_logo.drawHeight * sign_logo.imageWidth / sign_logo.imageHeight
    else:
        sign_logo = Spacer(1, 20)

    # Left block (p1 + logo)
    left_block = Table([
        [Paragraph(p1, signature_style)],
        [sign_logo]
    ])
    left_block.setStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ])

    # Middle block (p2)
    middle_block = Paragraph(p2, signature_style) if p2 else Spacer(1, 20)

    # Right block (p3 bottom aligned)
    right_block = Table([
        [''],
        [Paragraph(p3, signature_style)]
    ], rowHeights=[30, None])

    right_block.setStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, 1), 'BOTTOM')
    ])

    # Final horizontal signature table
    signatureTable = Table(
        [[left_block, middle_block, right_block]],
        colWidths=[180, 180, 180]
    )

    signatureTable.setStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ])

    # ====================================================
    # Custom Canvas (Signature Only On Last Page)
    # ====================================================
    class SignatureCanvas(rl_canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.pages = []

        def showPage(self):
            self.pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total_pages = len(self.pages)

            for page_number, page in enumerate(self.pages, start=1):
                self.__dict__.update(page)

                if page_number == total_pages:
                    w, h = signatureTable.wrap(doc.width, doc.bottomMargin)
                    signatureTable.drawOn(
                        self,
                        doc.leftMargin,
                        doc.bottomMargin - h + 30
                    )

                super().showPage()

            super().save()

    doc.build(elements, canvasmaker=SignatureCanvas)

    buffer.seek(0)
    return buffer


def generate_dynamic_signature_pdf(title: str, body: str, p1: str, p2: str, p3: str):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    elements = []
    styles = getSampleStyleSheet()

    # =========================
    # Custom Styles
    # =========================
    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Normal"],
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName="Helvetica-Bold"
    )

    body_style = ParagraphStyle(
        name="BodyStyle",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        alignment=0
    )

    signature_style = ParagraphStyle(
        name="SignatureStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=0
    )

    center_style = ParagraphStyle(
        name="CenterStyle",
        parent=styles["Normal"],
        alignment=TA_CENTER
    )

    # =========================
    # Logo (Absolute Safe Path)
    # =========================
    BASE_DIR = Path(__file__).resolve().parent.parent
    logo_path = BASE_DIR / "static" / "logo.png"

    if logo_path.exists():
        logo = Image(str(logo_path), width=2 * inch, height=1 * inch)
        logo.hAlign = "LEFT"
        elements.append(logo)

    elements.append(Spacer(1, 10))

    # =========================
    # Date (Top Right)
    # =========================
    current_date = datetime.now().strftime("%d %B %Y")

    date_style = ParagraphStyle(
        name="DateStyle",
        parent=styles["Normal"],
        fontSize=10,
        alignment=2  # Right align
    )

    elements.append(Paragraph(current_date, date_style))
    elements.append(Spacer(1, 20))

    # =========================
    # Title
    # =========================
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))

    # =========================
    # Body
    # =========================
    elements.append(Paragraph(body, body_style))

    # =========================
    # Signature Section (Prepared but NOT added to elements)
    # =========================
    sign1 = Paragraph(p1, signature_style)
    left_cells = [sign1]

    if p2:
        sign2 = Paragraph(p2, signature_style)
        left_cells.append(sign2)

    left_group = Table([left_cells], colWidths=[120] * len(left_cells))

    hr = HRFlowable(width="100%", thickness=1, color=colors.black)
    sign3 = Paragraph(p3, center_style)

    right_group = Table([[hr], [sign3]], colWidths=[180])

    signatureTable = Table([[left_group, right_group]], colWidths=[350, 180])
    signatureTable.setStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ])

    # =========================
    # Professional Canvas (Signature on Last Page Only)
    # =========================
    class SignatureCanvas(rl_canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.pages = []

        def showPage(self):
            self.pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total_pages = len(self.pages)

            for page_number, page in enumerate(self.pages, start=1):
                self.__dict__.update(page)

                if page_number == total_pages:
                    w, h = signatureTable.wrap(doc.width, doc.bottomMargin)
                    signatureTable.drawOn(
                        self,
                        doc.leftMargin,
                        doc.bottomMargin - h + 20
                    )

                super().showPage()

            super().save()

    # Build document
    doc.build(elements, canvasmaker=SignatureCanvas)

    buffer.seek(0)
    return buffer

def generateFaxCopy(): 
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    elements = []
    styles = getSampleStyleSheet()

    normal = styles["Normal"]

    # =========================
    # HEADER BOX
    # =========================
    header_data = [
        [
            Paragraph("<b>Fax Call Report</b>", normal),
            Paragraph("<b>HP Laser Jet color MFP M283fdw</b><br/>Page 1", 
                      ParagraphStyle(
                          name="RightHeader",
                          parent=normal,
                          alignment=TA_RIGHT
                      ))
        ]
    ]

    header_table = Table(header_data, colWidths=[300, 200])
    header_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # =========================
    # Fax Header Info
    # =========================
    elements.append(Paragraph("Fax Header", normal))
    elements.append(Paragraph("Information BASF", normal))
    elements.append(Paragraph("03 2241 1511", normal))
    elements.append(Spacer(1, 25))

    # =========================
    # Report Table
    # =========================
    table_data = [
        ["Job", "Date", "Type", "Line", "Identification", "Duration", "Pages", "Result"],
        ["2316", "", "Send", "Analog", "", "0:30", "1", "Successful"]
    ]

    report_table = Table(table_data, colWidths=[60, 70, 70, 70, 110, 70, 50, 90])

    report_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(report_table)

    elements.append(Spacer(1, 350))

    # =========================
    # Footer
    # =========================
    footer_table = Table([
        [
            Paragraph("Internal", normal),
            Paragraph("English (United States)", 
                      ParagraphStyle(
                          name="RightFooter",
                          parent=normal,
                          alignment=TA_RIGHT
                      ))
        ]
    ], colWidths=[300, 200])

    elements.append(footer_table)

    # Build
    doc.build(elements)

    buffer.seek(0)

    return buffer

def generate_email_pdf():
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    elements = []
    styles = getSampleStyleSheet()

    normal = styles["Normal"]

    small_style = ParagraphStyle(
        name="Small",
        parent=normal,
        fontSize=10,
        leading=14,
        alignment=TA_LEFT
    )

    bold_style = ParagraphStyle(
        name="Bold",
        parent=normal,
        fontSize=10,
        leading=14
    )

    # =========================
    # Header Table (From / To / etc.)
    # =========================

    header_data = [
        ["From:", "APTIC_LC_CHECK@basf.com"],
        ["To:", ""],
        ["Subject:", ""],
        ["Date:", datetime.now().strftime("%d/%m/%Y")],
        ["Attachments:", "DOCS.pdf"],
    ]

    header_table = Table(header_data, colWidths=[100, 350])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 10))

    # =========================
    # Horizontal Line
    # =========================

    elements.append(HRFlowable(width="100%", thickness=2, color=colors.black))
    elements.append(Spacer(1, 20))

    # =========================
    # Body
    # =========================

    elements.append(Paragraph("To:", small_style))
    elements.append(Spacer(1, 15))

    body_text = """
    Enclose documents pertaining as per above subject details for your kind reference.
    """

    elements.append(Paragraph(body_text, small_style))
    elements.append(Spacer(1, 200))  # push content downward

    # =========================
    # Closing Section
    # =========================

    closing_text = """
    Thank You,<br/><br/>
    Regards,<br/>
    BASF Hong Kong Ltd.<br/>
    36/F, Two Taikoo Place, Taikoo Place,<br/>
    979 King's Road, Quarry Bay, Hong Kong.
    """

    elements.append(Paragraph(closing_text, small_style))
    elements.append(Spacer(1, 20))

    # =========================
    # Logo (Auto Size - No Stretch)
    # =========================

    BASE_DIR = Path(__file__).resolve().parent.parent
    logo_path = BASE_DIR / "static" / "logo.png"

    if logo_path.exists():
        logo = Image(str(logo_path))
        logo._restrictSize(2.5 * inch, 1.2 * inch)  # keeps aspect ratio
        elements.append(logo)

    elements.append(Spacer(1, 40))

    # =========================
    # Bottom Right Signature Line
    # =========================

    sign_line = Table(
        [[""]],
        colWidths=[200],
        rowHeights=[1]
    )

    sign_line.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1, colors.black),
    ]))

    right_align_table = Table(
        [[sign_line]],
        colWidths=[doc.width]
    )

    right_align_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
    ]))

    elements.append(right_align_table)
    elements.append(Spacer(1, 5))

    elements.append(
        Paragraph(
            "for BASF HONG KONG LTD.",
            ParagraphStyle(
                name="RightSmall",
                parent=small_style,
                alignment=2
            )
        )
    )

    # =========================
    # Build PDF with Footer
    # =========================

    doc.build(
        elements
    )

    buffer.seek(0)
    return buffer