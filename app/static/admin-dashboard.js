document.addEventListener('DOMContentLoaded', function() {
    const userData = JSON.parse(localStorage.getItem('admin'));
    if (!userData) {
        window.location.href = '/';
        return;
    }

    loadDepartments();
    loadAllUsers();
    loadEquipment();
    loadAssignments();
});

// Tab Management
function showTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(`${tabName}-tab`).classList.add('active');
    document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
}

// Load departments and populate select
async function loadDepartments() {
    try {
        const response = await fetch('/api/admin/departments');
        const departments = await handleResponse(response, 'departments');
        
        // Populate department filter dropdown
        const userDeptSelect = document.getElementById('department-select');
        userDeptSelect.innerHTML = '<option value="">All Departments</option>' +
            departments.map(dept => `
                <option value="${dept.id}">${dept.name}</option>
            `).join('');

        // Populate equipment department dropdown
        const equipmentDeptSelect = document.getElementById('equipment-department');
        if (equipmentDeptSelect) {
            equipmentDeptSelect.innerHTML = '<option value="">Select Department</option>' +
                departments.map(dept => `
                    <option value="${dept.id}">${dept.name}</option>
                `).join('');
        }
    } catch (error) {
        console.error('Error loading departments:', error);
    }
}

// Load users based on department and type filters
async function loadAllUsers() {
    try {
        const departmentId = document.getElementById('department-select').value;
        const userType = document.getElementById('user-type-select').value;
        
        const url = departmentId 
            ? `/api/admin/users-by-department/${departmentId}`
            : '/api/admin/users-by-department/0';
            
        const response = await fetch(url);
        const users = await handleResponse(response, 'users');
        
        displayUsers(users, userType);
        
        // Populate assignment dropdowns
        populateStaffSelect(users.staff);
        populatePatientSelect(users.patients);
    } catch (error) {
        console.error('Error loading users:', error);
        alert(error.message);
    }
}

// Populate staff select dropdown
function populateStaffSelect(staffList) {
    const select = document.getElementById('staff-select');
    if (select) {
        select.innerHTML = '<option value="">Select Staff Member</option>' +
            staffList.map(staff => `
                <option value="${staff.id}">${staff.name}</option>
            `).join('');
    }
}

// Populate patient select dropdown
function populatePatientSelect(patients) {
    const select = document.getElementById('patient-select');
    if (select) {
        select.innerHTML = '<option value="">Select Patient</option>' +
            patients.map(patient => `
                <option value="${patient.id}">${patient.user.username}</option>
            `).join('');
    }
}

// Display users based on type
function displayUsers(users, userType) {
    const usersList = document.getElementById('users-list');
    let html = '';

    if (userType === 'all' || userType === 'doctors') {
        html += '<h4>Doctors</h4>';
        html += '<div class="user-group">';
        users.doctors.forEach(doctor => {
            html += `
                <div class="user-card">
                    <h5>${doctor.user.username}</h5>
                    <p>Specialization: ${doctor.specialization}</p>
                    <p>Email: ${doctor.user.email}</p>
                    <p>Fee: $${doctor.consultation_fee}</p>
                </div>
            `;
        });
        html += '</div>';
    }

    if (userType === 'all' || userType === 'patients') {
        html += '<h4>Patients</h4>';
        html += '<div class="user-group">';
        users.patients.forEach(patient => {
            html += `
                <div class="user-card">
                    <h5>${patient.user.username}</h5>
                    <p>Email: ${patient.user.email}</p>
                    <p>Emergency Contact: ${patient.emergency_contact || 'Not provided'}</p>
                </div>
            `;
        });
        html += '</div>';
    }

    if (userType === 'all' || userType === 'staff') {
        html += '<h4>Staff</h4>';
        html += '<div class="user-group">';
        users.staff.forEach(staff => {
            html += `
                <div class="user-card">
                    <h5>${staff.name}</h5>
                    <p>Email: ${staff.user.email}</p>
                </div>
            `;
        });
        html += '</div>';
    }

    usersList.innerHTML = html;
}

// Equipment Management
async function loadEquipment() {
    try {
        const response = await fetch('/api/admin/equipment');
        const equipment = await response.json();
        displayEquipment(equipment);
    } catch (error) {
        console.error('Error loading equipment:', error);
    }
}

function showAddEquipmentForm() {
    document.getElementById('add-equipment-form').style.display = 'block';
}

// Display Functions
function displayEquipment(equipment) {
    const list = document.getElementById('equipment-list');
    let html = '<div class="equipment-grid">';
    
    equipment.forEach(item => {
        for (let i = 1; i <= item.quantity; i++) {
            const equipmentId = `${item.id}-${i}`;
            const unitStatus = item.unit_statuses[i.toString()] || item.status;
            console.log(`Unit ${i} status:`, unitStatus);  // Debug log
            
            html += `
                <div class="equipment-card">
                    <div class="equipment-header">
                        <h4>${item.name} #${i}</h4>
                        <span class="equipment-id">ID: ${equipmentId}</span>
                    </div>
                    <div class="equipment-content">
                        <p><strong>Category:</strong> ${item.category}</p>
                        <p><strong>Status:</strong> <span class="status-badge ${unitStatus.toLowerCase()}">${unitStatus}</span></p>
                        <p><strong>Department:</strong> ${item.department?.name || 'Not Assigned'}</p>
                    </div>
                    <div class="equipment-actions">
                        <button class="edit-btn" onclick="editEquipmentStatus('${equipmentId}')">
                            <i class="fas fa-edit"></i> Change Status
                        </button>
                        <button class="delete-btn" onclick="deleteEquipmentUnit('${equipmentId}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            `;
        }
    });
    
    html += '</div>';
    list.innerHTML = html;
}

// Edit individual equipment status
async function editEquipmentStatus(equipmentId) {
    const [baseId, unitNumber] = equipmentId.split('-');
    
    // Create a modal dialog for status editing
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Update Equipment Status</h3>
            <p>Equipment ID: ${equipmentId}</p>
            <select id="status-select" class="form-control">
                <option value="AVAILABLE">Available</option>
                <option value="IN_USE">In Use</option>
                <option value="MAINTENANCE">Maintenance</option>
            </select>
            <div class="modal-actions">
                <button onclick="updateEquipmentStatus('${equipmentId}')" class="save-btn">Save</button>
                <button onclick="closeModal()" class="cancel-btn">Cancel</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

async function updateEquipmentStatus(equipmentId) {
    const [baseId, unitNumber] = equipmentId.split('-');
    const newStatus = document.getElementById('status-select').value;
    
    try {
        const response = await fetch(`/api/admin/equipment/${baseId}/unit/${unitNumber}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update status');
        }

        const result = await response.json();
        console.log('Status update result:', result);  // Debug log

        closeModal();
        await loadEquipment(); // Reload to show updated status
        alert('Status updated successfully');
    } catch (error) {
        console.error('Error updating status:', error);
        alert(error.message);
    }
}

// Delete individual equipment unit
async function deleteEquipmentUnit(equipmentId) {
    const [baseId, unitNumber] = equipmentId.split('-');
    
    if (!confirm(`Are you sure you want to delete equipment unit ${equipmentId}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/equipment/${baseId}/unit/${unitNumber}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete equipment unit');
        }
        
        loadEquipment();
        alert('Equipment unit deleted successfully');
    } catch (error) {
        console.error('Error deleting equipment unit:', error);
        alert(error.message);
    }
}

function closeModal() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
    }
}

// Add these functions for equipment management
async function editEquipment(equipmentId) {
    try {
        const response = await fetch(`/api/admin/equipment/${equipmentId}`);
        if (!response.ok) throw new Error('Failed to fetch equipment details');
        const equipment = await response.json();
        
        // Show the form and populate it with current values
        document.getElementById('add-equipment-form').style.display = 'block';
        document.getElementById('equipment-name').value = equipment.name;
        document.getElementById('equipment-category').value = equipment.category;
        document.getElementById('equipment-status').value = equipment.status;
        document.getElementById('equipment-department').value = equipment.department_id;
        document.getElementById('equipment-quantity').value = equipment.quantity;
        
        // Set the form to edit mode
        document.getElementById('equipment-form').dataset.editId = equipmentId;
        
        // Change submit button text
        const submitBtn = document.querySelector('#equipment-form button[type="submit"]');
        submitBtn.textContent = 'Update Equipment';
    } catch (error) {
        console.error('Error loading equipment details:', error);
        alert('Error loading equipment details: ' + error.message);
    }
}

async function deleteEquipment(equipmentId) {
    if (!confirm('Are you sure you want to delete this equipment?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/equipment/${equipmentId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete equipment');
        }
        
        // Reload equipment list after successful deletion
        loadEquipment();
    } catch (error) {
        console.error('Error deleting equipment:', error);
        alert('Error deleting equipment: ' + error.message);
    }
}

// Update the equipment form submit handler
document.getElementById('equipment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('equipment-name').value,
        category: document.getElementById('equipment-category').value,
        status: 'AVAILABLE', // Default status
        department_id: parseInt(document.getElementById('equipment-department').value),
        quantity: parseInt(document.getElementById('equipment-quantity').value)
    };

    try {
        const response = await fetch('/api/admin/equipment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add equipment');
        }

        alert('Equipment added successfully');
        e.target.reset();
        loadEquipment();
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
});

// Filter handlers
function filterByDepartment() {
    loadAllUsers();
}

function filterByUserType() {
    loadAllUsers();
}

// Add these functions
async function loadAssignments() {
    try {
        const response = await fetch('/api/admin/assignments');
        if (!response.ok) throw new Error('Failed to fetch assignments');
        const assignments = await response.json();
        displayAssignments(assignments);
    } catch (error) {
        console.error('Error loading assignments:', error);
    }
}

function displayAssignments(assignments) {
    const list = document.getElementById('assignments-list');
    list.innerHTML = assignments.map(assignment => `
        <div class="assignment-item">
            <p>Staff: ${assignment.staff.name}</p>
            <p>Patient: ${assignment.patient.user.username}</p>
            <p>Assigned: ${new Date(assignment.assigned_date).toLocaleDateString()}</p>
            <button onclick="removeAssignment(${assignment.id})">Remove</button>
        </div>
    `).join('');
}

// Add assignment form handler
document.getElementById('assignment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        staff_id: parseInt(document.getElementById('staff-select').value),
        patient_id: parseInt(document.getElementById('patient-select').value)
    };

    try {
        const response = await fetch('/api/admin/assign-patient', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            alert('Patient assigned successfully');
            loadAssignments();
        } else {
            const error = await response.json();
            alert(error.detail || 'Error assigning patient');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error assigning patient');
    }
});

async function removeAssignment(assignmentId) {
    if (confirm('Are you sure you want to remove this assignment?')) {
        try {
            const response = await fetch(`/api/admin/assignments/${assignmentId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                loadAssignments();
            } else {
                const error = await response.json();
                alert(error.detail || 'Error removing assignment');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error removing assignment');
        }
    }
}

// Helper function to handle API responses
async function handleResponse(response, resourceName) {
    if (!response.ok) {
        const errorText = await response.text();
        let errorMessage;
        try {
            const errorJson = JSON.parse(errorText);
            errorMessage = errorJson.detail;
        } catch {
            errorMessage = errorText;
        }
        throw new Error(`Failed to fetch ${resourceName}: ${errorMessage}`);
    }
    return response.json();
} 