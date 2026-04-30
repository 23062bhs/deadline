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
        document.querySelector('.close-modal-btn').click(); 
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
document.querySelector('.close-modal-btn').onclick = function() {
    const modal = document.getElementById('task-modal');
    const form = document.getElementById('task-form');
    
    // 1. Hide the modal
    modal.style.display = 'none';
    
    // 2. Clear all inputs (Task Name, Date, etc.)
    form.reset();
    
    // 3. Reset the form action and titles back to "New Task" defaults
    form.action = '/add-task';
    document.getElementById('modal-title').innerText = "New Task";
    document.querySelector('.save-btn').innerText = "Save Task";
}


//resets the edit form
function openAddModal() {
    document.getElementById('task-form').reset();
    document.getElementById('task-form').action = '/add-task';
    document.getElementById('modal-title').innerText = "Add New Task";
    
    const saveBtn = document.querySelector('.save-btn');
    if (saveBtn) saveBtn.innerText = "Save Task";
    
    document.getElementById('task-modal').style.display = 'flex';
}

