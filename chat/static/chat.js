const chatId = JSON.parse(document.getElementById('chat-id').textContent);
const url = 'ws://' + window.location.host + '/ws/chat/room/' + chatId + '/';
const chatSocket = new WebSocket(url);
chatSocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const chat = document.getElementById('chat');
    chat.innerHTML += '<div class="message">' + data.message + '</div>';
    chat.scrollTop = chat.scrollHeight;
};
chatSocket.onclose = function(event) {
    console.error('Chat socket closed unexpectedly');
};
const input = document.getElementById('chat-message-input');
const submitButton = document.getElementById('chat-message-submit');
input.addEventListener("keypress", function(event) {
    if (event.key == "Enter") {
        event.preventDefault();
        submitButton.click();
        input.focus();
    }
})
submitButton.addEventListener('click', function(event) {
    const message = input.value;
    if (message) {
        chatSocket.send(JSON.stringify({ 'message': message }));
        input.value = '';
        input.focus();
    }
});