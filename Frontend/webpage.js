document.addEventListener("DOMContentLoaded", function () {
    // Chatbot Toggle Functionality
    const chatbotIcon = document.querySelector(".chatbot-icon");
    const chatbotPopup = document.querySelector(".chatbot-popup");

    if (chatbotIcon) {
        chatbotIcon.addEventListener("click", function () {
            chatbotPopup.style.display = chatbotPopup.style.display === "block" ? "none" : "block";
        });
    }

    // Logout Button Functionality
    const logoutButton = document.querySelector(".sidebar a[href='Lumina login.html'] button");

    if (logoutButton) {
        logoutButton.addEventListener("click", function (event) {
            event.preventDefault(); // Prevents default link behavior
            localStorage.clear(); // Clears all stored user data
            alert("You have been logged out.");
            window.location.href = "Lumina login.html"; // Redirect to login page
        });
    }
});
