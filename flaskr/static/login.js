async function login(e) {
    e.preventDefault()
    let form = e.target
    let data = new FormData(form)
    let email = data.get("email")
    let password = data.get("password")

    // TODO - add better validation 
    if (!email || !password) {
        return alert("Please fill both fields.")
    }

    // Send to api /login
    response = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    })

    // TODO Clear inputs

    if (!response.ok) {
        console.log("something went wrong with user auth")
        // handle user registration error 
    }
    console.log("sucessfull login - should redirect")
    window.location.href = "/assistant"
}

function addEventListeners() {
    document.addEventListener("submit", login)

}

function init() {
    addEventListeners()

}

document.addEventListener("DOMContentLoaded", init)