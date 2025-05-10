from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
import pytz


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    status: str = "pending"

    @field_validator("title")
    def title_not_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Название задачи не может быть пустым")
        return v

    @field_validator("status")
    def status_must_be_valid(cls, v):
        if v not in ["pending", "completed", "overdue"]:
            raise ValueError("Статус должен быть 'pending', 'completed' или 'overdue'")
        return v

    @field_validator("due_date")
    def due_date_not_in_past(cls, v):
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
    def title_not_empty(cls, v):
        if v is not None and (not v or v.strip() == ""):
            raise ValueError("Название задачи не может быть пустым")
        return v

    @field_validator("status")
    def status_must_be_valid(cls, v):
        if v is not None and v not in ["pending", "completed", "overdue"]:
            raise ValueError("Статус должен быть 'pending', 'completed' или 'overdue'")
        return v

    @field_validator("due_date")
    def due_date_not_in_past(cls, v):
        if v is not None:
            now_utc = datetime.now(tz=pytz.UTC)
            v_utc = v if v.tzinfo else v.replace(tzinfo=pytz.UTC)
            if v_utc < now_utc:
                raise ValueError("Дата выполнения не может быть в прошлом")
        return v

    model_config = ConfigDict(extra="forbid")


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    created_at: datetime
    due_date: datetime | None
    status: str

    model_config = ConfigDict(from_attributes=True)