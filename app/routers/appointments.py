from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.db import get_db
from app.models import Doctor, TimeSlot, Appointment, DoctorSchedule, User, Invoice, InvoiceItem
from app.schemas import (
    TimeSlotCreate, TimeSlotResponse, AppointmentCreate, 
    AppointmentResponse, DoctorAvailabilityResponse, AppointmentStatusUpdate
)

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

@router.get("/doctors/{doctor_id}/availability", response_model=List[TimeSlotResponse])
def get_doctor_availability(
    doctor_id: int,
    date: datetime,
    db: Session = Depends(get_db)
):
    try:
        print(f"Received request for doctor_id: {doctor_id}, date: {date}")  # Debug log
        
        # Convert string date to datetime if needed
        if isinstance(date, str):
            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        
        print(f"Parsed date: {date}, weekday: {date.weekday()}")  # Debug log

        # Get doctor's schedule for the given day
        day_of_week = date.weekday()
        schedule = db.query(DoctorSchedule).filter(
            DoctorSchedule.doctor_id == doctor_id,
            DoctorSchedule.day_of_week == day_of_week,
            DoctorSchedule.is_available == True
        ).first()

        print(f"Found schedule: {schedule}")  # Debug log

        if not schedule:
            print(f"No schedule found for doctor {doctor_id} on day {day_of_week}")  # Debug log
            return []

        # Get existing appointments/time slots for the day
        existing_slots = db.query(TimeSlot).filter(
            TimeSlot.doctor_id == doctor_id,
            TimeSlot.date == date.date()
        ).all()

        # Generate available time slots
        available_slots = []
        current_time = schedule.start_time
        slot_duration = timedelta(minutes=30)  # 30-minute slots

        while current_time < schedule.end_time:
            slot_end_time = (datetime.combine(date.date(), current_time) + slot_duration).time()
            
            # Check if slot is already booked
            is_available = not any(
                slot.start_time == current_time and not slot.is_available 
                for slot in existing_slots
            )

            if is_available:
                # Create a new time slot in the database
                time_slot = TimeSlot(
                    doctor_id=doctor_id,
                    date=date.date(),
                    start_time=current_time,
                    end_time=slot_end_time,
                    is_available=True
                )
                db.add(time_slot)
                db.commit()
                db.refresh(time_slot)

                available_slots.append(
                    TimeSlotResponse(
                        id=time_slot.id,
                        date=date.date(),
                        start_time=current_time,
                        end_time=slot_end_time,
                        is_available=True,
                        doctor_id=doctor_id
                    )
                )

            current_time = slot_end_time

        return available_slots

    except Exception as e:
        print(f"Error in get_doctor_availability: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/book", response_model=AppointmentResponse)
def book_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db)
):
    try:
        print(f"Booking appointment: {appointment}")  # Debug log
        
        # Verify time slot is available
        time_slot = db.query(TimeSlot).filter(
            TimeSlot.id == appointment.time_slot_id,
            TimeSlot.is_available == True
        ).first()

        if not time_slot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected time slot is not available"
            )

        # Create appointment
        new_appointment = Appointment(
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            time_slot_id=appointment.time_slot_id,
            appointment_date=appointment.appointment_date,
            purpose=appointment.purpose,
            status="SCHEDULED"
        )

        # Mark time slot as unavailable
        time_slot.is_available = False

        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)

        print(f"Appointment booked successfully: {new_appointment.id}")  # Debug log
        return new_appointment

    except Exception as e:
        print(f"Error booking appointment: {str(e)}")  # Debug log
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/doctors/available", response_model=List[DoctorAvailabilityResponse])
def get_available_doctors(
    specialization: str = None,
    date: datetime = None,
    db: Session = Depends(get_db)
):
    query = db.query(Doctor)
    if specialization:
        query = query.filter(Doctor.specialization == specialization)
    
    doctors = query.all()
    available_doctors = []

    for doctor in doctors:
        available_slots = get_doctor_availability(doctor.id, date, db)
        if available_slots:
            available_doctors.append({
                "doctor_id": doctor.id,
                "doctor_name": doctor.user.username,
                "specialization": doctor.specialization,
                "available_slots": available_slots
            })

    return available_doctors

@router.get("/patient/{patient_id}", response_model=List[dict])
def get_patient_appointments(
    patient_id: int,
    db: Session = Depends(get_db)
):
    try:
        # Get all appointments for the patient
        appointments = db.query(Appointment).filter(
            Appointment.patient_id == patient_id
        ).join(
            Doctor, Appointment.doctor_id == Doctor.id
        ).join(
            User, Doctor.user_id == User.id
        ).join(
            TimeSlot, Appointment.time_slot_id == TimeSlot.id
        ).all()

        # Format appointments for response
        formatted_appointments = []
        for appointment in appointments:
            formatted_appointments.append({
                "id": appointment.id,
                "doctor_name": appointment.doctor.user.username,
                "appointment_date": appointment.appointment_date,
                "time_slot": f"{appointment.time_slot.start_time.strftime('%I:%M %p')} - {appointment.time_slot.end_time.strftime('%I:%M %p')}",
                "status": appointment.status,
                "purpose": appointment.purpose
            })

        return formatted_appointments

    except Exception as e:
        print(f"Error fetching appointments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching appointments: {str(e)}"
        )

@router.put("/{appointment_id}/status")
def update_appointment_status(
    appointment_id: int,
    status_update: AppointmentStatusUpdate,
    db: Session = Depends(get_db)
):
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        appointment.status = status_update.status
        
        # Generate invoice when appointment is completed
        if status_update.status == "COMPLETED" and not appointment.invoice:
            try:
                # Get doctor's consultation fee
                doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
                
                # Create invoice
                invoice = Invoice(
                    patient_id=appointment.patient_id,
                    appointment_id=appointment.id,
                    total_amount=doctor.consultation_fee,
                    status="PENDING"
                )
                db.add(invoice)
                db.commit()
                db.refresh(invoice)
                
                # Add consultation fee as invoice item
                invoice_item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=f"Consultation with Dr. {doctor.user.username}",
                    amount=doctor.consultation_fee,
                    item_type="CONSULTATION"
                )
                db.add(invoice_item)
                db.commit()
            except Exception as e:
                print(f"Error creating invoice: {str(e)}")
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error creating invoice: {str(e)}"
                )
        
        db.commit()
        return {
            "id": appointment.id,
            "status": appointment.status,
            "message": "Status updated successfully"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        print(f"Error updating appointment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
