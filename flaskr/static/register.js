import { showError, clearError } from './helpers.js';

async function register(e) {
    e.preventDefault();

    const errorEl = document.querySelector('.error');
    clearError(errorEl);

    const form = e.target;
    const formData = new FormData(form);

    const email = formData.get('email').toLowerCase();
    const password = formData.get('password');
    const password_confirm = formData.get('confirm');

    if (!email || !password || !password_confirm) {
        showError('All fields are required', errorEl);
        return;
    }

    if (password !== password_confirm) {
        showError('Password mismatch', errorEl);
        return;
    }

    const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, password_confirm }),
    });

    const data = await response.json();

    if (!response.ok) {
        showError(data.error || 'Something went wrong', errorEl);
        return;
    }

    window.location.replace('/login');
}

function addEventListeners() {
    document.addEventListener('submit', register);
}

function init() {
    addEventListeners();
}

document.addEventListener('DOMContentLoaded', init);
