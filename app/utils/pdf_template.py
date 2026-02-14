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
    HRFlowable
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas as rl_canvas



def generate_agreement_pdf(title: str, body: str, left_signature: str, right_section: str):

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
    width, height = A4

    styles = getSampleStyleSheet()

    # =========================
    # Custom Styles
    # =========================
    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Normal"],
        fontSize=16,
        leading=20,
        alignment=1,  # Center
        spaceAfter=20,
        spaceBefore=10,
        fontName="Helvetica-Bold"
    )

    body_style = ParagraphStyle(
        name="BodyStyle",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        alignment=0,
    )

    signature_style = ParagraphStyle(
        name="SignatureStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=0,
    )

    right_style = ParagraphStyle(
        name="RightStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=1,  # Center text under line
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
        alignment=2  # Right
    )

    elements.append(Paragraph(current_date, date_style))
    elements.append(Spacer(1, 20))

    # =========================
    # Title (Center Bold)
    # =========================
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))

    # =========================
    # Body (Dynamic)
    # =========================
    elements.append(Paragraph(body, body_style))
    elements.append(Spacer(1, 40))

    # =========================
    # Bottom Signature Layout
    # =========================
    def draw_bottom_section(canvas, doc):
        canvas.saveState()

        page_width, page_height = A4
        y_position = 80  # distance from bottom

        # LEFT SIGNATURE
        canvas.line(40, y_position + 20, 240, y_position + 20)  # 200px width line
        text_left = canvas.beginText(40, y_position)
        text_left.setFont("Helvetica", 10)
        text_left.textLines(left_signature)
        canvas.drawText(text_left)

        # RIGHT SECTION
        right_x_start = page_width - 240
        canvas.line(right_x_start, y_position + 20, right_x_start + 200, y_position + 20)

        text_right = canvas.beginText(right_x_start, y_position)
        text_right.setFont("Helvetica", 10)

        # Center text manually
        lines = right_section.split("\n")
        for line in lines:
            text_width = canvas.stringWidth(line, "Helvetica", 10)
            centered_x = right_x_start + (200 - text_width) / 2
            canvas.drawString(centered_x, y_position, line)
            y_position -= 14

        canvas.restoreState()

    # =========================
    # Build PDF
    # =========================
    doc.build(elements, onFirstPage=draw_bottom_section)

    buffer.seek(0)
    return buffer


def generate_dynamic_signature_pdf(title: str, body: str, p1: str, p2: str, p3: str):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=60
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
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
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