document.getElementById('admin-login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch('/api/admin/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('admin', JSON.stringify({
                id: data.admin_id,
                username: formData.username
            }));
            window.location.href = '/admin-dashboard';
        } else {
            const error = await response.json();
            document.getElementById('error-message').textContent = error.detail;
            document.getElementById('error-message').style.display = 'block';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('error-message').textContent = 'An error occurred. Please try again.';
        document.getElementById('error-message').style.display = 'block';
    }
}); 