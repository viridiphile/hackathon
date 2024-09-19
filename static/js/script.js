let register = document.querySelector("#get-started");
register.addEventListener("click", function () {
    window.location.href = "/register";
})

function toggleChatbot() {
    var chatbotContainer = document.getElementById('chatbotContainer');
    if (chatbotContainer.style.display === 'none' || chatbotContainer.style.display === '') {
        chatbotContainer.style.display = 'flex';
    } else {
        chatbotContainer.style.display = 'none';
    }
}

function sendMessage() {
    var input = document.getElementById('chatInput');
    var message = input.value.trim();
    if (message) {
        var chatbotBody = document.getElementById('chatbotBody');
        var newMessage = document.createElement('div');
        newMessage.textContent = 'You: ' + message;
        chatbotBody.appendChild(newMessage);
        chatbotBody.scrollTop = chatbotBody.scrollHeight;  // Scroll to the bottom
        input.value = '';  // Clear input field

        // Add your backend chat response logic here, e.g., AJAX request to Flask backend
    }
}