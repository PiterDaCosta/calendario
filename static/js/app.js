// Task Calendar - Main JavaScript

// Global refresh callback
window.refreshCurrentView = null;

// ============ Utility Functions ============

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(date) {
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
    });
}

function isSameDay(date1, date2) {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
}

// ============ Modal Functions ============

function closeModal() {
    document.getElementById('taskModal').classList.remove('active');
}

function openEditTaskModal(taskId) {
    fetch(`/api/tasks/${taskId}`)
        .then(response => response.json())
        .then(task => {
            document.getElementById('modalTitle').textContent = 'Edit Task';
            document.getElementById('taskId').value = task.id;
            document.getElementById('taskTitle').value = task.title;
            document.getElementById('taskDescription').value = task.description || '';
            document.getElementById('taskDate').value = task.due_date;
            document.getElementById('taskTime').value = task.due_time ? task.due_time.slice(0, 5) : '';
            document.getElementById('taskPriority').value = task.priority;
            document.getElementById('taskModal').classList.add('active');
        })
        .catch(error => console.error('Error loading task:', error));
}

// ============ API Functions ============

function saveTask(event) {
    event.preventDefault();
    
    const taskId = document.getElementById('taskId').value;
    const data = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        due_date: document.getElementById('taskDate').value,
        due_time: document.getElementById('taskTime').value || null,
        priority: parseInt(document.getElementById('taskPriority').value)
    };
    
    const url = taskId ? `/api/tasks/${taskId}` : '/api/tasks';
    const method = taskId ? 'PUT' : 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(() => {
        closeModal();
        // Reload the current view using global refresh callback
        if (window.refreshCurrentView) {
            window.refreshCurrentView();
        }
    })
    .catch(error => {
        console.error('Error saving task:', error);
        alert('Error saving task. Please try again.');
    });
}

function toggleTask(taskId) {
    fetch(`/api/tasks/${taskId}/toggle`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(() => {
        if (window.refreshCurrentView) {
            window.refreshCurrentView();
        }
    })
    .catch(error => console.error('Error toggling task:', error));
}

function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    fetch(`/api/tasks/${taskId}`, {
        method: 'DELETE'
    })
    .then(() => {
        if (window.refreshCurrentView) {
            window.refreshCurrentView();
        }
    })
    .catch(error => console.error('Error deleting task:', error));
}

// ============ Keyboard Shortcuts ============

document.addEventListener('keydown', (event) => {
    // Close modal on Escape
    if (event.key === 'Escape') {
        const taskModal = document.getElementById('taskModal');
        const templateModal = document.getElementById('templateModal');
        
        if (taskModal && taskModal.classList.contains('active')) {
            closeModal();
        }
        if (templateModal && templateModal.classList.contains('active')) {
            closeTemplateModal();
        }
    }
    
    // Quick add task on 'n' key (when not in input)
    if (event.key === 'n' && !event.target.matches('input, textarea')) {
        event.preventDefault();
        if (typeof openAddTaskModal === 'function') {
            openAddTaskModal();
        }
    }
});

// ============ Touch/Swipe Support for Mobile ============

let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
}, false);

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}, false);

function handleSwipe() {
    const swipeThreshold = 100;
    const diff = touchEndX - touchStartX;
    
    if (Math.abs(diff) < swipeThreshold) return;
    
    if (diff > 0) {
        // Swiped right - go to previous week/month
        if (typeof navigateWeek === 'function') {
            navigateWeek(-1);
        } else if (typeof navigateMonth === 'function') {
            navigateMonth(-1);
        }
    } else {
        // Swiped left - go to next week/month
        if (typeof navigateWeek === 'function') {
            navigateWeek(1);
        } else if (typeof navigateMonth === 'function') {
            navigateMonth(1);
        }
    }
}

// ============ Service Worker Registration (for PWA) ============

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('ServiceWorker registered:', registration.scope);
            })
            .catch(error => {
                console.log('ServiceWorker registration failed:', error);
            });
    });
}
