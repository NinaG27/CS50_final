// Toggle history item
function toggleHistory(el) {
    id = el.dataset.id
    const content = document.getElementById(`history-content-${id}`);
    const arrow = document.querySelectorAll(`.history-arrow-${id}`);
    console.log(arrow)

    if (content.classList.contains('expanded')) {
        content.classList.remove('expanded');
        arrow.textContent = '▼';
    } else {
        content.classList.add('expanded');
        arrow.textContent = '▲';
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document
        .querySelectorAll(".history-date")
        .forEach(item =>
            item.addEventListener("click", function () {
                toggleHistory(this)
            })
        )
})


