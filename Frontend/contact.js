document.getElementById("contactForm").addEventListener("submit", function(event) {
    event.preventDefault();

    // Simple validation
    var isValid = true;
    var inputs = document.querySelectorAll("#contactForm input[required], #contactForm textarea[required]");
    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = "red";
        } else {
            input.style.borderColor = "";
        }
    });

    if (isValid) {
        var responseMsg = document.getElementById("responseMsg");
        responseMsg.style.display = "block";
        setTimeout(() => {
            responseMsg.style.display = "none";
            document.getElementById("contactForm").reset();
        }, 2000);
    }
});
