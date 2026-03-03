function showError(message, el) {
    if (!el) return;
    el.textContent = message;
    el.hidden = false;
}

function clearError(el) {
    if (!el) return;
    el.textContent = '';
    el.hidden = true;
}

export { showError, clearError };
