// allows menu button to show task dropdown on click
function toggleMenu(event, button) {
    event.stopPropagation(); // stops the click from propagating up to window.onclick, which would immediately close the dropdown I'm trying to open
    const dropdown = button.nextElementSibling;
    
    const isHidden = window.getComputedStyle(dropdown).display === 'none';

    document.querySelectorAll('.dropdown-content').forEach(d => d.style.display = 'none'); // closes other dropdowns

    dropdown.style.display = isHidden ? 'block' : 'none';
}

// this runs on every click anywhere on the page
window.onclick = function(event) {
    const taskModal = document.getElementById('task-modal');
    const subjectModal = document.getElementById('subject-modal');

    // closes modal if user clicks off of it
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

// store modal and button elements in variables so I can reuse them
const taskModal = document.getElementById('task-modal');
const openTaskBtn = document.getElementById('open-task-modal-btn');
const subjectModal = document.getElementById('subject-modal');
const openSubjectBtn = document.getElementById('open-subject-modal-btn');

// if the buttons exist on this page, attach click handlers to open the modals
if (openTaskBtn) openTaskBtn.onclick = () => { if (taskModal) taskModal.style.display = 'flex'; };
if (openSubjectBtn) openSubjectBtn.onclick = () => { if (subjectModal) subjectModal.style.display = 'flex'; };

// some pages have multiple buttons with the same id so this catches all of them since getElementById only catches the first
document.querySelectorAll('[id="open-task-modal-btn"]').forEach(btn => {
    btn.onclick = () => { if (taskModal) taskModal.style.display = 'flex'; };
});
document.querySelectorAll('[id="open-subject-modal-btn"]').forEach(btn => {
    btn.onclick = () => { if (subjectModal) subjectModal.style.display = 'flex'; };
});

// edit task button
function prepareEditModal(element) {
    // reads the task data stored in data - attributes on the edit button
    const id = element.getAttribute('data-id');
    const name = element.getAttribute('data-name');
    const date = element.getAttribute('data-date');
    const subject = element.getAttribute('data-subject');
    const status = element.getAttribute('data-status');

    // pre-fills the modal form with the existing task data
    document.getElementById('task-name-input').value = name;
    document.getElementById('due-date-input').value = date;
    document.getElementById('subject-id-select').value = subject;
    document.getElementById('status-select').value = status;

    // changes modal title
    document.getElementById('modal-title').innerText = "Edit Task";
    document.getElementById('save-btn').innerText = "Update Task";

    // changes the form action so it submits to the edit route instead of the add route
    document.getElementById('task-form').action = '/edit-task/' + id;

    // changes button text
    const saveBtn = document.querySelector('.save-btn');
    if (saveBtn) saveBtn.innerText = "Update Task";

    document.getElementById('task-modal').style.display = 'flex';
}

// runs when any close modal button is clicked
document.querySelectorAll('.close-modal').forEach(btn => {
    btn.onclick = () => {
        if (taskModal) {
            taskModal.style.display = 'none'; // hides the task modal
            const form = document.getElementById('task-form');
            if (form) {
                form.reset(); // clears all the form inputs
                form.action = '/'; // resets the form action back to the add route
            }
            const modalTitle = document.getElementById('modal-title');
            const saveBtn = document.querySelector('.save-btn');
            if (modalTitle) modalTitle.innerText = "New Task"; // resets the title
            if (saveBtn) saveBtn.innerText = "Save Task"; // resets the button text
        }
        if (subjectModal) subjectModal.style.display = 'none'; // hides subject modal
    }
});

// for when the user wants to cancel an edit 
function resetForm() {
    const form = document.getElementById('task-form');
    form.reset(); // clears inputs
    form.action = '/'; // resets to add route

    document.getElementById('modal-title').innerText = "Add New Task";
    
    const saveBtn = document.querySelector('.save-btn');
    if (saveBtn) saveBtn.innerText = "Save Task";
    
    document.getElementById('task-modal').style.display = 'flex'; // reopens the modal 
}

// highlight the active nav link
const navLinks = document.querySelectorAll('.navbar li a');

navLinks.forEach(link => {
    if (link.getAttribute('href') === window.location.pathname) {
        link.classList.add('active'); // if the link's href matches the URl path, add the active class
    }
});

// changes date warning text
const dueDateInput = document.getElementById('due-date-input');
if (dueDateInput) {
    dueDateInput.addEventListener('input', function() {
        // changes message if user inputted date it too far into the future
        if (this.validity.rangeOverflow) {
            this.setCustomValidity('Please enter a date before 31/12/2050');
        // changes message if user inputted date it too far in the past
        } else if (this.validity.rangeUnderflow) {
            this.setCustomValidity('Please enter a date from 01/01/2026 or later');
        // resets warning message
        } else {
            this.setCustomValidity('');
        }
    });
}

// edit subject modal
function prepareEditSubjectModal(element) {
    const id = element.getAttribute('data-id'); 
    const name = element.getAttribute('data-name');
    const color = element.getAttribute('data-color');

    document.getElementById('edit-subject-name').value = name;
    document.getElementById('edit-subject-color').value = color;
    document.getElementById('edit-subject-form').action = '/edit-subject/' + id;

    document.getElementById('edit-subject-modal').style.display = 'flex';
}