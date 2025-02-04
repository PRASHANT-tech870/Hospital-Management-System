from sqlalchemy.orm import Session
from app.models import Patient, User
from app.schemas import PatientCreate, PatientUpdate

# Create a new patient
def create_patient(db: Session, patient: PatientCreate):
    user = User(
        username=patient.username,
        email=patient.email,
        password=patient.password,  # Note: Hash the password in production
        role="PATIENT",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    new_patient = Patient(
        user_id=user.id,
        medical_history=patient.medical_history,
        emergency_contact=patient.emergency_contact,
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

# Get a single patient by ID
def get_patient(db: Session, patient_id: int):
    return db.query(Patient).filter(Patient.id == patient_id).first()

# Get all patients
def get_all_patients(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Patient).offset(skip).limit(limit).all()

# Update a patient's details
def update_patient(db: Session, patient_id: int, patient: PatientUpdate):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        return None
    for key, value in patient.dict(exclude_unset=True).items():
        setattr(db_patient, key, value)
    db.commit()
    db.refresh(db_patient)
    return db_patient

# Delete a patient
def delete_patient(db: Session, patient_id: int):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if db_patient:
        db.delete(db_patient)
        db.commit()
        return True
    return False
