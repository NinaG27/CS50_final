async function registar(e) {
    e.preventDefault()
    let form = e.target
    let data = new FormData(form)

    let email = data.get("email")
    let password = data.get("password")
    let password_confirm = data.get("confirm")

    // TODO - add better validation 
    if (!email || !password || !password_confirm) {
        return alert("Please fill all fields.")
    }

    if (password !== password_confirm) {
        return alert("Passwords do not match.")
    }
    console.log({ email, password, password_confirm })

    // Send to api /registar
    const response = await fetch("/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password, password_confirm }
        )
    })

    if (!response.ok) {
        // handle user registration error 
    }

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