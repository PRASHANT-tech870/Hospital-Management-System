// Load specializations when page loads
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/doctors/specializations');
        if (!response.ok) {
            throw new Error('Failed to fetch specializations');
        }
        const specializations = await response.json();
        console.log('Specializations:', specializations);
        
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
            if (!response.ok) throw new Error('Failed to fetch doctors');
            const doctors = await response.json();
            console.log('Doctors:', doctors);
            
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
        const today = new Date();
        const minDate = today.toISOString().split('T')[0];
        dateInput.min = minDate;
        
        // Set max date to 30 days from now
        const maxDate = new Date();
        maxDate.setDate(maxDate.getDate() + 30);
        dateInput.max = maxDate.toISOString().split('T')[0];
        
        dateInput.value = minDate; // Set default value to today
        // Trigger date change event to load time slots
        dateInput.dispatchEvent(new Event('change'));
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
            // Format date for the API
            const selectedDate = new Date(e.target.value);
            const formattedDate = selectedDate.toISOString();
            
            const response = await fetch(
                `/api/appointments/doctors/${doctorId}/availability?date=${formattedDate}`
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const slots = await response.json();
            console.log('Time slots:', slots);
            
            if (slots.length === 0) {
                timeSlotSelect.innerHTML = '<option value="">No available slots</option>';
                return;
            }
            
            slots.forEach(slot => {
                const option = document.createElement('option');
                option.value = slot.id;
                const startTime = new Date(`2000-01-01T${slot.start_time}`).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                const endTime = new Date(`2000-01-01T${slot.end_time}`).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                option.textContent = `${startTime} - ${endTime}`;
                timeSlotSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading time slots:', error);
            timeSlotSelect.innerHTML = '<option value="">Error loading time slots</option>';
        }
    }
});

// Handle form submission
document.getElementById('appointment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const userData = JSON.parse(localStorage.getItem('user'));
    if (!userData) {
        alert('Please login to book an appointment');
        return;
    }

    const formData = {
        doctor_id: parseInt(document.getElementById('doctor').value),
        time_slot_id: parseInt(document.getElementById('time-slot').value),
        appointment_date: new Date(document.getElementById('appointment-date').value).toISOString(),
        purpose: document.getElementById('purpose').value,
        patient_id: parseInt(userData.id)
    };

    console.log('Booking appointment:', formData);
    
    try {
        const response = await fetch('/api/appointments/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Appointment booked:', result);
            alert('Appointment booked successfully!');
            // Refresh appointments list
            loadAppointments();
        } else {
            const error = await response.json();
            console.error('Booking error:', error);
            alert(error.detail || 'Error booking appointment');
        }
    } catch (error) {
        console.error('Error booking appointment:', error);
        alert('Error booking appointment. Please try again.');
    }
});

// Function to load existing appointments
async function loadAppointments() {
    const userData = JSON.parse(localStorage.getItem('user'));
    if (!userData) return;

    try {
        const response = await fetch(`/api/appointments/patient/${userData.id}`);
        if (!response.ok) throw new Error('Failed to fetch appointments');
        
        const appointments = await response.json();
        const appointmentsList = document.getElementById('appointments-list');
        appointmentsList.innerHTML = ''; // Clear existing appointments

        appointments.forEach(appointment => {
            const appointmentElement = document.createElement('div');
            appointmentElement.className = 'appointment-item';
            appointmentElement.innerHTML = `
                <p>Doctor: ${appointment.doctor_name}</p>
                <p>Date: ${new Date(appointment.appointment_date).toLocaleDateString()}</p>
                <p>Time: ${appointment.time_slot}</p>
                <p>Status: ${appointment.status}</p>
            `;
            appointmentsList.appendChild(appointmentElement);
        });
    } catch (error) {
        console.error('Error loading appointments:', error);
    }
}

// Load appointments when page loads
document.addEventListener('DOMContentLoaded', loadAppointments); 