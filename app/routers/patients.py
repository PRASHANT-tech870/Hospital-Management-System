from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app import crud, schemas
from fastapi import status
from app.models import Patient, User

router = APIRouter()

# Create a new patient
@router.post("/", response_model=schemas.PatientResponse)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    return crud.create_patient(db=db, patient=patient)

# Get a single patient by ID
@router.get("/{patient_id}", response_model=schemas.PatientResponse)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = crud.get_patient(db=db, patient_id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# Get all patients
@router.get("/", response_model=list[schemas.PatientResponse])
def read_patients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_all_patients(db=db, skip=skip, limit=limit)

# Update a patient
@router.put("/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(patient_id: int, patient: schemas.PatientUpdate, db: Session = Depends(get_db)):
    updated_patient = crud.update_patient(db=db, patient_id=patient_id, patient=patient)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated_patient

# Delete a patient
@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    success = crud.delete_patient(db=db, patient_id=patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}

@router.get("/{user_id}", response_model=dict)
def get_patient(
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        patient = db.query(Patient).join(
            User, Patient.user_id == User.id
        ).filter(
            User.id == user_id
        ).first()

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        return {
            "id": patient.id,
            "user_id": patient.user_id,
            "medical_history": patient.medical_history,
            "emergency_contact": patient.emergency_contact
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
