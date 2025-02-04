console.log('Dashboard.js loaded');

// Function to get user data from localStorage
function getUserData() {
    const userData = localStorage.getItem('user');
    console.log('User data from localStorage:', userData);
    
    if (!userData) {
        console.error('No user data found');
        window.location.href = '/';
        return null;
    }
    
    try {
        const user = JSON.parse(userData);
        console.log('Parsed user data:', user);
        return user;
    } catch (error) {
        console.error('Error parsing user data:', error);
        localStorage.removeItem('user');
        window.location.href = '/';
        return null;
    }
}

function logout() {
    console.log('Logout clicked');
    localStorage.removeItem('user');
    window.location.href = '/';
}

// Check authentication and setup dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    const userData = getUserData();
    if (!userData) return;

    // Verify user is on the correct dashboard
    const currentPath = window.location.pathname;
    const expectedPath = `/${userData.role.toLowerCase()}-dashboard`;
    
    if (currentPath !== expectedPath) {
        console.error(`Wrong dashboard. Expected: ${expectedPath}, Current: ${currentPath}`);
        window.location.href = expectedPath;
        return;
    }

    // Update username in the dashboard
    const nameElement = document.getElementById(`${userData.role.toLowerCase()}-name`);
    if (nameElement) {
        nameElement.textContent = userData.username;
    }

    // Initialize dashboard-specific features
    initializeDashboard(userData);
});

// Initialize dashboard-specific features
function initializeDashboard(userData) {
    switch (userData.role) {
        case 'PATIENT':
            // Initialize patient-specific features
            initializePatientDashboard(userData);
            break;
        case 'DOCTOR':
            // Initialize doctor-specific features
            initializeDoctorDashboard(userData);
            break;
        case 'STAFF':
            // Initialize staff-specific features
            initializeStaffDashboard(userData);
            break;
    }
}

// Patient dashboard initialization
function initializePatientDashboard(userData) {
    console.log('Initializing patient dashboard for:', userData.username);
    // Add patient-specific initialization here
}

// Doctor dashboard initialization
function initializeDoctorDashboard(userData) {
    console.log('Initializing doctor dashboard for:', userData.username);
    // Add doctor-specific initialization here
}

