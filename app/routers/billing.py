from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db import get_db
from app.models import Invoice, InvoiceItem, Patient, Appointment, Doctor
from app.schemas import InvoiceCreate, InvoiceResponse

router = APIRouter(prefix="/api/billing", tags=["billing"])

@router.post("/invoices", response_model=InvoiceResponse)
def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db)
):
    try:
        # Create invoice
        new_invoice = Invoice(
            patient_id=invoice.patient_id,
            appointment_id=invoice.appointment_id,
            total_amount=invoice.total_amount,
            status=invoice.status
        )
        db.add(new_invoice)
        db.commit()
        db.refresh(new_invoice)

        # Create invoice items
        for item in invoice.items:
            invoice_item = InvoiceItem(
                invoice_id=new_invoice.id,
                description=item.description,
                amount=item.amount,
                item_type=item.item_type
            )
            db.add(invoice_item)
        
        db.commit()
        return new_invoice

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/patient/{patient_id}/invoices", response_model=List[InvoiceResponse])
def get_patient_invoices(
    patient_id: int,
    db: Session = Depends(get_db)
):
    invoices = db.query(Invoice).filter(
        Invoice.patient_id == patient_id
    ).order_by(Invoice.created_at.desc()).all()
    return invoices

@router.post("/invoices/{invoice_id}/pay")
def pay_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    try:
        # Get invoice
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )

        if invoice.status == "PAID":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice already paid"
            )

        # For demo: Simply mark the invoice as paid
        invoice.status = "PAID"
        invoice.paid_at = datetime.now()
        db.commit()

        return {
            "message": "Payment successful",
            "invoice_id": invoice.id,
            "amount_paid": invoice.total_amount,
            "status": invoice.status
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 