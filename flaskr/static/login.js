function login(e) {
    e.preventDefault()
    let form = e.target
    let data = new FormData(form)
    let email = data.get("email")
    let password = data.get("password")

    // TODO - add better validation 
    if (!email || !password) {
        return alert("Please fill both fields.")
    }
    console.log(email, password)

    // Send to api /login
}

function addEventListeners() {
    document.addEventListener("submit", login)

}

function init() {
    addEventListeners()

}

document.addEventListener("DOMContentLoaded", init)