// chatbot/static/chatbot.js
document.addEventListener("DOMContentLoaded", function () {
    const chatContainer = document.getElementById("chat-container");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");

    // Function to add messages to chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender);
        messageDiv.innerText = text;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Function to send user query to the backend
    function sendMessage() {
        const userQuery = userInput.value.trim();
        if (userQuery === "") return; // Ignore empty messages

        // Add user message to chat
        addMessage(`🗣️ You: ${userQuery}`, "user");

        // Send query to the Flask backend
        fetch("/chatbot/query", {  // <-- Updated URL to point to your chatbot blueprint
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query: userQuery }),
        })
            .then(response => response.json())
            .then(data => {
                // Add chatbot response to chat
                addMessage(`🤖 Chatbot: ${data.response}`, "bot");
            })
            .catch(error => {
                console.error("Error:", error);
                addMessage("⚠️ Error: Unable to fetch response.", "bot");
            });

        // Clear input field
        userInput.value = "";
    }

    // Event listener for send button
    sendButton.addEventListener("click", sendMessage);

    // Send message when Enter key is pressed
    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
});
