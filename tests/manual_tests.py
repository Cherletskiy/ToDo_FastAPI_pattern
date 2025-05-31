import random
import string
import requests
from datetime import datetime, timedelta


BASE_URL = "http://localhost:8000"

rand_mail = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(5, 15))) + "@example.com"

user_data = {
    "username": "new_user",
    "email": rand_mail,
    "password": "anotherpassword123"
}

token = ""
refresh_token = ""


def test_register_success():
    """Тест: успешная регистрация нового пользователя."""
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Register Success: Status {response.status_code}, Response {response.json()}")
    json_res = response.json()
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    assert json_res["email"] == user_data["email"], "Email mismatch"
    assert json_res["username"] == user_data["username"], "Username mismatch"
    assert json_res["created_at"] is not None, "Created at should not be None"
    assert json_res["id"] > 0, "ID should be greater than 0"
    assert len(json_res) == 4, "Expected 4 fields in response"
    return json_res


def test_register_duplicate_email():
    """Тест: регистрация с существующим email."""
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Duplicate Email: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert response.json()["detail"] == "Email уже зарегистрирован", "Expected duplicate email error"


def test_register_incorrect_email():
    """Тест: регистрация с некорректным email."""
    incorrect_data = user_data.copy()
    incorrect_data["email"] = "invalid_email"
    response = requests.post(f"{BASE_URL}/auth/register", json=incorrect_data)
    print(f"Invalid Email: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


def test_login_for_access_token():
    """Тест: успешная аутентификация и получение токенов."""
    data_login = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=data_login)
    print(f"Login Success: Status {response.status_code}, Response {response.json()}")
    global token, refresh_token
    token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "access_token" in response.json(), "Access token not in response"
    assert "refresh_token" in response.json(), "Refresh token not in response"
    assert response.json()["token_type"] == "bearer", "Token type should be bearer"


def test_login_incorrect_email_password():
    """Тест: аутентификация с некорректным email или паролем."""
    data_login = {
        "email": user_data["email"],
        "password": user_data["password"]
    }

    incorrect_data_login = data_login.copy()
    incorrect_data_login["email"] = "invalid_email"
    response = requests.post(f"{BASE_URL}/auth/login", data=incorrect_data_login)
    print(f"Invalid Email: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    assert response.json()["detail"] == "Неверное имя пользователя или пароль", "Expected incorrect email error"

    incorrect_data_login = data_login.copy()
    incorrect_data_login["password"] = "invalid_password"
    response = requests.post(f"{BASE_URL}/auth/login", data=incorrect_data_login)
    print(f"Invalid Password: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    assert response.json()["detail"] == "Неверное имя пользователя или пароль", "Expected incorrect password error"


def test_get_current_user():
    """Тест: получение данных текущего пользователя."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Get Current User: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    json_res = response.json()
    assert json_res["email"] == user_data["email"], "Email mismatch"
    assert json_res["username"] == user_data["username"], "Username mismatch"
    assert json_res["id"] > 0, "ID should be greater than 0"
    assert json_res["created_at"] is not None, "Created at should not be None"
    assert len(json_res) == 4, "Expected 4 fields in response"

    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Get Current User: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


def test_refresh_token():
    """Тест: обновление токена."""
    data = {"refresh_token": refresh_token}
    response = requests.post(f"{BASE_URL}/auth/refresh", data=data)
    print(f"Refresh Token: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    json_res = response.json()
    global token
    token = json_res["access_token"]
    assert "access_token" in json_res, "Access token not in response"
    assert json_res["refresh_token"] == refresh_token, "Refresh token should remain the same"
    assert json_res["token_type"] == "bearer", "Token type should be bearer"


def test_create_task():
    """Тест: создание новой задачи."""
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "due_date": (datetime.now() + timedelta(days=1)).replace(tzinfo=None).isoformat(),
        "status": "not_started"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
    print(f"Create Task: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    json_res = response.json()
    assert json_res["title"] == task_data["title"], "Title mismatch"
    assert json_res["description"] == task_data["description"], "Description mismatch"
    assert json_res["status"] == task_data["status"], "Status mismatch"
    assert json_res["id"] > 0, "ID should be greater than 0"
    assert json_res["user_id"] > 0, "User ID should be greater than 0"
    assert json_res["created_at"] is not None, "Created at should not be None"
    return json_res["id"]


def test_create_task_invalid_due_date():
    """Тест: создание задачи с прошедшей датой."""
    task_data = {
        "title": "Invalid Task",
        "description": "Task with past due date",
        "due_date": (datetime.now() - timedelta(days=1)).replace(tzinfo=None).isoformat(),
        "status": "not_started"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
    print(f"Create Task Invalid Due Date: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


def test_update_task():
    """Тест: обновление задачи."""
    task_id = test_create_task()
    update_data = {
        "title": "Updated Task",
        "description": "Updated description",
        "status": "in_progress"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data, headers=headers)
    print(f"Update Task: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    json_res = response.json()
    assert json_res["id"] == task_id, "Task ID mismatch"
    assert json_res["title"] == update_data["title"], "Title mismatch"
    assert json_res["description"] == update_data["description"], "Description mismatch"
    assert json_res["status"] == update_data["status"], "Status mismatch"


def test_update_task_not_found():
    """Тест: обновление несуществующей задачи."""
    update_data = {
        "title": "Updated Task",
        "description": "Updated description",
        "status": "in_progress"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/tasks/99999", json=update_data, headers=headers)
    print(f"Update Task Not Found: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    assert response.json()["detail"] == "Задача не найдена", "Expected task not found error"


def test_get_task():
    """Тест: получение задачи по ID."""
    task_id = test_create_task()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    print(f"Get Task: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    json_res = response.json()
    assert json_res["id"] == task_id, "Task ID mismatch"
    assert json_res["title"] == "Test Task", "Title mismatch"
    assert json_res["user_id"] > 0, "User ID should be greater than 0"


def test_get_task_not_found():
    """Тест: получение несуществующей задачи."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tasks/99999", headers=headers)
    print(f"Get Task Not Found: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    assert response.json()["detail"] == "Задача не найдена", "Expected task not found error"


def test_get_tasks():
    """Тест: получение списка задач."""
    test_create_task()  # Создаем задачу для проверки
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
    print(f"Get Tasks: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    json_res = response.json()
    assert isinstance(json_res, list), "Response should be a list"
    assert len(json_res) > 0, "Expected at least one task"
    assert json_res[0]["title"] == "Test Task", "Title mismatch"


def test_get_tasks_with_filters():
    """Тест: получение задач с фильтрами по статусу."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tasks/?status=not_started", headers=headers)
    print(f"Get Tasks with Filter: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    json_res = response.json()
    assert isinstance(json_res, list), "Response should be a list"
    for task in json_res:
        assert task["status"] == "not_started", "Status filter mismatch"


def test_delete_task():
    """Тест: удаление задачи."""
    task_id = test_create_task()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    print(f"Delete Task: Status {response.status_code}, Response {response.text}")
    assert response.status_code == 204, f"Expected 204, got {response.status_code}"
    # Проверяем, что задача удалена
    response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


def test_delete_task_not_found():
    """Тест: удаление несуществующей задачи."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/tasks/99999", headers=headers)
    print(f"Delete Task Not Found: Status {response.status_code}, Response {response.json()}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    assert response.json()["detail"] == "Задача не найдена", "Expected task not found error"


def run_tests():
    """Запускает все тесты."""
    try:
        print("Starting manual tests...")
        test_register_success()
        test_register_duplicate_email()
        test_register_incorrect_email()
        test_login_for_access_token()
        test_get_current_user()
        test_refresh_token()
        test_create_task()
        test_create_task_invalid_due_date()
        test_get_task()
        test_get_task_not_found()
        test_get_tasks()
        test_get_tasks_with_filters()
        test_update_task()
        test_update_task_not_found()
        test_delete_task()
        test_delete_task_not_found()
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    run_tests()