import { showError, clearError } from './helpers.js';

async function send_message(e) {
    e.preventDefault();

    const errorEl = document.querySelector('.error');
    clearError(errorEl);

    const form = e.target;
    const formData = new FormData(form);

    const userInput = formData.get('user_input');

    if (!userInput) {
        return;
    }

    // Clear user input
    form.reset();

    // Update UI with user message
    const chat = document.querySelector('.messages-area');
    const time = new Date().toLocaleTimeString();
    chat.innerHTML += `
        <div class="message user">
            <div class="message-timestamp">${time}</div>
            <div class="message user"><p class="message-content">${userInput}</p></div>
        </div>
    `;

    const response = await fetch('/api/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput }),
    });

    const data = await response.json();

    if (!response.ok) {
        showError(data.error || 'Something went wrong', errorEl);
    }

    // Update UI with assistant message
    const formattedTime = new Date(
        data.assistant_message.created_at,
    ).toLocaleTimeString();

    chat.innerHTML += `
        <div class="message assistant">
            <div class="message-timestamp">${formattedTime}</div>
            <div class="message assistant"><p class="message-content">${data.assistant_message.message}</p></div>
        </div>
    `;
}

function init() {
    const form = document.querySelector('.input-container');
    form.addEventListener('submit', send_message);
}

document.addEventListener('DOMContentLoaded', init);
