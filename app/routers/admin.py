from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.db import get_db
from app.models import Admin, Equipment, Staff, Patient, Doctor, PatientStaffAssignment, Department, Appointment
from app.schemas import (
    AdminCreate, AdminLogin, EquipmentCreate, EquipmentUpdate, 
    EquipmentResponse, PatientStaffAssignmentCreate, PatientResponse,
    DoctorResponse, StaffResponse, PatientStaffAssignmentResponse,
    DepartmentResponse, UsersByDepartmentResponse
)

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Admin authentication
@router.post("/login")
def admin_login(login: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == login.username).first()
    if not admin or admin.password != login.password:  # In production, use proper password hashing
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "admin_id": admin.id}

# Equipment management
@router.post("/equipment", response_model=EquipmentResponse)
def create_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    try:
        # Create new equipment with default unit statuses
        new_equipment = Equipment(
            name=equipment.name,
            category=equipment.category,
            status=equipment.status,
            department_id=equipment.department_id,
            quantity=equipment.quantity,
            unit_statuses={str(i): equipment.status for i in range(1, equipment.quantity + 1)}
        )
        
        db.add(new_equipment)
        db.commit()
        db.refresh(new_equipment)
        return new_equipment
    except Exception as e:
        db.rollback()
        print(f"Error creating equipment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating equipment: {str(e)}"
        )

@router.get("/equipment", response_model=List[EquipmentResponse])
def get_all_equipment(db: Session = Depends(get_db)):
    return db.query(Equipment).options(joinedload(Equipment.department)).all()

@router.put("/equipment/{equipment_id}", response_model=EquipmentResponse)
def update_equipment(equipment_id: int, equipment: EquipmentUpdate, db: Session = Depends(get_db)):
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    for key, value in equipment.dict(exclude_unset=True).items():
        setattr(db_equipment, key, value)
    
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

@router.delete("/equipment/{equipment_id}")
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    db.delete(equipment)
    db.commit()
    return {"message": "Equipment deleted"}

# Add these new endpoints to handle equipment unit operations

@router.patch("/equipment/{base_id}/unit/{unit_number}", response_model=dict)
def update_equipment_unit_status(
    base_id: int, 
    unit_number: int, 
    status_update: dict,
    db: Session = Depends(get_db)
):
    try:
        # Get the base equipment with department info
        equipment = db.query(Equipment).filter(Equipment.id == base_id).first()
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipment not found")
            
        # Verify unit number is valid
        if unit_number < 1 or unit_number > equipment.quantity:
            raise HTTPException(status_code=400, detail="Invalid unit number")

        # Initialize unit_statuses if None
        if equipment.unit_statuses is None:
            equipment.unit_statuses = {}

        # Update the status for this specific unit
        current_statuses = dict(equipment.unit_statuses)  # Create a copy
        current_statuses[str(unit_number)] = status_update['status']
        equipment.unit_statuses = current_statuses

        # Also update the base status if this is the only unit
        if equipment.quantity == 1:
            equipment.status = status_update['status']
        
        try:
            db.commit()
            db.refresh(equipment)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )
        
        return {
            "message": "Equipment unit status updated successfully",
            "equipment_id": base_id,
            "unit_number": unit_number,
            "status": status_update['status'],
            "unit_statuses": equipment.unit_statuses
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        print(f"Error updating status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating status: {str(e)}"
        )

@router.delete("/equipment/{base_id}/unit/{unit_number}")
def delete_equipment_unit(
    base_id: int, 
    unit_number: int,
    db: Session = Depends(get_db)
):
    try:
        # Get the base equipment
        equipment = db.query(Equipment).filter(Equipment.id == base_id).first()
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipment not found")
            
        # Verify unit number is valid
        if unit_number < 1 or unit_number > equipment.quantity:
            raise HTTPException(status_code=400, detail="Invalid unit number")

        # Decrease quantity by 1
        equipment.quantity -= 1
        
        # Remove the unit status if it exists
        unit_statuses = getattr(equipment, 'unit_statuses', {})
        if isinstance(unit_statuses, dict):
            unit_statuses.pop(str(unit_number), None)
            # Reindex remaining units if needed
            new_statuses = {}
            current_index = 1
            for i in range(1, equipment.quantity + 2):
                if i != unit_number and str(i) in unit_statuses:
                    new_statuses[str(current_index)] = unit_statuses[str(i)]
                    current_index += 1
            equipment.unit_statuses = new_statuses

        # If quantity becomes 0, delete the equipment entirely
        if equipment.quantity <= 0:
            db.delete(equipment)
        
        db.commit()
        
        return {
            "message": "Equipment unit deleted successfully",
            "equipment_id": base_id,
            "unit_number": unit_number,
            "remaining_quantity": max(0, equipment.quantity)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Staff-Patient assignment
@router.post("/assign-patient", response_model=PatientStaffAssignmentResponse)
def assign_patient_to_staff(
    assignment: PatientStaffAssignmentCreate,
    db: Session = Depends(get_db)
):
    new_assignment = PatientStaffAssignment(**assignment.dict())
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment

# View all patients and doctors
@router.get("/patients", response_model=List[PatientResponse])
def get_all_patients(db: Session = Depends(get_db)):
    try:
        patients = db.query(Patient).options(
            joinedload(Patient.user)
        ).all()
        return patients
    except Exception as e:
        print(f"Error fetching patients: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch patients"
        )

@router.get("/doctors", response_model=List[DoctorResponse])
def get_all_doctors(db: Session = Depends(get_db)):
    try:
        doctors = db.query(Doctor).options(
            joinedload(Doctor.user),
            joinedload(Doctor.department)
        ).all()
        return doctors
    except Exception as e:
        print(f"Error fetching doctors: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch doctors"
        )

@router.get("/staff", response_model=List[StaffResponse])
def get_all_staff(db: Session = Depends(get_db)):
    try:
        staff = db.query(Staff).options(
            joinedload(Staff.user),
            joinedload(Staff.assigned_patients)
        ).all()
        for s in staff:
            print(f"Staff data: id={s.id}, name={s.name}, user_id={s.user_id}")
            if s.user:
                print(f"User data: id={s.user.id}, username={s.user.username}")
        return staff
    except Exception as e:
        print(f"Error fetching staff: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch staff"
        )

# Add departments endpoint
@router.get("/departments", response_model=List[DepartmentResponse])
def get_all_departments(db: Session = Depends(get_db)):
    try:
        departments = db.query(Department).all()
        return departments
    except Exception as e:
        print(f"Error fetching departments: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch departments"
        )

@router.get("/assignments", response_model=List[PatientStaffAssignmentResponse])
def get_all_assignments(db: Session = Depends(get_db)):
    return db.query(PatientStaffAssignment).all()

@router.delete("/assignments/{assignment_id}")
def remove_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(PatientStaffAssignment).filter(PatientStaffAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    db.delete(assignment)
    db.commit()
    return {"message": "Assignment removed successfully"}

@router.get("/users-by-department/{department_id}", response_model=UsersByDepartmentResponse)
def get_users_by_department(department_id: int = None, db: Session = Depends(get_db)):
    try:
        # Get doctors in department
        doctors = db.query(Doctor).filter(
            Doctor.department_id == department_id if department_id else True
        ).options(joinedload(Doctor.user), joinedload(Doctor.department)).all()

        # Get patients (through appointments with doctors in the department)
        if department_id:
            dept_doctors = [d.id for d in doctors]
            patients = db.query(Patient).join(Appointment).filter(
                Appointment.doctor_id.in_(dept_doctors)
            ).options(joinedload(Patient.user)).distinct().all()
        else:
            patients = db.query(Patient).options(joinedload(Patient.user)).all()

        # Get staff (assuming staff might be department-specific in future)
        staff = db.query(Staff).options(joinedload(Staff.user)).all()

        return {
            "doctors": doctors,
            "patients": patients,
            "staff": staff
        }
    except Exception as e:
        print(f"Error fetching users by department: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch users by department"
        )