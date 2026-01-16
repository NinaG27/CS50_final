async function add_note(e) {
    e.preventDefault()



}

function addEventListeners() {
    document.addEventListener("submit", add_note)

}

function init() {
    addEventListeners()

}

document.addEventListener("DOMContentLoaded", init)