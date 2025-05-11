# ToDo API

Простое REST API для управления задачами, построенное на **FastAPI** и **PostgreSQL**. Приложение использует модульную структуру с элементами слоистой архитектуры (репозиторий-сервис-маршруты). API поддерживает CRUD-операции (создание, чтение, обновление, удаление задач), фильтрацию по статусу и логирование всех действий. 

## Возможности
- Создание, просмотр, обновление и удаление задач.
- Фильтрация задач по статусу и дате.
- Логирование всех операций в файл (`app.log`).
- Интерактивная документация API через Swagger (`/docs`).

## Технологии

- **FastAPI**
- **PostgreSQL**
- **Docker & Docker Compose**
- **Pydantic**
- **Asyncpg**
- **Python 3.12**

## Требования
- **Docker Desktop** (для Windows/Mac) или **Docker** (для Linux).
- **Git** (для клонирования репозитория).

## Установка

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/Cherletskiy/ToDo_FastAPI_pattern.git
   cd ToDo_FastAPI_pattern
   ```

2. **Настройте переменные окружения**:
   Создайте файл `.env` в корне проекта со следующим содержимым:
   ```plaintext
   DB_HOST=postgres
   DB_PORT=5432
   DB_NAME=ToDo
   DB_USER=postgres
   DB_PASSWORD=postgres
   ```

3. **Запустите приложение**:
   ```bash
   docker-compose up --build
   ```
   Это:
   - Соберёт и запустит приложение FastAPI (на `http://127.0.0.1:8000`).
   - Запустит базу данных PostgreSQL.
   - Инициализирует схему базы данных.

4. **Доступ к API**:
   - Откройте `http://127.0.0.1:8000/docs` в браузере для просмотра Swagger UI.
   - Используйте `curl` или Postman для отправки запросов.

5. **Остановка приложения**:
   ```bash
   docker-compose down
   ```
   Для сброса базы данных:
   ```bash
   docker-compose down -v
   ```

## Зависимости
Перечислены в `requirements.txt`:
- `fastapi==0.115.0`: Веб-фреймворк.
- `uvicorn==0.31.0`: ASGI-сервер.
- `asyncpg==0.29.0`: Драйвер для PostgreSQL.
- `pydantic==2.9.2`: Валидация данных.
- `python-dotenv==1.0.1`: Управление переменными окружения.
- `httpx==0.27.2`: HTTP-клиент для тестов.

## Структура проекта
```
todo-fastapi-pattern/
├── app/                    # Код приложения
│   ├── database/           # Подключение к базе и схема
│   ├── models/             # Модели Pydantic
│   ├── repository/         # Операции с базой данных
│   ├── routes/             # Эндпоинты API
│   ├── services/           # Бизнес-логика
│   ├── logging_config.py   # Настройка логирования
│   ├── main.py             # Точка входа FastAPI
├── tests/                  # Юнит-тесты
├── .env                    # Переменные окружения
├── Dockerfile             # Конфигурация Docker для приложения
├── docker-compose.yml      # Конфигурация Docker Compose
├── requirements.txt        # Зависимости Python
```

## Эндпоинты API

| Метод  | Эндпоинт           | Описание                        | Тело запроса (JSON)                                                                          |
|--------|--------------------|---------------------------------|----------------------------------------------------------------------------------------------|
| POST   | `/tasks/`          | Создать задачу                  | `{ "title": "строка", "description": "строка", "status": "pending"\"completed"\"overdue" }`  |
| GET    | `/tasks/`          | Получить список задач           | -                                                                                            |
| GET    | `/tasks/{id}`      | Получить задачу по ID           | -                                                                                            |
| PUT    | `/tasks/{id}`      | Обновить задачу по ID           | `{ "title": "строка", "description": "строка", "status": "pending"\"completed"\"overdue" }` |
| DELETE | `/tasks/{id}`      | Удалить задачу по ID            | -                                                                                            |

### Примеры запросов

1. **Создание задачи**:
   ```bash
   curl -X POST "http://127.0.0.1:8000/tasks/" -H "Content-Type: application/json" -d '{"title":"Купить продукты","description":"Молоко, хлеб, яйца","status":"pending"}'
   ```
   **Ответ**:
   ```json
   {"id":1,"title":"Купить продукты","description":"Молоко, хлеб, яйца","created_at":"2025-05-11T08:40:00","due_date":null,"status":"pending"}
   ```

2. **Получение всех задач**:
   ```bash
   curl -X GET "http://127.0.0.1:8000/tasks/"
   ```
   **Ответ**:
   ```json
   [{"id":1,"title":"Купить продукты","description":"Молоко, хлеб, яйца","created_at":"2025-05-11T08:40:00","due_date":null,"status":"pending"}]
   ```

3. **Обновление задачи**:
   ```bash
   curl -X PATCH "http://127.0.0.1:8000/tasks/1" -H "Content-Type: application/json" -d '{"title":"Купить продукты","description":"Молоко, хлеб","status":"in_progress"}'
   ```
   **Ответ**:
   ```json
   {"id":1,"title":"Купить продукты","description":"Молоко, хлеб","created_at":"2025-05-11T08:40:00","due_date":null,"status":"in_progress"}
   ```

## База данных
- **СУБД**: PostgreSQL 16.
- **Таблица**: `tasks`
  ```sql
  CREATE TABLE IF NOT EXISTS tasks (
     id SERIAL PRIMARY KEY,
     title VARCHAR(255) NOT NULL,
     description TEXT,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     due_date TIMESTAMP,
     status VARCHAR(20) NOT NULL
  );
  ```
- Схема автоматически создаётся при запуске (см. `app/database/db.py`).

## Тестирование
В разработке. 

## Логирование
- Логи записываются в файл `app.log` в корне проекта.
- Включают события запуска/остановки и запросы к API.
