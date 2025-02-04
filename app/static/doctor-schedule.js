// Load doctor's schedule
async function loadDoctorSchedule() {
    const userData = JSON.parse(localStorage.getItem('user'));
    if (!userData) return;

    try {
        const response = await fetch(`/api/doctors/${userData.id}/schedule`);
        if (!response.ok) throw new Error('Failed to fetch schedule');
        
        const schedules = await response.json();
        console.log('Doctor schedules:', schedules);
        
        // Update form with existing schedule if available
        const daySelect = document.getElementById('day');
        if (schedules[daySelect.value]) {
            const schedule = schedules[daySelect.value];
            document.getElementById('start-time').value = schedule.start_time;
            document.getElementById('end-time').value = schedule.end_time;
            document.getElementById('is-available').checked = schedule.is_available;
        }
    } catch (error) {
        console.error('Error loading schedule:', error);
    }
}

// Handle schedule form submission
document.getElementById('schedule-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const userData = JSON.parse(localStorage.getItem('user'));
    if (!userData) return;

    const formData = {
        doctor_id: parseInt(userData.id),
        day_of_week: parseInt(document.getElementById('day').value),
        start_time: document.getElementById('start-time').value,
        end_time: document.getElementById('end-time').value,
        is_available: document.getElementById('is-available').checked
    };

    try {
        const response = await fetch('/api/doctors/schedule/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            alert('Schedule updated successfully!');
            loadDoctorSchedule();
        } else {
            const error = await response.json();
            alert(error.detail || 'Error updating schedule');
        }
    } catch (error) {
        console.error('Error updating schedule:', error);
        alert('Error updating schedule');
    }
});

// Load appointments
async function loadAppointments() {
    const userData = JSON.parse(localStorage.getItem('user'));
    if (!userData) return;

    const statusFilter = document.getElementById('status-filter').value;
    const dateFilter = document.getElementById('date-filter').value;
    
    try {
        let url = `/api/doctors/${userData.id}/appointments?`;
        
        // Add status filter if not 'all'
        if (statusFilter && statusFilter !== 'all') {
            url += `status=${statusFilter}&`;
        }
        
        // Add date filter if selected
        if (dateFilter) {
            // Format date to YYYY-MM-DD
            const formattedDate = new Date(dateFilter).toISOString().split('T')[0];
            url += `date=${formattedDate}`;
        }

        console.log('Fetching appointments:', url); // Debug log
        
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch appointments');

        const appointments = await response.json();
        console.log('Received appointments:', appointments); // Debug log

        const appointmentsList = document.getElementById('appointments-list');
        appointmentsList.innerHTML = '';

        if (appointments.length === 0) {
            appointmentsList.innerHTML = '<p class="no-appointments">No appointments found</p>';
            return;
        }

        appointments.forEach(appointment => {
            const appointmentElement = document.createElement('div');
            appointmentElement.className = 'appointment-item';
            appointmentElement.innerHTML = `
                <p><strong>Patient:</strong> ${appointment.patient_name}</p>
                <p><strong>Date:</strong> ${new Date(appointment.appointment_date).toLocaleDateString()}</p>
                <p><strong>Time:</strong> ${appointment.time_slot}</p>
                <p><strong>Status:</strong> ${appointment.status}</p>
                <p><strong>Purpose:</strong> ${appointment.purpose}</p>
                <div class="appointment-actions">
                    ${appointment.status === 'SCHEDULED' ? `
                        <button class="confirm-btn" onclick="confirmAppointment(${appointment.id})">Confirm</button>
                    ` : ''}
                    ${appointment.status === 'CONFIRMED' ? `
                        <button class="complete-btn" onclick="completeAppointment(${appointment.id})">Complete</button>
                    ` : ''}
                    ${['SCHEDULED', 'CONFIRMED'].includes(appointment.status) ? `
                        <button class="cancel-btn" onclick="cancelAppointment(${appointment.id})">Cancel</button>
                    ` : ''}
                </div>
            `;
            appointmentsList.appendChild(appointmentElement);
        });
    } catch (error) {
        console.error('Error loading appointments:', error);
        document.getElementById('appointments-list').innerHTML = 
            '<p class="error-message">Error loading appointments</p>';
    }
}

// Update appointment status
async function updateAppointmentStatus(appointmentId, newStatus) {
    try {
        const response = await fetch(`/api/appointments/${appointmentId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                status: newStatus
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update appointment status');
        }

        const result = await response.json();
        console.log('Status update result:', result);  // Debug log

        // Refresh the appointments list
        loadAppointments();
        
        // Show success message
        alert(`Appointment ${result.status.toLowerCase()} successfully`);
        
    } catch (error) {
        console.error('Error updating appointment status:', error);
        alert(error.message || 'Error updating appointment status');
    }
}

// Add these helper functions for appointment actions
function confirmAppointment(appointmentId) {
    updateAppointmentStatus(appointmentId, 'CONFIRMED');
}

function completeAppointment(appointmentId) {
    updateAppointmentStatus(appointmentId, 'COMPLETED');
}

function cancelAppointment(appointmentId) {
    if (confirm('Are you sure you want to cancel this appointment?')) {
        updateAppointmentStatus(appointmentId, 'CANCELLED');
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    loadDoctorSchedule();
    loadAppointments();

    // Set default date filter to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date-filter').value = today;

    // Add event listeners for filters
    document.getElementById('status-filter').addEventListener('change', loadAppointments);
    document.getElementById('date-filter').addEventListener('change', loadAppointments);
    document.getElementById('day').addEventListener('change', loadDoctorSchedule);
}); 