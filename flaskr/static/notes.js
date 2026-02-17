// Render all notes to the grid
async function renderNotes() {
    const notesGrid = document.getElementById('notes-grid');
    const notesEmpty = document.getElementById('notes-empty');

    // Fetch all notes for the user
    const response = await fetch('/api/get_notes');

    if (!response.ok) {
        return 'Something went wrong';
    }

    const notes = await response.json();

    if (notes.length === 0) {
        notesGrid.style.display = 'none';
        notesEmpty.style.display = 'block';
        return;
    }

    notesGrid.style.display = 'grid';
    notesEmpty.style.display = 'none';

    notesGrid.innerHTML = notes
        .map(
            note => `
        <div class="note-card" data-id="${note['id']}">
          <div class="note-header">
            <div class="note-date">${note['created_at']}</div>
            <button class="note-delete">Edit</button>
          </div>
          <div class="note-content">${note['note']}</div>
        </div>
    `,
        )
        .join('');

    addEventListeners();
}

// Add a new note
async function addNote() {
    const noteInput = document.getElementById('note-input');
    const note = noteInput.value.trim();

    if (!note) {
        return;
    }

    try {
        response = await fetch('/api/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ note }),
        });

        if (!response.ok) {
            console.log('somthing went wrong with adding of the note');
        }
        // Clear input
        noteInput.value = '';
        noteInput.focus();
        // Handle UI update - rerender all notes
        renderNotes();
    } catch {
        print('TODO');
    }
}

// Delete a note
async function redirect(el) {
    id = el.dataset.id;

    window.location.replace(`/note/${id}`);
}

function addEventListeners() {
    const addNoteBtn = document.querySelector('#add-note-button');
    const cardDivs = document.querySelectorAll('.note-card');

    if (addNoteBtn) addNoteBtn.addEventListener('click', addNote);

    // Event delegation
    if (cardDivs) {
        cardDivs.forEach(card =>
            card.addEventListener('click', function (ev) {
                if (ev.target.tagName === 'BUTTON') {
                    redirect(this);
                }
            }),
        );
    }
}

function init() {
    renderNotes();
}

document.addEventListener('DOMContentLoaded', init);
