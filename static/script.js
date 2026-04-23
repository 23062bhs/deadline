//allows menu button to show task dropdown on click
function toggleMenu(event, button) {
    event.stopPropagation();
    
    document.querySelectorAll('.dropdown-content').forEach(menu => {
        if (menu !== button.nextElementSibling) {
            menu.classList.remove('show');
        }
    });

    button.nextElementSibling.classList.toggle('show');
    
    window.onclick = function(event) {
    if (!event.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown-content').forEach(menu => {
            menu.classList.remove('show');
        });
    }
}
}

window.onclick = function(event) {
    if (!event.target.matches('.menu-btn') && !event.target.matches('.fa-ellipsis-vertical')) {
        document.querySelectorAll('.dropdown-content').forEach(menu => {
            menu.classList.remove('show');
        });
    }
}

//allows task and subject modal to show on click, close modal button to close modal on click and closes modal when clicking outside of it
const taskModal = document.getElementById('task-modal');
const openTaskBtn = document.getElementById('open-task-modal-btn');
const subjectModal = document.getElementById('subject-modal');
const openSubjectBtn = document.getElementById('open-subject-modal-btn');

if (openTaskBtn && openSubjectBtn) {
    openTaskBtn.onclick = () => taskModal.style.display = 'flex';
    openSubjectBtn.onclick = () => subjectModal.style.display = 'flex';
}

document.querySelectorAll('.close-modal').forEach(btn => {
    btn.onclick = () => {
        taskModal.style.display = 'none';
        subjectModal.style.display = 'none';
    }
});

window.onclick = (event) => {
    if (event.target == taskModal) taskModal.style.display = 'none';
    if (event.target == subjectModal) subjectModal.style.display = 'none';
}
