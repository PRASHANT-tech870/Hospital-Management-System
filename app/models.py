from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Time, Date, Boolean, Text, JSON, TypeDecorator
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
from datetime import datetime, time
import json

# Custom JSON type for SQLite compatibility
class SQLiteJSON(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return {}

# User table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum("DOCTOR", "PATIENT", "STAFF"), nullable=False)  # Added STAFF back

    # Relationships
    doctor = relationship("Doctor", back_populates="user", uselist=False)
    patient = relationship("Patient", back_populates="user", uselist=False)
    staff = relationship("Staff", back_populates="user", uselist=False)

# Patient table
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    medical_history = Column(String)
    emergency_contact = Column(String)

    # Relationships
    user = relationship("User", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    accounts = relationship("Account", back_populates="patient")
    medical_histories = relationship("MedicalHistory", back_populates="patient")
    doctor_notes = relationship("DoctorNote", back_populates="patient")
    invoices = relationship("Invoice", back_populates="patient")
    staff_assignments = relationship("PatientStaffAssignment", back_populates="patient")

# Doctor table
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    specialization = Column(String)
    consultation_fee = Column(Float)
    department_id = Column(Integer, ForeignKey("department.id"))

    # Relationships
    user = relationship("User", back_populates="doctor")
    department = relationship("Department", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")
    schedules = relationship("DoctorSchedule", back_populates="doctor")
    time_slots = relationship("TimeSlot", back_populates="doctor")
    doctor_notes = relationship("DoctorNote", back_populates="doctor")

# Department table
class Department(Base):
    __tablename__ = "department"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    budget = Column(Float)

    # Relationships
    doctors = relationship("Doctor", back_populates="department")
    equipment = relationship("Equipment", back_populates="department")

# Equipment table
class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String)
    status = Column(String)
    department_id = Column(Integer, ForeignKey("department.id"))
    quantity = Column(Integer, default=1)
    unit_statuses = Column(SQLiteJSON, default=dict)
    last_maintenance = Column(DateTime, nullable=True)
    next_maintenance = Column(DateTime, nullable=True)
    added_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    department = relationship("Department", back_populates="equipment")

    @property
    def get_unit_status(self, unit_number: str) -> str:
        """Get status for a specific unit"""
        if self.unit_statuses and str(unit_number) in self.unit_statuses:
            return self.unit_statuses[str(unit_number)]
        return self.status

# Account table
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    total_amount = Column(Float)
    payment_status = Column(String)

    # Relationships
    patient = relationship("Patient", back_populates="accounts")

# Appointment table
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"))
    appointment_date = Column(DateTime, nullable=False)
    status = Column(Enum("SCHEDULED", "CONFIRMED", "COMPLETED", "CANCELLED", "RESCHEDULED"), default="SCHEDULED")
    purpose = Column(String)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    time_slot = relationship("TimeSlot", back_populates="appointment")
    doctor_notes = relationship("DoctorNote", back_populates="appointment")
    invoice = relationship("Invoice", back_populates="appointment", uselist=False)

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    day_of_week = Column(Integer)  # 0-6 for Monday-Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)

    # Relationship
    doctor = relationship("Doctor", back_populates="schedules")

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)

    # Relationships
    doctor = relationship("Doctor", back_populates="time_slots")
    appointment = relationship("Appointment", back_populates="time_slot", uselist=False)

class MedicalHistory(Base):
    __tablename__ = "medical_histories"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    condition = Column(String(255))
    diagnosis_date = Column(DateTime)
    treatment = Column(Text)
    is_chronic = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    patient = relationship("Patient", back_populates="medical_histories")

class DoctorNote(Base):
    __tablename__ = "doctor_notes"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    note = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    patient = relationship("Patient", back_populates="doctor_notes")
    doctor = relationship("Doctor", back_populates="doctor_notes")
    appointment = relationship("Appointment", back_populates="doctor_notes")

# Add these new models
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    total_amount = Column(Float)
    status = Column(String, default="PENDING")  # PENDING, PAID, CANCELLED
    created_at = Column(DateTime, server_default=func.now())
    paid_at = Column(DateTime, nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="invoices")
    appointment = relationship("Appointment", back_populates="invoice")
    items = relationship("InvoiceItem", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    description = Column(String)
    amount = Column(Float)
    item_type = Column(String)  # CONSULTATION, TEST, MEDICATION, etc.

    invoice = relationship("Invoice", back_populates="items")

# Add Admin model
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

# Add Staff model
class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="staff")
    assigned_patients = relationship("PatientStaffAssignment", back_populates="staff")

# Add PatientStaffAssignment model for staff-patient assignments
class PatientStaffAssignment(Base):
    __tablename__ = "patient_staff_assignments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    staff_id = Column(Integer, ForeignKey("staff.id"))
    assigned_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="staff_assignments")
    staff = relationship("Staff", back_populates="assigned_patients")
