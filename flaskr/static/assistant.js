async function registar(e) {
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

    const chat = document.querySelector("#chat");
    chat.innerHTML += `<div class="msg user"><strong>You:</strong>${user_input}</div>`;
    chat.innerHTML += `<div class="msg assistant"><strong>Assistant:</strong>${data.reply}</div>`;

    // TODO Clear inputs
    console.log(response)

}

function addEventListeners() {
    document.addEventListener("submit", registar)

}

function init() {
    addEventListeners()

}

document.addEventListener("DOMContentLoaded", init)