from pydantic import BaseModel, validator, Field, field_validator
from datetime import datetime
from typing import Optional
import pytz


class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = None
    status: str = Field(..., pattern="^(pending|completed|overdue)$")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(pending|completed|overdue)$")

    class Config:
        extra = "forbid"


class TaskResponse(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

    @field_validator("due_date")
    def due_date_not_in_past(cls, v):
        """Проверяет, что due_date не в прошлом, сравнивая в UTC"""
        if v is not None:
            now_utc = datetime.now(tz=pytz.UTC)
            v_utc = v if v.tzinfo else v.replace(tzinfo=pytz.UTC)
            if v_utc < now_utc:
                raise ValueError("Дата выполнения не может быть в прошлом")
        return v