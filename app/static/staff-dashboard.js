document.addEventListener('DOMContentLoaded', function() {
    const userData = JSON.parse(localStorage.getItem('user'));
    if (!userData || userData.role !== 'STAFF') {
        window.location.href = '/';
        return;
    }

    document.getElementById('staff-name').textContent = userData.username;
    loadAssignedPatients(userData.id);
});

async function loadAssignedPatients(staffId) {
    try {
        const response = await fetch(`/api/staff/${staffId}/patients`);
        const patients = await response.json();
        
        displayAssignedPatients(patients);
        populatePatientSelect(patients);
    } catch (error) {
        console.error('Error loading assigned patients:', error);
    }
}

function displayAssignedPatients(patients) {
    const list = document.getElementById('assigned-patients-list');
    if (patients.length === 0) {
        list.innerHTML = '<p class="no-data">No patients assigned yet.</p>';
        return;
    }

    list.innerHTML = patients.map(patient => `
        <div class="patient-item">
            <div class="patient-header">
                <h4>${patient.user.username}</h4>
                <span class="patient-id">ID: ${patient.id}</span>
            </div>
            <div class="patient-info">
                <p><strong>Email:</strong> ${patient.user.email}</p>
                <p><strong>Emergency Contact:</strong> ${patient.emergency_contact || 'Not provided'}</p>
                <p><strong>Medical History:</strong> ${patient.medical_history || 'No history available'}</p>
            </div>
            <div class="patient-actions">
                <button onclick="viewPatientDetails(${patient.id})" class="view-btn">View Details</button>
            </div>
        </div>
    `).join('');
}

function populatePatientSelect(patients) {
    const select = document.getElementById('patient-select');
    select.innerHTML = '<option value="">Select Patient</option>' +
        patients.map(patient => `
            <option value="${patient.id}">${patient.user.username}</option>
        `).join('');
}

async function viewPatientDetails(patientId) {
    try {
        const response = await fetch(`/patients/${patientId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch patient details');
        }
        const patient = await response.json();
        
        const patientDetails = `
            <div class="patient-details">
                <h4>Patient Information</h4>
                <div class="info-group">
                    <p><strong>Name:</strong> ${patient?.user?.username || 'N/A'}</p>
                    <p><strong>Email:</strong> ${patient?.user?.email || 'N/A'}</p>
                    <p><strong>Emergency Contact:</strong> ${patient?.emergency_contact || 'Not provided'}</p>
                </div>
                <div class="info-group">
                    <h5>Medical History</h5>
                    <p>${patient?.medical_history || 'No medical history available'}</p>
                </div>
            </div>
        `;
        
        document.getElementById('patient-details').innerHTML = patientDetails;
    } catch (error) {
        console.error('Error fetching patient details:', error);
        document.getElementById('patient-details').innerHTML = `
            <div class="error-message">
                <p>Error loading patient details. Please try again.</p>
                <p>Error: ${error.message}</p>
            </div>
        `;
    }
}

function logout() {
    localStorage.removeItem('user');
    window.location.href = '/';
} 