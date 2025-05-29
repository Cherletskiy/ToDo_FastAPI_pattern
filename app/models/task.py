from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
import pytz

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    status: str = "not_started"

    @field_validator("title")
    def title_not_empty(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("Название задачи не может быть пустым")
        return v

    @field_validator("status")
    def status_must_be_valid(cls, v: str) -> str:
        valid_statuses = ["not_started", "in_progress", "completed", "overdue"]
        if v not in valid_statuses:
            raise ValueError(f"Статус должен быть одним из: {', '.join(valid_statuses)}")
        return v

    @field_validator("due_date")
    def due_date_not_in_past(cls, v: datetime | None) -> datetime | None:
        if v is not None:
            now_utc = datetime.now(tz=pytz.UTC)
            v_utc = v if v.tzinfo else v.replace(tzinfo=pytz.UTC)
            if v_utc < now_utc:
                raise ValueError("Дата выполнения не может быть в прошлом")
        return v

    model_config = ConfigDict(extra="forbid")

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    status: str | None = None

    @field_validator("title")
    def title_not_empty(cls, v: str | None) -> str | None:
        if v is not None and (not v or v.strip() == ""):
            raise ValueError("Название задачи не может быть пустым")
        return v

    @field_validator("status")
    def status_must_be_valid(cls, v: str | None) -> str | None:
        if v is not None:
            valid_statuses = ["not_started", "in_progress", "completed", "overdue"]
            if v not in valid_statuses:
                raise ValueError(f"Статус должен быть одним из: {', '.join(valid_statuses)}")
        return v

    @field_validator("due_date")
    def due_date_not_in_past(cls, v: datetime | None) -> datetime | None:
        if v is not None:
            now_utc = datetime.now(tz=pytz.UTC)
            v_utc = v if v.tzinfo else v.replace(tzinfo=pytz.UTC)
            if v_utc < now_utc:
                raise ValueError("Дата выполнения не может быть в прошлом")
        return v

    model_config = ConfigDict(extra="forbid")

class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    created_at: datetime
    due_date: datetime | None
    status: str

    model_config = ConfigDict(from_attributes=True)