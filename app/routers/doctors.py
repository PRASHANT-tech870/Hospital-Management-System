from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from datetime import datetime, time
from app.db import get_db
from app.models import Doctor, DoctorSchedule, Appointment, TimeSlot, User, Patient
from app.schemas import (
    DoctorScheduleUpdate, DoctorScheduleResponse, 
    DoctorAppointmentResponse
)

router = APIRouter(prefix="/api/doctors", tags=["doctors"])

@router.get("/specializations", response_model=List[str])
def get_specializations(db: Session = Depends(get_db)):
    # Get unique specializations from doctors table
    specializations = db.query(Doctor.specialization).distinct().all()
    return [spec[0] for spec in specializations if spec[0]]

@router.get("/", response_model=List[dict])
def get_doctors(specialization: str = None, db: Session = Depends(get_db)):
    query = db.query(Doctor)
    if specialization:
        query = query.filter(Doctor.specialization == specialization)
    
    doctors = query.all()
    return [
        {
            "id": doc.id,
            "name": doc.user.username,
            "specialization": doc.specialization,
        }
        for doc in doctors
    ]

@router.get("/{doctor_id}/schedule", response_model=Dict[str, DoctorScheduleResponse])
def get_doctor_schedule(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    try:
        schedules = db.query(DoctorSchedule).filter(
            DoctorSchedule.doctor_id == doctor_id
        ).all()

        # Convert to dictionary with day_of_week as key
        schedule_dict = {}
        for schedule in schedules:
            schedule_dict[str(schedule.day_of_week)] = schedule

        return schedule_dict

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/schedule/update", response_model=DoctorScheduleResponse)
def update_doctor_schedule(
    schedule: DoctorScheduleUpdate,
    db: Session = Depends(get_db)
):
    try:
        # Check if schedule exists for this day
        existing_schedule = db.query(DoctorSchedule).filter(
            DoctorSchedule.doctor_id == schedule.doctor_id,
            DoctorSchedule.day_of_week == schedule.day_of_week
        ).first()

        if existing_schedule:
            # Update existing schedule
            existing_schedule.start_time = schedule.start_time
            existing_schedule.end_time = schedule.end_time
            existing_schedule.is_available = schedule.is_available
            db.commit()
            db.refresh(existing_schedule)
            return existing_schedule
        else:
            # Create new schedule
            new_schedule = DoctorSchedule(**schedule.dict())
            db.add(new_schedule)
            db.commit()
            db.refresh(new_schedule)
            return new_schedule

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{doctor_id}/appointments", response_model=List[DoctorAppointmentResponse])
def get_doctor_appointments(
    doctor_id: int,
    status: str = None,
    date: str = None,
    db: Session = Depends(get_db)
):
    try:
        print(f"Getting appointments for doctor {doctor_id}, status: {status}, date: {date}")  # Debug log
        query = db.query(Appointment).filter(Appointment.doctor_id == doctor_id)

        # Apply filters
        if status and status != "all":
            query = query.filter(Appointment.status == status)
        
        if date:
            try:
                # Convert date string to datetime object
                filter_date = datetime.strptime(date, "%Y-%m-%d").date()
                print(f"Filtering by date: {filter_date}")  # Debug log
                
                # Filter appointments for the specific date
                query = query.filter(
                    func.date(Appointment.appointment_date) == filter_date
                )
            except ValueError as e:
                print(f"Date parsing error: {e}")  # Debug log
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid date format. Expected YYYY-MM-DD, got {date}"
                )

        # Join with related tables and order by date
        appointments = query.join(
            Patient, Appointment.patient_id == Patient.id
        ).join(
            User, Patient.user_id == User.id
        ).join(
            TimeSlot, Appointment.time_slot_id == TimeSlot.id
        ).order_by(
            Appointment.appointment_date
        ).all()

        print(f"Found {len(appointments)} appointments")  # Debug log

        # Format response
        formatted_appointments = []
        for appointment in appointments:
            formatted_appointment = {
                "id": appointment.id,
                "patient_name": appointment.patient.user.username,
                "appointment_date": appointment.appointment_date,
                "time_slot": f"{appointment.time_slot.start_time.strftime('%I:%M %p')} - {appointment.time_slot.end_time.strftime('%I:%M %p')}",
                "status": appointment.status,
                "purpose": appointment.purpose
            }
            formatted_appointments.append(formatted_appointment)

        return formatted_appointments

    except Exception as e:
        print(f"Error in get_doctor_appointments: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{doctor_id}/patients", response_model=List[dict])
def get_doctor_patients(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    try:
        # Get unique patients who have appointments with this doctor
        patients = db.query(Patient).join(
            Appointment, Patient.id == Appointment.patient_id
        ).join(
            User, Patient.user_id == User.id
        ).filter(
            Appointment.doctor_id == doctor_id
        ).distinct().all()

        return [
            {
                "id": patient.id,
                "name": patient.user.username,
            }
            for patient in patients
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
