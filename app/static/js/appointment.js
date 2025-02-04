// Load specializations when page loads
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/doctors/specializations');
        const specializations = await response.json();
        
        const specializationSelect = document.getElementById('specialization');
        specializations.forEach(spec => {
            const option = document.createElement('option');
            option.value = spec;
            option.textContent = spec;
            specializationSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading specializations:', error);
    }
});

// Handle specialization selection
document.getElementById('specialization').addEventListener('change', async (e) => {
    const doctorSelect = document.getElementById('doctor');
    doctorSelect.disabled = !e.target.value;
    doctorSelect.innerHTML = '<option value="">-- Select Doctor --</option>';
    
    if (e.target.value) {
        try {
            const response = await fetch(`/api/doctors?specialization=${e.target.value}`);
            const doctors = await response.json();
            
            doctors.forEach(doctor => {
                const option = document.createElement('option');
                option.value = doctor.id;
                option.textContent = doctor.name;
                doctorSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading doctors:', error);
        }
    }
});

// Handle doctor selection
document.getElementById('doctor').addEventListener('change', (e) => {
    const dateInput = document.getElementById('appointment-date');
    dateInput.disabled = !e.target.value;
    if (e.target.value) {
        // Set min date to today
        const today = new Date().toISOString().split('T')[0];
        dateInput.min = today;
        
        // Set max date to 30 days from now
        const maxDate = new Date();
        maxDate.setDate(maxDate.getDate() + 30);
        dateInput.max = maxDate.toISOString().split('T')[0];
    }
});

// Handle date selection
document.getElementById('appointment-date').addEventListener('change', async (e) => {
    const timeSlotSelect = document.getElementById('time-slot');
    const doctorId = document.getElementById('doctor').value;
    
    timeSlotSelect.disabled = !e.target.value;
    timeSlotSelect.innerHTML = '<option value="">-- Select Time Slot --</option>';
    
    if (e.target.value && doctorId) {
        try {
            const response = await fetch(
                `/api/appointments/doctors/${doctorId}/availability?date=${e.target.value}`
            );
            const slots = await response.json();
            
            slots.forEach(slot => {
                const option = document.createElement('option');
                option.value = slot.id;
                option.textContent = `${slot.start_time} - ${slot.end_time}`;
                timeSlotSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading time slots:', error);
        }
    }
});

// Handle form submission
document.getElementById('appointment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        doctor_id: document.getElementById('doctor').value,
        time_slot_id: document.getElementById('time-slot').value,
        appointment_date: document.getElementById('appointment-date').value,
        purpose: document.getElementById('purpose').value
    };
    
    try {
        const response = await fetch('/api/appointments/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            alert('Appointment booked successfully!');
            // Refresh appointments list
            loadAppointments();
        } else {
            const error = await response.json();
            alert(error.detail || 'Error booking appointment');
        }
    } catch (error) {
        console.error('Error booking appointment:', error);
        alert('Error booking appointment');
    }
}); 