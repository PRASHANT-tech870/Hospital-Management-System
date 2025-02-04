// Initialize all event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    loadMedicalHistory();
    
    // Add form submission handler
    const historyForm = document.getElementById('history-form');
    if (historyForm) {
        historyForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const userData = JSON.parse(localStorage.getItem('user'));
            if (!userData) return;

            const formData = {
                patient_id: userData.id,
                condition: document.getElementById('condition').value,
                diagnosis_date: new Date(document.getElementById('diagnosis-date').value),
                treatment: document.getElementById('treatment').value,
                is_chronic: document.getElementById('is-chronic').checked,
                notes: document.getElementById('history-notes').value
            };

            try {
                const response = await fetch('/api/medical/history', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    alert('Medical history added successfully');
                    document.getElementById('add-history-form').style.display = 'none';
                    document.getElementById('history-form').reset();
                    loadMedicalHistory();
                } else {
                    const error = await response.json();
                    alert(error.detail || 'Error adding medical history');
                }
            } catch (error) {
                console.error('Error adding medical history:', error);
                alert('Error adding medical history');
            }
        });
    }
});

// Make showAddHistoryForm function global
window.showAddHistoryForm = function() {
    document.getElementById('add-history-form').style.display = 'block';
};

// Load medical history and doctor notes
async function loadMedicalHistory() {
    const userData = JSON.parse(localStorage.getItem('user'));
    if (!userData) return;

    try {
        // Fetch both medical history and doctor notes
        const [historyResponse, notesResponse] = await Promise.all([
            fetch(`/api/medical/history/patient/${userData.id}`),
            fetch(`/api/medical/notes/patient/${userData.id}`)
        ]);

        if (!historyResponse.ok || !notesResponse.ok) {
            throw new Error('Failed to fetch medical data');
        }

        const [histories, doctorNotes] = await Promise.all([
            historyResponse.json(),
            notesResponse.json()
        ]);

        // Display medical history
        const historyList = document.getElementById('medical-history-list');
        historyList.innerHTML = '<h4>Medical Conditions</h4>';

        if (histories.length === 0) {
            historyList.innerHTML += '<p class="no-history">No medical history records found.</p>';
        } else {
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
                historyList.appendChild(historyElement);
            });
        }

        // Display doctor notes
        const notesList = document.getElementById('doctor-notes-list');
        notesList.innerHTML = '';

        if (doctorNotes.length === 0) {
            notesList.innerHTML = '<p class="no-notes">No doctor notes available.</p>';
        } else {
            doctorNotes.forEach(note => {
                const noteElement = document.createElement('div');
                noteElement.className = 'note-item';
                noteElement.innerHTML = `
                    <p class="note-text">${note.note}</p>
                    <p class="note-meta">By Dr. ${note.doctor_name} on ${new Date(note.created_at).toLocaleDateString()}</p>
                `;
                notesList.appendChild(noteElement);
            });
        }
    } catch (error) {
        console.error('Error loading medical data:', error);
        document.getElementById('medical-history-list').innerHTML = 
            '<p class="error-message">Error loading medical history</p>';
        document.getElementById('doctor-notes-list').innerHTML = 
            '<p class="error-message">Error loading doctor notes</p>';
    }
} 