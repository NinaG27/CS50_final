async function updateNote(el) {
    id = el.dataset.id;

    const noteInput = document.querySelector('.note-edit');
    const note = noteInput.value.trim();

    //Disable edits while request processing
    noteInput.setAttribute('disabled', 'disabled');
    const btns = document.querySelectorAll('.mybtn');

    btns.forEach(btn => {
        btn.setAttribute('disabled', 'disabled');
        btn.style.color = 'gray';
    });

    if (!note) {
        return;
    }

    const response = await fetch(`/api/notes/${id}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ note }),
    });

    const data = await response.json();

    if (!response.ok) {
        alert(
            `Could not update note. Error: ${data.error || 'Something went wrong'}`,
        );
        return;
    }

    // Simulate longer request
    setTimeout(function () {
        const toast = document.getElementById('save-toast');

        if (toast) {
            const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toast);
            toastBootstrap.show();
        }

        //Enable edits after request processed
        noteInput.removeAttribute('disabled', 'disabled');

        btns.forEach(btn => {
            btn.removeAttribute('disabled', 'disabled');
            btn.style.color = 'white';
        });
    }, 2000);
}

function redirect(url) {
    // Simulate an HTTP redirect
    return window.location.replace(url);
}

// Delete a note
async function deleteNote(el) {
    confirm = confirm('Are you sure?');

    if (!confirm) return;

    const id = el.dataset.id;

    const response = await fetch(`/api/notes/${id}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    const data = await response.json();

    if (!response.ok) {
        alert(
            `Could not delete note. Error: ${data.error || 'Something went wrong'}`,
        );
        return;
    }
    // Handle UI update
    redirect('/notes');
}

function init() {
    const btnContainer = document.querySelector('.note-buttons');

    btnContainer.addEventListener('click', function (ev) {
        if (ev.target.tagName === 'BUTTON') {
            let classes = ev.target.classList.value;

            if (classes.includes('--back')) redirect('/notes');
            if (classes.includes('--delete')) deleteNote(this);
            if (classes.includes('--save')) updateNote(this);
        }
    });
}

document.addEventListener('DOMContentLoaded', init);
