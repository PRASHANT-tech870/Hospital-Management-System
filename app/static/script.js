const API_BASE_URL = "/auth/login"; // Updated login endpoint

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const role = document.getElementById("role").value;

  const credentials = {
    username: username,
    password: password,
    role: role,
  };

  console.log('Login attempt:', credentials);

  try {
    const response = await fetch(API_BASE_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    });

    console.log('Login response status:', response.status);
    console.log('Login response headers:', response.headers);

    if (response.ok) {
      const data = await response.json();
      console.log('Login successful - data:', data);
      
      // Ensure all required data is present
      const userData = {
        id: data.id,
        username: data.username,
        role: data.role,
        message: data.message
      };
      
      // Store user data in localStorage
      localStorage.setItem('user', JSON.stringify(userData));
      console.log('User data stored in localStorage:', userData);
      
      // Redirect based on role
      const dashboardUrl = `/${userData.role.toLowerCase()}-dashboard`;
      console.log('Redirecting to:', dashboardUrl);
      window.location.href = dashboardUrl;
    } else {
      const error = await response.json();
      console.error('Login failed:', error);
      document.getElementById("error-message").textContent = error.detail || "Login failed";
      document.getElementById("error-message").style.display = "block";
    }
  } catch (error) {
    console.error("Error during login:", error);
    document.getElementById("error-message").textContent = "An error occurred. Please try again.";
    document.getElementById("error-message").style.display = "block";
  }
});
