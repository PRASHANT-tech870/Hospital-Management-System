from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.db import get_db
from app.models import Staff, Patient, PatientStaffAssignment
from app.schemas import StaffResponse, PatientResponse

router = APIRouter(prefix="/api/staff", tags=["staff"])

@router.get("/{staff_id}/patients", response_model=List[PatientResponse])
def get_staff_patients(staff_id: int, db: Session = Depends(get_db)):
    try:
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")

        # Get patients through assignments
        patients = db.query(Patient).join(PatientStaffAssignment).filter(
            PatientStaffAssignment.staff_id == staff_id
        ).options(joinedload(Patient.user)).all()

        return patients
    except Exception as e:
        print(f"Error fetching staff patients: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch staff patients"
        )

@router.get("/{staff_id}", response_model=StaffResponse)
def get_staff_details(staff_id: int, db: Session = Depends(get_db)):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff