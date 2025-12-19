// Глобальные переменные для хранения токенов
let accessToken = localStorage.getItem('accessToken');
let refreshToken = localStorage.getItem('refreshToken');

// Проверка авторизации при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Страница загружена');

    // Проверяем, есть ли сохраненные токены
    if (accessToken) {
        console.log('Токен найден, показываем раздел задач');
        document.getElementById('auth-section').style.display = 'none';
        document.getElementById('todo-section').style.display = 'block';
        loadTasks();
    } else {
        console.log('Токен не найден, показываем раздел авторизации');
    }

    // Добавляем обработчики событий для форм
    setupEventListeners();
});

function setupEventListeners() {
    // Обработчик для формы входа на Enter
    document.getElementById('login-password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            login();
        }
    });

    // Обработчик для формы регистрации на Enter
    document.getElementById('register-password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            register();
        }
    });
}

// Функции аутентификации
async function login() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    if (!email || !password) {
        showNotification('Пожалуйста, заполните все поля', 'warning');
        return;
    }

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                'email': email,
                'password': password
            })
        });

        const data = await response.json();
        console.log('Ответ от сервера:', data);

        if (response.ok) {
            // Сохраняем токены в localStorage
            localStorage.setItem('accessToken', data.access_token);
            localStorage.setItem('refreshToken', data.refresh_token);
            accessToken = data.access_token;
            refreshToken = data.refresh_token;

            console.log('Авторизация успешна, переключаем интерфейс');
            document.getElementById('auth-section').style.display = 'none';
            document.getElementById('todo-section').style.display = 'block';
            loadTasks();
            showNotification('Добро пожаловать! Вы успешно вошли в систему.', 'success');
        } else {
            showNotification('Ошибка входа: ' + getErrorMessage(data), 'error');
        }
    } catch (error) {
        console.error('Ошибка при входе:', error);
        showNotification('Произошла ошибка при подключении к серверу', 'error');
    }
}

async function register() {
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    if (!username || !email || !password) {
        showNotification('Пожалуйста, заполните все поля', 'warning');
        return;
    }

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });

        const data = await response.json();
        console.log('Ответ регистрации:', data);

        if (response.ok) {
            showNotification('Регистрация успешна! Теперь вы можете войти.', 'success');
            toggleRegister(); // Возвращаемся к форме входа
        } else {
            showNotification('Ошибка регистрации: ' + getErrorMessage(data), 'error');
        }
    } catch (error) {
        console.error('Ошибка при регистрации:', error);
        showNotification('Произошла ошибка при подключении к серверу', 'error');
    }
}

// Функции работы с задачами
async function loadTasks() {
    const statusFilter = document.getElementById('filter-status').value;
    const tasksContainer = document.getElementById('tasks-container');

    tasksContainer.innerHTML = '<p>Загрузка задач...</p>';

    try {
        let url = '/tasks/';
        if (statusFilter) {
            url += `?status=${statusFilter}`;
        }

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (response.status === 401) {
            console.log('Токен недействителен, пытаемся обновить');
            const refreshSuccess = await refreshAuthTokens();
            if (refreshSuccess) {
                return loadTasks(); // Повторный запрос после обновления токена
            } else {
                logout();
                return;
            }
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(getErrorMessage(errorData) || 'Ошибка загрузки задач');
        }

        const tasks = await response.json();
        console.log('Загруженные задачи:', tasks);
        renderTasks(tasks);
    } catch (error) {
        console.error('Ошибка загрузки задач:', error);
        tasksContainer.innerHTML = `<p class="error">Ошибка при загрузке задач: ${error.message}</p>`;
        showNotification(error.message || 'Не удалось загрузить задачи', 'error');
    }
}

async function createTask() {
    const title = document.getElementById('task-title').value;
    const description = document.getElementById('task-description').value;
    const dueDateInput = document.getElementById('task-due-date').value;
    const status = document.getElementById('task-status').value;

    if (!title.trim()) {
        showNotification('Введите название задачи', 'warning');
        return;
    }

    try {
        // Преобразуем дату в формат ISO для отправки на сервер
        let dueDate = null;
        if (dueDateInput) {
            dueDate = new Date(dueDateInput);
            if (isNaN(dueDate.getTime())) {
                showNotification('Неверный формат даты', 'warning');
                return;
            }
        }

        const response = await fetch('/tasks/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                title: title,
                description: description.trim() || undefined,
                due_date: dueDate ? dueDate.toISOString() : undefined,
                status: status
            })
        });

        if (response.status === 401) {
            const refreshSuccess = await refreshAuthTokens();
            if (refreshSuccess) {
                return createTask(); // Повторная попытка после обновления токена
            } else {
                logout();
                return;
            }
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(getErrorMessage(errorData) || 'Ошибка создания задачи');
        }

        // Очищаем форму
        document.getElementById('task-title').value = '';
        document.getElementById('task-description').value = '';
        document.getElementById('task-due-date').value = '';

        showNotification('Задача успешно создана!', 'success');
        loadTasks();
    } catch (error) {
        console.error('Ошибка создания задачи:', error);
        showNotification(error.message || 'Не удалось создать задачу', 'error');
    }
}

async function updateTaskStatus(taskId, newStatus) {
    try {
        // Используем существующий PUT эндпоинт вместо несуществующего PATCH /status
        const response = await fetch(`/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({ status: newStatus }) // Отправляем только статус для частичного обновления
        });

        if (response.status === 401) {
            const refreshSuccess = await refreshAuthTokens();
            if (refreshSuccess) {
                return updateTaskStatus(taskId, newStatus);
            } else {
                logout();
                return;
            }
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(getErrorMessage(errorData) || 'Ошибка обновления статуса');
        }

        showNotification('Статус задачи успешно обновлен!', 'success');
        loadTasks(); // Обновляем список задач
    } catch (error) {
        console.error('Ошибка обновления статуса:', error);
        showNotification('Не удалось обновить статус задачи: ' + error.message, 'error');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Вы уверены, что хотите удалить эту задачу?')) {
        return;
    }

    try {
        const response = await fetch(`/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (response.status === 401) {
            const refreshSuccess = await refreshAuthTokens();
            if (refreshSuccess) {
                return deleteTask(taskId);
            } else {
                logout();
                return;
            }
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(getErrorMessage(errorData) || 'Ошибка удаления задачи');
        }

        showNotification('Задача успешно удалена!', 'success');
        loadTasks();
    } catch (error) {
        console.error('Ошибка удаления задачи:', error);
        showNotification('Не удалось удалить задачу: ' + error.message, 'error');
    }
}

// Вспомогательные функции
function renderTasks(tasks) {
    const container = document.getElementById('tasks-container');

    if (tasks.length === 0) {
        container.innerHTML = '<p class="no-tasks">Нет задач. Создайте первую задачу!</p>';
        return;
    }

    let html = '';

    tasks.forEach(task => {
        const dueDate = task.due_date ? new Date(task.due_date) : null;
        const dueDateStr = dueDate ? dueDate.toLocaleString('ru-RU') : 'Не указана';
        const createdAt = new Date(task.created_at).toLocaleString('ru-RU');

        html += `
        <div class="task-card">
            <h3>${escapeHtml(task.title)}</h3>
            <p>${task.description ? escapeHtml(task.description) : '<span class="no-description">Без описания</span>'}</p>
            <div class="task-meta">
                <span>Создано: ${createdAt}</span>
                <span>Выполнить до: ${dueDateStr}</span>
                <span class="status-${task.status}">Статус: ${getStatusText(task.status)}</span>
            </div>
            <div class="task-actions">
                <select onchange="updateTaskStatus(${task.id}, this.value)">
                    <option value="not_started" ${task.status === 'not_started' ? 'selected' : ''}>Не начата</option>
                    <option value="in_progress" ${task.status === 'in_progress' ? 'selected' : ''}>В процессе</option>
                    <option value="completed" ${task.status === 'completed' ? 'selected' : ''}>Завершена</option>
                    <option value="overdue" ${task.status === 'overdue' ? 'selected' : ''}>Просрочена</option>
                </select>
                <button class="danger" onclick="deleteTask(${task.id})">Удалить</button>
            </div>
        </div>
        `;
    });

    container.innerHTML = html;
}

function getStatusText(status) {
    const statusMap = {
        'not_started': 'Не начата',
        'in_progress': 'В процессе',
        'completed': 'Завершена',
        'overdue': 'Просрочена'
    };
    return statusMap[status] || status;
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: переименована функция из refreshToken() в refreshAuthTokens()
async function refreshAuthTokens() {
    if (!refreshToken) {
        console.log('Нет refresh токена');
        showNotification('Сессия истекла. Пожалуйста, войдите снова.', 'warning');
        return false;
    }

    try {
        const response = await fetch('/auth/refresh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                'refresh_token': refreshToken
            })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('accessToken', data.access_token);
            accessToken = data.access_token;
            console.log('Токен успешно обновлен');
            return true;
        } else {
            const errorData = await response.json();
            console.log('Не удалось обновить токен:', errorData);
            return false;
        }
    } catch (error) {
        console.error('Ошибка обновления токена:', error);
        return false;
    }
}

function logout() {
    console.log('Выход из системы');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    accessToken = null;
    refreshToken = null;

    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('todo-section').style.display = 'none';
    document.getElementById('tasks-container').innerHTML = '<p>Нет задач. Создайте первую задачу!</p>';

    // Очищаем форму входа
    document.getElementById('login-email').value = '';
    document.getElementById('login-password').value = '';

    showNotification('Вы успешно вышли из системы', 'info');
}

function toggleRegister() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (loginForm.style.display === 'none') {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
    }
}

// Функция для показа кастомных уведомлений
function showNotification(message, type = 'info') {
    const container = document.getElementById('notifications-container');

    // Создаем уведомление
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    // Определяем иконку в зависимости от типа
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '❌';
    if (type === 'warning') icon = '⚠️';

    notification.innerHTML = `
        <div class="notification-content">
            <span>${icon}</span>
            <span>${message}</span>
        </div>
        <button class="close-notification">&times;</button>
    `;

    // Добавляем уведомление в контейнер
    container.appendChild(notification);

    // Удаляем уведомление через 5 секунд или при клике на крестик
    const timeoutId = setTimeout(() => {
        removeNotification(notification);
    }, 5000);

    // Добавляем обработчик клика по крестик
    notification.querySelector('.close-notification').addEventListener('click', () => {
        clearTimeout(timeoutId);
        removeNotification(notification);
    });

    // Добавляем обработчик клика по всему уведомлению
    notification.addEventListener('click', (e) => {
        if (!e.target.classList.contains('close-notification')) {
            clearTimeout(timeoutId);
            removeNotification(notification);
        }
    });
}

function removeNotification(notification) {
    notification.style.animation = 'fadeOut 0.5s ease-in';
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 500);
}

// Функция для извлечения сообщения об ошибке из ответа сервера
function getErrorMessage(errorData) {
    if (!errorData) return 'Произошла неизвестная ошибка';

    // Если есть детальное описание ошибки
    if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
            // Обработка ошибок валидации Pydantic
            return errorData.detail.map(err => {
                if (err.msg && err.msg.includes('Value error,')) {
                    return err.msg.replace('Value error,', '').trim();
                }
                return err.msg || 'Ошибка валидации';
            }).join('; ');
        } else if (typeof errorData.detail === 'string') {
            // Стандартное сообщение об ошибке
            return errorData.detail;
        }
    }

    // Если ошибка содержит поле "message"
    if (errorData.message) {
        return errorData.message;
    }

    // Если в ответе есть другие поля с сообщениями
    if (errorData.error) {
        return typeof errorData.error === 'string' ? errorData.error : JSON.stringify(errorData.error);
    }

    // Если ничего не помогло, возвращаем строковое представление
    return JSON.stringify(errorData);
}

// Вспомогательная функция для обработки ошибок API
async function handleApiError(response) {
    if (response.status === 401) {
        throw new Error('Сессия истекла. Пожалуйста, войдите снова.');
    }

    if (!response.ok) {
        let errorData;
        try {
            errorData = await response.json();
        } catch (e) {
            errorData = { detail: `Ошибка сервера: ${response.status} ${response.statusText}` };
        }

        throw new Error(getErrorMessage(errorData));
    }

    return response;
}

// Добавляем периодическую проверку токена
setInterval(() => {
    if (accessToken) {
        console.log('Токен активен');
    }
}, 300000); // Проверяем каждые 5 минут