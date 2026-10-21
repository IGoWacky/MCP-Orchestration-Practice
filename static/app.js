document.addEventListener('DOMContentLoaded', fetchTasks);

async function fetchTasks() {
    const response = await fetch('/api/tasks');
    const tasks = await response.json();
    const taskList = document.getElementById('task-list');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        const priority = task.priority || 'Medium';
        const priorityClass = priority.toLowerCase();
        const li = document.createElement('li');
        li.innerHTML = `
            <div class="task-details">
                <span>${task.title}</span>
                <span class="priority priority-${priorityClass}">
                    ${priority}
                </span>
            </div>
            <button class="delete-btn" onclick="deleteTask(${task.id})">
                Delete
            </button>
        `;
        taskList.appendChild(li);
    });
}

async function addTask() {
    const titleInput = document.getElementById('task-title');
    const priorityInput = document.getElementById('task-priority');
    const title = titleInput.value.trim();
    const priority = priorityInput ? priorityInput.value : '';

    if (!title) return;

    await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, priority })
    });

    titleInput.value = '';
    if (priorityInput) priorityInput.value = 'Medium';
    fetchTasks();
}

async function deleteTask(id) {
    await fetch(`/api/tasks/${id}`, {
        method: 'DELETE'
    });
    fetchTasks();
}
