// Global Variables
let current_username = "";
let current_user_id = null;
let tasks = [];

// DOM Elements (تعریف بعد از بارگذاری صفحه)
let set_user_btn, username_input, username_error, tasks_section;
let active_username, lock_message, current_user_info;
let create_task_btn, task_title_input, task_description_input;
let task_due_date_input, task_list;

// API Base URL
const API_BASE_URL = "http://127.0.0.1:8000/api";

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
    console.log("=== To-Do List App Initialized ===");
    
    // Initialize DOM elements
    set_user_btn = document.getElementById("set_user_btn");
    username_input = document.getElementById("username_input");
    username_error = document.getElementById("username_error");
    tasks_section = document.getElementById("tasks_section");
    active_username = document.getElementById("active_username");
    lock_message = document.getElementById("lock_message");
    current_user_info = document.getElementById("current_user_info");
    
    create_task_btn = document.getElementById("create_task_btn");
    task_title_input = document.getElementById("task_title_input");
    task_description_input = document.getElementById("task_description_input");
    task_due_date_input = document.getElementById("task_due_date_input");
    task_list = document.getElementById("task_list");
    
    // Load current user from localStorage
    const savedUser = Utils.getFromLocalStorage('current_user');
    if (savedUser) {
        current_username = savedUser.username;
        current_user_id = savedUser.user_id;
        console.log('✅ Loaded user from localStorage:', { username: current_username, id: current_user_id });
        unlockInterface();
        loadTasks();
    } else {
        console.log('ℹ️ No saved user found in localStorage');
    }
});

// Set User Handler
set_user_btn.addEventListener("click", async () => {
    const username = username_input.value.trim();
    
    // Validate username
    const validation = FormValidator.validateUsername(username);
    if (!validation.valid) {
        FormValidator.showError('username_error', validation.errors);
        Utils.addAnimation(username_input, 'shake');
        return;
    }
    
    FormValidator.clearError('username_error');
    
    try {
        // Show loading state
        Utils.showButtonLoading(set_user_btn);
        
        const response = await fetch(`${API_BASE_URL}/set-user/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const userId = data.data.user.id;
            current_username = username;
            current_user_id = userId;
            
            console.log('✅ User set successfully:', { username: current_username, id: current_user_id });
            
            // Save to localStorage
            Utils.saveToLocalStorage('current_user', {
                username: current_username,
                user_id: current_user_id
            });
            
            unlockInterface();
            await loadTasks(); // await اضافه شد
            
            Utils.showSuccess(data.message || 'کاربر با موفقیت انتخاب شد');
            username_input.value = '';
        } else {
            const errorMsg = data.errors?.username || data.message || 'خطا در انتخاب کاربر';
            Utils.showError(errorMsg);
            Utils.addAnimation(username_input, 'shake');
        }
    } catch (error) {
        console.error('❌ Error setting user:', error);
        Utils.showError('خطا در ارتباط با سرور');
    } finally {
        Utils.hideButtonLoading(set_user_btn, 'انتخاب کاربر');
    }
});

// Unlock Interface
function unlockInterface() {
    tasks_section.classList.remove("locked");
    lock_message.style.display = "none";
    active_username.innerText = `لیست کارهای ${current_username}`;
    
    current_user_info.innerHTML = `
        <strong>کاربر فعلی:</strong> ${current_username}<br>
        <strong>ID:</strong> ${current_user_id}
    `;
    current_user_info.classList.add('show');
}

// Load Tasks from API - با Cache-Buster
async function loadTasks() {
    if (!current_user_id) {
        console.warn('⚠️ No user ID available, cannot load tasks');
        return;
    }
    
    try {
        // افزودن timestamp برای جلوگیری از کش مرورگر
        const timestamp = Date.now();
        const url = `${API_BASE_URL}/tasks/?user_id=${current_user_id}&_=${timestamp}`;
        
        console.log(`📡 Fetching tasks from: ${url}`);
        
        const response = await fetch(url, {
            headers: { 'Cache-Control': 'no-cache' }
        });
        
        const data = await response.json();
        console.log('📥 Tasks API response:', data);
        
        if (data.success) {
            tasks = data.data.tasks || [];
            console.log(`✅ Loaded ${tasks.length} tasks for user ${current_user_id}:`, tasks);
            renderTasks();
        } else {
            console.error('❌ API returned error:', data.message);
            Utils.showError(data.message || 'خطا در دریافت تسک‌ها');
        }
    } catch (error) {
        console.error('❌ Error loading tasks:', error);
        Utils.showError('خطا در ارتباط با سرور');
    }
}

// Render Tasks
function renderTasks() {
    console.log(`🎨 Rendering ${tasks.length} tasks`);
    
    if (!task_list) {
        console.error('❌ task_list element not found!');
        return;
    }
    
    task_list.innerHTML = "";
    
    if (tasks.length === 0) {
        task_list.innerHTML = '<li style="text-align:center;padding:20px;color:#9ca3af;font-size:16px;">📭 هیچ تسکی وجود ندارد</li>';
        console.log('ℹ️ No tasks to display');
        return;
    }
    
    tasks.forEach((task, index) => {
        const li = document.createElement("li");
        li.className = "task_card" + (task.completed ? " completed" : "");
        li.dataset.taskId = task.id;
        
        // Format due date
        const dueDateDisplay = task.due_date ? Utils.formatDate(task.due_date) : '-';
        const isOverdue = task.due_date && Utils.isOverdue(task.due_date);
        
        li.innerHTML = `
            <input type="checkbox" ${task.completed ? "checked" : ""} data-id="${task.id}">
            <div class="task_content">
                <h3 class="task_title">${escapeHtml(task.title)}</h3>
                <p class="task_description">${task.description || ''}</p>
                <span class="task_due_date ${isOverdue ? 'overdue' : ''}">
                    ${dueDateDisplay}
                </span>
            </div>
            <div class="task_actions">
                <button class="update_task_btn" data-id="${task.id}">ویرایش</button>
                <button class="delete_task_btn" data-id="${task.id}">حذف</button>
            </div>
        `;
        
        task_list.appendChild(li);
    });
    
    console.log(`✅ Rendered ${tasks.length} tasks successfully`);
    addTaskEventListeners();
}

// Add Event Listeners to Tasks
function addTaskEventListeners() {
    // Checkbox toggle
    document.querySelectorAll('.task_card input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', async (e) => {
            const taskId = e.target.getAttribute('data-id');
            await toggleTaskComplete(taskId);
        });
    });
    
    // Delete button
    document.querySelectorAll('.delete_task_btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            const taskId = e.target.getAttribute('data-id');
            if (confirm('آیا مطمئن هستید؟')) {
                await deleteTask(taskId);
            }
        });
    });
    
    // Update button
    document.querySelectorAll('.update_task_btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            const taskId = e.target.getAttribute('data-id');
            await showUpdateTaskModal(taskId);
        });
    });
}

// Create Task
create_task_btn.addEventListener("click", async () => {
    const title = task_title_input.value.trim();
    const description = task_description_input.value.trim();
    const dueDate = task_due_date_input.value;
    
    // Validate form
    const validation = FormValidator.validateTaskForm(title, description, dueDate);
    if (!validation.valid) {
        Utils.showError(validation.errors.join('\n'));
        Utils.addAnimation(create_task_btn, 'shake');
        return;
    }
    
    if (!current_user_id) {
        Utils.showError('ابتدا باید کاربری انتخاب کنید');
        Utils.addAnimation(set_user_btn, 'shake');
        return;
    }
    
    try {
        Utils.showButtonLoading(create_task_btn);
        
        console.log(`📤 Creating task for user ${current_user_id}:`, { title, description, dueDate });
        
        const response = await fetch(`${API_BASE_URL}/tasks/create/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: current_user_id,
                title: title,
                description: description,
                due_date: dueDate || null
            })
        });
        
        const data = await response.json();
        console.log('📥 Create task response:', data);
        
        if (data.success) {
            // Clear form
            task_title_input.value = "";
            task_description_input.value = "";
            task_due_date_input.value = "";
            
            console.log('✅ Task created successfully, reloading tasks...');
            await loadTasks(); // await اضافه شد
            
            Utils.showSuccess(data.message || 'تسک با موفقیت ایجاد شد');
        } else {
            const errorMsg = data.errors?.title || data.errors?.description || data.message || 'خطا در ایجاد تسک';
            console.error('❌ Create task failed:', errorMsg);
            Utils.showError(errorMsg);
            Utils.addAnimation(create_task_btn, 'shake');
        }
    } catch (error) {
        console.error('❌ Error creating task:', error);
        Utils.showError('خطا در ارتباط با سرور');
    } finally {
        Utils.hideButtonLoading(create_task_btn, '+');
    }
});

// Toggle Task Complete
async function toggleTaskComplete(taskId) {
    try {
        console.log(`🔄 Toggling task ${taskId}`);
        
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/toggle-complete/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✅ Task status toggled, reloading tasks...');
            await loadTasks();
        } else {
            Utils.showError(data.message || 'خطا در تغییر وضعیت تسک');
        }
    } catch (error) {
        console.error('❌ Error toggling task:', error);
        Utils.showError('خطا در ارتباط با سرور');
    }
}

// Delete Task
async function deleteTask(taskId) {
    try {
        console.log(`🗑️ Deleting task ${taskId}`);
        
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/delete/`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✅ Task deleted, reloading tasks...');
            await loadTasks();
            Utils.showSuccess('تسک با موفقیت حذف شد');
        } else {
            Utils.showError(data.message || 'خطا در حذف تسک');
        }
    } catch (error) {
        console.error('❌ Error deleting task:', error);
        Utils.showError('خطا در ارتباط با سرور');
    }
}

// Show Update Task Modal
async function showUpdateTaskModal(taskId) {
    const task = tasks.find(t => t.id == taskId);
    if (!task) {
        Utils.showError('تسک یافت نشد');
        return;
    }
    
    const newTitle = prompt("ویرایش عنوان:", task.title);
    if (newTitle === null || newTitle.trim() === "") return;
    
    const newDescription = prompt("ویرایش توضیحات:", task.description || "");
    if (newDescription === null) return;
    
    const currentDueDate = task.due_date ? task.due_date.split('T')[0] : '';
    const newDueDate = prompt("ویرایش تاریخ ددلاین (YYYY-MM-DD):", currentDueDate);
    if (newDueDate === null) return;
    
    await updateTask(taskId, newTitle.trim(), newDescription.trim(), newDueDate.trim());
}

// Update Task
async function updateTask(taskId, title, description, dueDate) {
    try {
        console.log(`✏️ Updating task ${taskId}`);
        
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/update/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: title,
                description: description,
                due_date: dueDate || null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✅ Task updated, reloading tasks...');
            await loadTasks();
            Utils.showSuccess('تسک با موفقیت ویرایش شد');
        } else {
            Utils.showError(data.message || 'خطا در ویرایش تسک');
        }
    } catch (error) {
        console.error('❌ Error updating task:', error);
        Utils.showError('خطا در ارتباط با سرور');
    }
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Refresh tasks manually (Ctrl+R)
document.addEventListener('keydown', (e) => {
    if (e.key === 'r' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        console.log('🔄 Manual refresh triggered (Ctrl+R)');
        loadTasks();
    }
});

// Debug function
window.debugApp = () => {
    console.log('=== 🐞 App State Debug ===');
    console.log('Current Username:', current_username);
    console.log('Current User ID:', current_user_id);
    console.log('Tasks Array Length:', tasks.length);
    console.log('Tasks:', tasks);
    console.log('LocalStorage User:', Utils.getFromLocalStorage('current_user'));
    console.log('Task List Element:', task_list);
    console.log('=========================');
};

console.log('✅ App.js loaded successfully. Use debugApp() in console for diagnostics.');