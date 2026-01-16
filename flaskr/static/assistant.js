async function send_message(e) {
    e.preventDefault()
    const form = e.target;
    const form_data = new FormData(form);

    const user_input = form_data.get("user_input");

    // TODO - add better validation 
    if (!user_input) {
        return alert("TODO check for empty input")
    };

    // Clear user input 
    form.reset();

    // Send to api /registar
    const response = await fetch("/api/send_message", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: user_input }
        )
    });

    if (!response.ok) {
        // handle user registration error 
    };

    const data = await response.json();

    const chat = document.querySelector(".messages-area");
    chat.innerHTML += `<div class="message user"><p class="message-content">${user_input}</p></div>`;
    chat.innerHTML += `<div class="message assistant"><p class="message-content">${data.reply}</p></div>`;

    // TODO Clear inputs
    console.log(response)

}

function addEventListeners() {
    document.addEventListener("submit", send_message)

}

function init() {
    addEventListeners()

}

document.addEventListener("DOMContentLoaded", init)