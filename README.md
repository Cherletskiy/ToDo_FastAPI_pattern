# 📝 ToDo API (FastAPI + Vanilla JS)

Небольшое full‑stack приложение для управления задачами, выполненное в рамках **тестового задания**.
---

## 🚀 Возможности

### Backend
- CRUD‑операции с задачами
- JWT‑аутентификация (access + refresh)
- автоматическое определение просроченных задач
- фильтрация задач по статусу и дате
- логирование действий

### Frontend
- авторизация и регистрация пользователей
- создание, изменение и удаление задач
- обновление access‑токена через refresh
- простой UI без фреймворков (vanilla JS)
---

## 🛠️ Технологии

### Backend
- **FastAPI**
- **SQLAlchemy 2 (async)**
- **PostgreSQL**
- **JWT (PyJWT)**
- **Pydantic v2**

### Frontend
- HTML + CSS
- Vanilla JavaScript (без фреймворков)

### Инфраструктура
- Docker
- docker‑compose 

---

## ⚙️ Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/Cherletskiy/ToDo_FastAPI_pattern.git
cd ToDo_FastAPI_pattern
````

### 2. Настройка переменных окружения

Создайте файл `.env` на основе примера (`.env.example`):
```bash
cp .env.example .env
```

```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=ToDo
DB_USER=postgres
DB_PASSWORD=postgres

SECRET_KEY=secret
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Запуск приложения

```bash
docker-compose up --build
```

* Приложение будет доступно на `http://127.0.0.1:8000`
* Swagger UI — по адресу `http://127.0.0.1:8000/docs`

### 4. Остановка приложения

```bash
docker-compose down          # остановка
docker-compose down -v       # остановка и удаление volumes (сброс БД)
```

---

## 📦 Зависимости

Основные библиотеки указаны в `requirements.txt`:

* `fastapi==0.115.0`
* `uvicorn==0.32.0`
* `sqlalchemy==2.0.20`
* `asyncpg==0.29.0`
* `pydantic[email]==2.9.2`
* `python-dotenv==1.0.1`
* `pyjwt[crypto]==2.8.0`
* `python-multipart==0.0.19`
* `alembic==1.15.2`
* `pytz==2025.2`
* `bcrypt==5.0.0`
* `jinja2==3.1.4`
* `aiofiles==23.2.1`

---

## 🗂️ Структура проекта

```
todo_fastapi_pattern/
├── app/
│   ├── database/          # Подключение к БД и ORM‑модели
│   ├── models/            # Pydantic‑схемы
│   ├── repository/        # Работа с БД
│   ├── services/          # Бизнес‑логика
│   ├── routes/            # API‑эндпоинты
│   ├── static/            # CSS и JS
│   ├── templates/         # HTML
│   ├── logging_config.py
│   └── main.py            # Точка входа
├── tests/                 # Ручные тесты API
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🔐 Аутентификация (JWT)

| Метод | Эндпоинт         | Описание                        | Тело запроса (JSON/Форма)                                  |
| ----- | ---------------- | ------------------------------- | ---------------------------------------------------------- |
| POST  | `/auth/register` | Регистрация пользователя        | `{ "username": "...", "email": "...", "password": "..." }` |
| POST  | `/auth/login`    | Логин, выдача токенов           | `email=...&password=...` (форма)                           |
| POST  | `/auth/refresh`  | Обновление access-токена        | `refresh_token=...` (форма)                                |
| GET   | `/auth/me`       | Получение текущего пользователя | Требуется Bearer access токен                              |

---

## ✅ Эндпоинты задач

| Метод  | Эндпоинт      | Описание              | Примечания                                                                                     |
| ------ | ------------- | --------------------- | ---------------------------------------------------------------------------------------------- |
| POST   | `/tasks/`     | Создание задачи       | `{ "title": "...", "description": "...", "due_date": "YYYY-MM-DDTHH:MM:SS", "status": "..." }` |
| GET    | `/tasks/`     | Получить список задач | Поддерживает фильтры: `status=...`, `due_date_from=...`, `due_date_to=...`                     |
| GET    | `/tasks/{id}` | Получить задачу по ID |                                                                                                |
| PUT    | `/tasks/{id}` | Обновить задачу по ID | Частичное обновление (можно указать только изменяемые поля)                                    |
| DELETE | `/tasks/{id}` | Удалить задачу по ID  |                                                                                                |

---

## 📡 Примеры запросов

### 1. Регистрация

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","email":"test@example.com","password":"testpassword123"}'
```

### 2. Логин

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "email=test@example.com&password=testpassword123"
```

### 3. Создание задачи

```bash
curl -X POST http://127.0.0.1:8000/tasks/ \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{"title":"Купить продукты","description":"Молоко, хлеб","due_date":"2025-06-01T12:00:00","status":"not_started"}'
```

### 4. Фильтрация задач

```bash
curl -X GET "http://127.0.0.1:8000/tasks/?status=completed&due_date_from=2025-06-01&due_date_to=2025-06-10" \
     -H "Authorization: Bearer <access_token>"
```

### 5. Обновление задачи

```bash
curl -X PUT http://127.0.0.1:8000/tasks/1 \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{"description":"Обновлённое описание","status":"in_progress"}'
```

### 6. Обновление токена

```bash
curl -X POST http://127.0.0.1:8000/auth/refresh \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "refresh_token=<refresh_token>"
```

---


## 🗃️ База данных

### Таблица `users`
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_users_id ON users(id);
CREATE INDEX ix_users_username ON users(username);
CREATE INDEX ix_users_email ON users(email);
````

### Таблица `tasks`

```sql
CREATE TYPE taskstatus AS ENUM ('not_started', 'in_progress', 'completed', 'overdue');

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    status taskstatus NOT NULL DEFAULT 'not_started'
);
CREATE INDEX ix_tasks_id ON tasks(id);
CREATE INDEX ix_tasks_user_id ON tasks(user_id);
CREATE INDEX ix_tasks_title ON tasks(title);
```

> ⚙️ Поле `status` реализовано как ENUM со значениями:
>
> * `not_started`
> * `in_progress`
> * `completed`
> * `overdue`
>
> ✅ Все индексы добавлены для повышения производительности фильтрации и поиска.

> 🔁 При удалении пользователя все связанные задачи также удаляются (ON DELETE CASCADE).

> 🧩 Схема создаётся автоматически через SQLAlchemy. Фильтрация по `due_date` оптимизирована.

---

## 🧪 Тестирование

* Основной файл: `tests/manual_test.py`
* Запуск:

  ```bash
  docker-compose up --build
  python tests/manual_test.py
  ```

---

## 🧾 Логирование

* Все действия записываются в файл `app.log`
* Включает: старт и остановку приложения, обращения к API, ошибки, попытки логина и т.п.

---

