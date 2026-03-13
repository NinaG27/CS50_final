import { showError, clearError } from './helpers.js';

async function login(e) {
    e.preventDefault();

    const errorEl = document.querySelector('.error');
    clearError(errorEl);

    let form = e.target;
    let formData = new FormData(form);

    let email = formData.get('email').toLowerCase();
    let password = formData.get('password');

    if (!email || !password) {
        showError('All fields are required', errorEl);
        return;
    }

    const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
        showError(data.error || 'Something went wrong', errorEl);
        return;
    }

    window.location.replace('/assistant');
}

function init() {
    const form = document.querySelector('.form-register');
    form.addEventListener('submit', login);
}

document.addEventListener('DOMContentLoaded', init);
