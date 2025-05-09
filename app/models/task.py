from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class TaskCreate(BaseModel):
    """Модель для создания новой задачи"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    due_date: datetime | None = None
    status: str = Field(..., pattern="^(pending|completed|overdue)$")

    @field_validator("title")
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Название задачи не может быть пустым")
        return v

    @field_validator("due_date")
    def due_date_not_in_past(cls, v):
        if v is not None and v < datetime.now().replace(tzinfo=None):
            raise ValueError("Дата выполнения не может быть в прошлом")
        return v


class TaskUpdate(BaseModel):
    """Модель для обновления задачи"""
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    due_date: datetime | None = None
    status: str | None = Field(None, pattern="^(pending|completed|overdue)$")

    @field_validator("title")
    def title_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Название задачи не может быть пустым")
        return v

    @field_validator("due_date")
    def due_date_not_in_past(cls, v):
        if v is not None and v < datetime.now().replace(tzinfo=None):
            raise ValueError("Дата выполнения не может быть в прошлом")
        return v


class TaskResponse(BaseModel):
    """Модель для ответа API с данными задачи"""
    id: int
    title: str
    description: str | None = None
    created_at: datetime
    due_date: datetime | None = None
    status: str

    class Config:
        from_attributes = True