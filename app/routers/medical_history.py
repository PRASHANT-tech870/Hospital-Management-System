from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db import get_db
from app.models import MedicalHistory, DoctorNote, Patient, Doctor, User
from app.schemas import (
    MedicalHistoryCreate, MedicalHistoryResponse,
    DoctorNoteCreate, DoctorNoteResponse
)

router = APIRouter(prefix="/api/medical", tags=["medical"])

@router.post("/history", response_model=MedicalHistoryResponse)
def add_medical_history(
    history: MedicalHistoryCreate,
    db: Session = Depends(get_db)
):
    try:
        new_history = MedicalHistory(**history.dict())
        db.add(new_history)
        db.commit()
        db.refresh(new_history)
        return new_history
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/history/patient/{patient_id}", response_model=List[MedicalHistoryResponse])
def get_patient_history(
    patient_id: int,
    db: Session = Depends(get_db)
):
    histories = db.query(MedicalHistory).filter(
        MedicalHistory.patient_id == patient_id
    ).order_by(MedicalHistory.diagnosis_date.desc()).all()
    return histories

@router.post("/notes", response_model=DoctorNoteResponse)
def add_doctor_note(
    note: DoctorNoteCreate,
    db: Session = Depends(get_db)
):
    try:
        # Verify doctor exists
        doctor = db.query(Doctor).filter(Doctor.id == note.doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )

        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == note.patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        # Create new note
        new_note = DoctorNote(
            patient_id=note.patient_id,
            doctor_id=note.doctor_id,
            appointment_id=note.appointment_id,
            note=note.note
        )
        
        db.add(new_note)
        db.commit()
        db.refresh(new_note)

        # Format response
        return DoctorNoteResponse(
            id=new_note.id,
            note=new_note.note,
            appointment_id=new_note.appointment_id,
            created_at=new_note.created_at,
            updated_at=new_note.updated_at,
            doctor_name=doctor.user.username
        )

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        print(f"Error adding doctor note: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding note: {str(e)}"
        )

@router.get("/notes/patient/{patient_id}", response_model=List[DoctorNoteResponse])
def get_patient_notes(
    patient_id: int,
    db: Session = Depends(get_db)
):
    notes = db.query(DoctorNote).join(
        Doctor, DoctorNote.doctor_id == Doctor.id
    ).join(
        User, Doctor.user_id == User.id
    ).filter(
        DoctorNote.patient_id == patient_id
    ).order_by(DoctorNote.created_at.desc()).all()
    
    return [
        DoctorNoteResponse(
            **note.__dict__,
            doctor_name=note.doctor.user.username
        ) for note in notes
    ] 