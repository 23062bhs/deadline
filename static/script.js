//allows menu button to show task dropdown on click
function toggleMenu(event, button) {
    event.stopPropagation();
    const dropdown = button.nextElementSibling;
    
    const isHidden = window.getComputedStyle(dropdown).display === 'none';

    document.querySelectorAll('.dropdown-content').forEach(d => d.style.display = 'none');

    dropdown.style.display = isHidden ? 'block' : 'none';
}

window.onclick = function(event) {
    const taskModal = document.getElementById('task-modal');
    const subjectModal = document.getElementById('subject-modal');

    if (event.target == taskModal) {
        const closeBtn = document.querySelector('.close-modal-btn');
        if (closeBtn) closeBtn.click();
    }
    
    if (event.target == subjectModal) subjectModal.style.display = 'none';

    if (!event.target.matches('.menu-btn') && !event.target.matches('.fa-ellipsis-vertical')) {
        document.querySelectorAll('.dropdown-content').forEach(menu => {
            menu.style.display = 'none';
        });
    }
}

//allows modals to show on click, close modal button to close modal on click and closes modal when clicking outside of it
const taskModal = document.getElementById('task-modal');
const openTaskBtn = document.getElementById('open-task-modal-btn');
const subjectModal = document.getElementById('subject-modal');
const openSubjectBtn = document.getElementById('open-subject-modal-btn');

if (openTaskBtn) openTaskBtn.onclick = () => { if (taskModal) taskModal.style.display = 'flex'; };
if (openSubjectBtn) openSubjectBtn.onclick = () => { if (subjectModal) subjectModal.style.display = 'flex'; };

document.querySelectorAll('[id="open-task-modal-btn"]').forEach(btn => {
    btn.onclick = () => { if (taskModal) taskModal.style.display = 'flex'; };
});
document.querySelectorAll('[id="open-subject-modal-btn"]').forEach(btn => {
    btn.onclick = () => { if (subjectModal) subjectModal.style.display = 'flex'; };
});

//edit task button
function prepareEditModal(element) {
    const id = element.getAttribute('data-id');
    const name = element.getAttribute('data-name');
    const date = element.getAttribute('data-date');
    const subject = element.getAttribute('data-subject');
    const status = element.getAttribute('data-status');

    document.getElementById('task-name-input').value = name;
    document.getElementById('due-date-input').value = date;
    document.getElementById('subject-id-select').value = subject;
    document.getElementById('status-select').value = status;
    document.getElementById('modal-title').innerText = "Edit Task";
    document.getElementById('save-btn').innerText = "Update Task";
    document.getElementById('task-form').action = '/edit-task/' + id;

    const saveBtn = document.querySelector('.save-btn');
    if (saveBtn) saveBtn.innerText = "Update Task";

    document.getElementById('task-modal').style.display = 'flex';
}

//make sure close button still works
document.querySelectorAll('.close-modal').forEach(btn => {
    btn.onclick = () => {
        if (taskModal) {
            taskModal.style.display = 'none';
            const form = document.getElementById('task-form');
            if (form) {
                form.reset();
                form.action = '/';
            }
            const modalTitle = document.getElementById('modal-title');
            const saveBtn = document.querySelector('.save-btn');
            if (modalTitle) modalTitle.innerText = "New Task";
            if (saveBtn) saveBtn.innerText = "Save Task";
        }
        if (subjectModal) subjectModal.style.display = 'none';
    }
});

//resets the edit form
function resetForm() {
    const form = document.getElementById('task-form');
    form.reset();
    form.action = '/';

    document.getElementById('modal-title').innerText = "Add New Task";
    
    const saveBtn = document.querySelector('.save-btn');
    if (saveBtn) saveBtn.innerText = "Save Task";
    
    document.getElementById('task-modal').style.display = 'flex';
}

//highlight the active nav link
const navLinks = document.querySelectorAll('.navbar li a');

navLinks.forEach(link => {
    if (link.getAttribute('href') === window.location.pathname) {
        link.classList.add('active');
    }
});