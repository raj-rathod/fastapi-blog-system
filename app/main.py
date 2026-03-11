# app.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from contextlib import asynccontextmanager

from app.utils.database import engine, get_db, Base
from app.utils.config import settings
from app.utils.pdf_template import generate_agreement_pdf, generate_email_pdf
from app.utils.pdf_template import generate_dynamic_signature_pdf
from app.utils.pdf_template import generateFaxCopy

# Configure CORS from .env
origins = []
if settings.CORS_ORIGINS != "*":
    origins = settings.CORS_ORIGINS.split(",")
else:
    origins = ["*"]



# Create FastAPI app with settings from .env
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/download-agreement")
def download_agreement():

    title = "SERVICE AGREEMENT"

    body = "<b>LEGAL AGREEMENT</b><br/><br/>This Legal Agreement (\"Agreement\") is made and entered into between the concerned parties for defining the terms and conditions governing their professional relationship.<br/><br/>1. <b>Scope of Services</b><br/>The Service Provider agrees to perform services with due diligence, professional care, and in compliance with all applicable laws and regulations.<br/><br/>2. <b>Payment Terms</b><br/>The Client agrees to compensate the Service Provider as per the mutually agreed commercial terms. Payments shall be made within the stipulated timeframe as outlined in the invoice or agreement schedule.<br/><br/>3. <b>Confidentiality</b><br/>Both parties agree to maintain strict confidentiality of all proprietary, financial, and business information exchanged during the course of this Agreement. Such information shall not be disclosed without prior written consent.<br/><br/>4. <b>Term and Termination</b><br/>This Agreement shall remain in effect unless terminated by either party with prior written notice. Termination shall not affect any obligations accrued before the termination date.<br/><br/>5. <b>Limitation of Liability</b><br/>Under no circumstances shall either party be liable for indirect, incidental, or consequential damages arising out of this Agreement.<br/><br/>6. <b>Governing Law</b><br/>This Agreement shall be governed and construed in accordance with the applicable laws of the relevant jurisdiction.<br/><br/>By signing below, both parties acknowledge that they have read, understood, and agreed to the terms and conditions stated herein.<br/><br/>Authorized Signatory<br/>__________________________<br/><br/>Client Signature<br/>__________________________"


    left_signature = "Authorized Signature\nCompany A"

    right_section = "Client Signature\nCompany B"

    pdf_buffer = generate_agreement_pdf(
        title=title,
        body=body,
        left_signature=left_signature,
        right_section=right_section
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=agreement.pdf"}
    )

@app.get("/download-agreement_sign")
def download_agreement_sign():

    title = "SERVICE AGREEMENT"

    body = "<b>LEGAL AGREEMENT</b><br/><br/>This Legal Agreement (\"Agreement\") is made and entered into between the concerned parties for defining the terms and conditions governing their professional relationship.<br/><br/>1. <b>Scope of Services</b><br/>The Service Provider agrees to perform services with due diligence, professional care, and in compliance with all applicable laws and regulations.<br/><br/>2. <b>Payment Terms</b><br/>The Client agrees to compensate the Service Provider as per the mutually agreed commercial terms. Payments shall be made within the stipulated timeframe as outlined in the invoice or agreement schedule.<br/><br/>3. <b>Confidentiality</b><br/>Both parties agree to maintain strict confidentiality of all proprietary, financial, and business information exchanged during the course of this Agreement. Such information shall not be disclosed without prior written consent.<br/><br/>4. <b>Term and Termination</b><br/>This Agreement shall remain in effect unless terminated by either party with prior written notice. Termination shall not affect any obligations accrued before the termination date.<br/><br/>5. <b>Limitation of Liability</b><br/>Under no circumstances shall either party be liable for indirect, incidental, or consequential damages arising out of this Agreement.<br/><br/>6. <b>Governing Law</b><br/>This Agreement shall be governed and construed in accordance with the applicable laws of the relevant jurisdiction.<br/><br/>By signing below, both parties acknowledge that they have read, understood, and agreed to the terms and conditions stated herein.<br/><br/>Authorized Signatory<br/>__________________________<br/><br/>Client Signature<br/>__________________________"


    left_signature = "Authorized Signature\nCompany A"

    right_section = "Client Signature\nCompany B"

    pdf_buffer = generate_agreement_pdf(
        title=title,
        body=body,
        p1=left_signature,
        p2=left_signature,
        p3=right_section
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=agreement.pdf"}
    )

@app.get("/download-fax_copy")
def download_fax_copy():

    pdf_buffer = generateFaxCopy()

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=agreement_fax.pdf"}
    )

@app.get("/download-email_copy")
def download_emailcopy():

    pdf_buffer = generate_email_pdf()

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=agreement_fax.pdf"}
    )

