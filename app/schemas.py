from __future__ import annotations  # Add this at the top
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, ForwardRef, Dict
from enum import Enum
from pydantic import BaseModel
from datetime import datetime, date, time

class UserRole(str, Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    STAFF = "STAFF"


class LoginRequest(BaseModel):
    username: str
    password: str
    role: UserRole


# Shared properties for Patient
class PatientBase(BaseModel):
    medical_history: Optional[str] = None
    emergency_contact: Optional[str] = None

# Base User Registration
class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole

    class Config:
        orm_mode = True

# Doctor Registration
class DoctorCreate(UserBase):
    specialization: str
    consultation_fee: float
    department_id: int

# Patient Registration (already exists, but adding here for completeness)
class PatientCreate(UserBase):
    medical_history: Optional[str] = None
    emergency_contact: str

# Properties for updating an existing Patient
class PatientUpdate(PatientBase):
    medical_history: Optional[str] = None
    emergency_contact: Optional[str] = None

# Base response classes to avoid circular dependencies
class PatientBaseResponse(PatientBase):
    id: int
    user_id: int
    user: UserBase

    class Config:
        orm_mode = True

class StaffBaseResponse(BaseModel):
    id: int
    user_id: int
    user: UserBase
    name: str

    class Config:
        orm_mode = True

# Updated response classes
class PatientResponse(PatientBaseResponse):
    staff_assignments: List["PatientStaffAssignmentBaseResponse"] = []

    class Config:
        orm_mode = True

class StaffResponse(StaffBaseResponse):
    assigned_patients: List["PatientStaffAssignmentBaseResponse"] = []

    class Config:
        orm_mode = True

class PatientStaffAssignmentBaseResponse(BaseModel):
    id: int
    patient_id: int
    staff_id: int
    assigned_date: datetime

    class Config:
        orm_mode = True

class PatientStaffAssignmentResponse(PatientStaffAssignmentBaseResponse):
    patient: PatientBaseResponse
    staff: StaffBaseResponse

    class Config:
        orm_mode = True

class TimeSlotBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    is_available: bool = True

class TimeSlotCreate(TimeSlotBase):
    doctor_id: int

class TimeSlotResponse(TimeSlotBase):
    id: int
    doctor_id: int

    class Config:
        orm_mode = True

class DoctorScheduleBase(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time
    is_available: bool = True

class DoctorScheduleCreate(DoctorScheduleBase):
    doctor_id: int

class DoctorScheduleResponse(DoctorScheduleBase):
    id: int
    doctor_id: int

    class Config:
        orm_mode = True

class AppointmentBase(BaseModel):
    purpose: str
    appointment_date: datetime

class AppointmentCreate(AppointmentBase):
    doctor_id: int
    time_slot_id: int
    patient_id: int

class AppointmentResponse(AppointmentBase):
    id: int
    patient_id: int
    doctor_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DoctorAvailabilityResponse(BaseModel):
    doctor_id: int
    doctor_name: str
    specialization: str
    available_slots: List[TimeSlotResponse]

    class Config:
        orm_mode = True

# Add these new schemas for appointment responses
class AppointmentListResponse(BaseModel):
    id: int
    doctor_name: str
    appointment_date: datetime
    time_slot: str
    status: str
    purpose: str

    class Config:
        orm_mode = True

# Add these new schemas
class DoctorScheduleUpdate(BaseModel):
    doctor_id: int
    day_of_week: int
    start_time: time
    end_time: time
    is_available: bool

class AppointmentStatusUpdate(BaseModel):
    status: str

class DoctorAppointmentResponse(BaseModel):
    id: int
    patient_name: str
    appointment_date: datetime
    time_slot: str
    status: str
    purpose: str

    class Config:
        orm_mode = True

# Add these new schemas
class MedicalHistoryBase(BaseModel):
    condition: str
    diagnosis_date: datetime
    treatment: str
    is_chronic: bool = False
    notes: Optional[str] = None

class MedicalHistoryCreate(MedicalHistoryBase):
    patient_id: int

class MedicalHistoryResponse(MedicalHistoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class DoctorNoteBase(BaseModel):
    note: str
    appointment_id: Optional[int] = None

class DoctorNoteCreate(DoctorNoteBase):
    patient_id: int
    doctor_id: int

class DoctorNoteResponse(DoctorNoteBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    doctor_name: str

    class Config:
        orm_mode = True

# Add these new schemas
class InvoiceItemBase(BaseModel):
    description: str
    amount: float
    item_type: str

class InvoiceItemCreate(InvoiceItemBase):
    invoice_id: int

class InvoiceItemResponse(InvoiceItemBase):
    id: int

    class Config:
        orm_mode = True

class InvoiceBase(BaseModel):
    patient_id: int
    appointment_id: int
    total_amount: float
    status: str = "PENDING"

class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemBase]

class InvoiceResponse(InvoiceBase):
    id: int
    created_at: datetime
    paid_at: Optional[datetime]
    items: List[InvoiceItemResponse]

    class Config:
        orm_mode = True

# Add Admin schemas
class AdminBase(BaseModel):
    username: str
    email: EmailStr

class AdminCreate(AdminBase):
    password: str

class AdminLogin(BaseModel):
    username: str
    password: str

# Add Staff schemas
class StaffBase(BaseModel):
    name: str

class StaffCreate(UserBase):
    name: str

    class Config:
        orm_mode = True

# Add Equipment schemas
class EquipmentBase(BaseModel):
    name: str
    category: str
    status: str
    department_id: int
    quantity: int = 1

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    department_id: Optional[int] = None
    quantity: Optional[int] = None
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None

class EquipmentResponse(EquipmentBase):
    id: int
    unit_statuses: Dict[str, str] = {}
    last_maintenance: Optional[datetime]
    next_maintenance: Optional[datetime]
    added_date: datetime
    modified_date: Optional[datetime]
    department: Optional[DepartmentResponse]

    class Config:
        orm_mode = True

# Add Assignment schemas
class PatientStaffAssignmentCreate(BaseModel):
    patient_id: int
    staff_id: int

# Reorder and update the schemas to avoid circular dependencies
class DepartmentBase(BaseModel):
    name: str
    budget: Optional[float] = None

    class Config:
        orm_mode = True

class DepartmentResponse(DepartmentBase):
    id: int

    class Config:
        orm_mode = True

# Doctor schemas
class DoctorBase(BaseModel):
    specialization: str
    consultation_fee: float
    department_id: int

class DoctorResponse(DoctorBase):
    id: int
    user_id: int
    user: UserBase
    department: Optional[DepartmentResponse] = None

    class Config:
        orm_mode = True

# Extended Department response (with doctors)
class DepartmentWithDoctorsResponse(DepartmentResponse):
    doctors: List[DoctorResponse] = []

# Add this new response model for users by department
class UsersByDepartmentResponse(BaseModel):
    doctors: List[DoctorResponse] = []
    patients: List[PatientResponse] = []
    staff: List[StaffResponse] = []

    class Config:
        orm_mode = True

# Add these to your equipment schemas
class EquipmentUnitStatus(BaseModel):
    status: str

class EquipmentUnitResponse(BaseModel):
    equipment_id: int
    unit_number: int
    status: str

    class Config:
        orm_mode = True
