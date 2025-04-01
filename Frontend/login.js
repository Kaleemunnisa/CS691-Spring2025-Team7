document.addEventListener("DOMContentLoaded", function () {
    const loginButton = document.querySelector("button");
    if (loginButton) {
        loginButton.addEventListener("click", loginUser);
    }
});

function loginUser() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    const storedUsername = localStorage.getItem("username");
    const storedPassword = localStorage.getItem("password");

    if (!username || !password) {
        alert("Please enter both username and password.");
        return;
    }

    if (username === storedUsername && password === storedPassword) {
        alert("Login successful!");
        
        // Redirect after a short delay
        setTimeout(() => {
            window.location.href = "wepage.html"; 
        }, 500);
    } else {
        document.getElementById("error-msg").style.display = "block";
    }
}
