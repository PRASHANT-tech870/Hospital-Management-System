document.addEventListener('DOMContentLoaded', function() {
    const roleSelect = document.getElementById('role');
    const patientFields = document.getElementById('patient-fields');
    const doctorFields = document.getElementById('doctor-fields');
    const staffFields = document.getElementById('staff-fields');
    const registerForm = document.getElementById('register-form');
    const errorMessage = document.getElementById('error-message');

    // Function to disable/enable form fields based on visibility
    function toggleFieldsRequirement(container, required) {
        const inputs = container.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.required = required;
        });
    }

    // Handle role selection
    roleSelect.addEventListener('change', function() {
        // Hide all role-specific fields and disable requirements
        [patientFields, doctorFields, staffFields].forEach(fields => {
            fields.style.display = 'none';
            toggleFieldsRequirement(fields, false);
        });

        // Show selected role fields and enable requirements
        const selectedRole = this.value;
        if (selectedRole === 'PATIENT') {
            patientFields.style.display = 'block';
            toggleFieldsRequirement(patientFields, true);
        } else if (selectedRole === 'DOCTOR') {
            doctorFields.style.display = 'block';
            toggleFieldsRequirement(doctorFields, true);
            loadDepartments();
        } else if (selectedRole === 'STAFF') {
            staffFields.style.display = 'block';
            toggleFieldsRequirement(staffFields, true);
        }
    });

    // Handle form submission
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get base fields
        const role = roleSelect.value;
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        // Validate base fields
        if (!username || !email || !password || !role) {
            alert('Please fill in all required fields');
            return;
        }

        const baseData = { username, email, password, role };
        let additionalData = {};

        // Get role-specific fields
        if (role === 'PATIENT') {
            const emergencyContact = document.getElementById('emergency-contact').value;
            if (!emergencyContact) {
                alert('Please provide an emergency contact');
                return;
            }
            additionalData = {
                medical_history: document.getElementById('medical-history').value || '',
                emergency_contact: emergencyContact
            };
        } else if (role === 'DOCTOR') {
            const specialization = document.getElementById('specialization').value;
            const consultationFee = document.getElementById('consultation-fee').value;
            const departmentId = document.getElementById('department-id').value;
            
            if (!specialization || !consultationFee || !departmentId) {
                alert('Please fill in all doctor details');
                return;
            }
            additionalData = {
                specialization,
                consultation_fee: parseFloat(consultationFee),
                department_id: parseInt(departmentId)
            };
        } else if (role === 'STAFF') {
            const name = document.getElementById('staff-name').value;
            if (!name) {
                alert('Please enter staff name');
                return;
            }
            additionalData = {
                name: name
            };
        }

        const data = { ...baseData, ...additionalData };

        try {
            const response = await fetch(`/auth/register/${role.toLowerCase()}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                alert('Registration successful! Please login.');
                window.location.href = '/';
            } else {
                const error = await response.json();
                console.error('Registration error:', error);
                errorMessage.textContent = error.detail || 'Registration failed';
                errorMessage.style.display = 'block';
            }
        } catch (error) {
            console.error('Error:', error);
            errorMessage.textContent = 'An error occurred. Please try again.';
            errorMessage.style.display = 'block';
        }
    });

    // Add this function
    async function loadDepartments() {
        try {
            const response = await fetch('/api/admin/departments');
            const departments = await response.json();
            
            const departmentSelect = document.getElementById('department-id');
            departmentSelect.innerHTML = '<option value="">-- Select Department --</option>' +
                departments.map(dept => `
                    <option value="${dept.id}">${dept.name}</option>
                `).join('');
        } catch (error) {
            console.error('Error loading departments:', error);
        }
    }
}); 