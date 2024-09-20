let register = document.querySelector("#get-started");
register.addEventListener("click", function () {
    window.location.href = "/register";
});

function toggleChatbot() {
    var chatbotContainer = document.getElementById('chatbotContainer');
    if (chatbotContainer.style.display === 'none' || chatbotContainer.style.display === '') {
        chatbotContainer.style.display = 'flex';
    } else {
        chatbotContainer.style.display = 'none';
    }
}

function sendMessage() {
    const inputField = document.getElementById("chatInput");
    const message = inputField.value.trim();

    if (message) {
        // Append user message to chatbot body
        appendMessage("You: " + message);
        
        // Clear the input field
        inputField.value = "";

        // Append loading message
        const loadingMessage = appendMessage("Бот: ...");

        // Fetch response from your chatbot API
        fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Остутствует подключение к Интернету");
            }
            return response.json();
        })
        .then(data => {
            // Replace loading message with actual bot response
            loadingMessage.textContent = "Бот: " + data.reply;
        })
        .catch(error => {
            console.error("Ошибка:", error);
            loadingMessage.textContent = "Бот: Извините, попробуйте позже.";
        });
    }
}

function appendMessage(text) {
    const chatbotBody = document.getElementById("chatbotBody");
    const messageElement = document.createElement("div");
    messageElement.textContent = text;
    chatbotBody.appendChild(messageElement);
    chatbotBody.scrollTop = chatbotBody.scrollHeight; // Scroll to the bottom
    return messageElement; // Return the message element for later reference
}
