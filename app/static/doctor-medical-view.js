// Load patients list
async function loadPatientsList() {
    const userData = JSON.parse(localStorage.getItem('user'));
    if (!userData) return;

    try {
        const response = await fetch(`/api/doctors/${userData.id}/patients`);
        if (!response.ok) throw new Error('Failed to fetch patients');

        const patients = await response.json();
        const patientSelect = document.getElementById('patient-select');
        
        patients.forEach(patient => {
            const option = document.createElement('option');
            option.value = patient.id;
            option.textContent = `${patient.name} (ID: ${patient.id})`;
            patientSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading patients:', error);
    }
}

// Load patient's medical history
async function loadPatientHistory(patientId) {
    try {
        const [historyResponse, notesResponse] = await Promise.all([
            fetch(`/api/medical/history/patient/${patientId}`),
            fetch(`/api/medical/notes/patient/${patientId}`)
        ]);

        if (!historyResponse.ok || !notesResponse.ok) 
            throw new Error('Failed to fetch patient data');

        const [histories, notes] = await Promise.all([
            historyResponse.json(),
            notesResponse.json()
        ]);

        const historyList = document.getElementById('patient-history-list');
        historyList.innerHTML = '';

        // Display medical history
        if (histories.length > 0) {
            const historySection = document.createElement('div');
            historySection.innerHTML = '<h4>Medical History</h4>';
            histories.forEach(history => {
                const historyElement = document.createElement('div');
                historyElement.className = 'history-item';
                historyElement.innerHTML = `
                    <h4>${history.condition}</h4>
                    <p>Diagnosed: ${new Date(history.diagnosis_date).toLocaleDateString()}</p>
                    <p>Treatment: ${history.treatment}</p>
                    ${history.is_chronic ? '<span class="chronic-badge">Chronic</span>' : ''}
                    ${history.notes ? `<p>Notes: ${history.notes}</p>` : ''}
                `;
                historySection.appendChild(historyElement);
            });
            historyList.appendChild(historySection);
        }

        // Display doctor notes
        if (notes.length > 0) {
            const notesSection = document.createElement('div');
            notesSection.innerHTML = '<h4>Doctor Notes</h4>';
            notes.forEach(note => {
                const noteElement = document.createElement('div');
                noteElement.className = 'note-item';
                noteElement.innerHTML = `
                    <p class="note-text">${note.note}</p>
                    <p class="note-meta">By Dr. ${note.doctor_name} on ${new Date(note.created_at).toLocaleDateString()}</p>
                `;
                notesSection.appendChild(noteElement);
            });
            historyList.appendChild(notesSection);
        }

        // Show add note section
        document.getElementById('add-note-section').style.display = 'block';
    } catch (error) {
        console.error('Error loading patient history:', error);
    }
}

// Handle patient selection
document.getElementById('patient-select').addEventListener('change', (e) => {
    const patientId = e.target.value;
    if (patientId) {
        loadPatientHistory(patientId);
    } else {
        document.getElementById('patient-history-list').innerHTML = '';
        document.getElementById('add-note-section').style.display = 'none';
    }
});

// Handle note form submission
document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;

    const userData = JSON.parse(localStorage.getItem('user'));
    const patientId = document.getElementById('patient-select').value;
    
    if (!userData || !patientId) return;

    // Show loading state
    form.classList.add('note-form-loading');
    submitButton.textContent = 'Adding Note...';

    try {
        const formData = {
            patient_id: parseInt(patientId),
            doctor_id: parseInt(userData.id),
            note: document.getElementById('doctor-note').value
        };

        const response = await fetch('/api/medical/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        let errorMessage = 'Error adding note';
        if (!response.ok) {
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch {
                errorMessage = `Server error: ${response.status}`;
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();
        alert('Note added successfully');
        form.reset();
        loadPatientHistory(patientId);
    } catch (error) {
        console.error('Error adding note:', error);
        alert(error.message || 'Error adding note');
    } finally {
        // Reset form state
        form.classList.remove('note-form-loading');
        submitButton.textContent = originalButtonText;
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', loadPatientsList); 