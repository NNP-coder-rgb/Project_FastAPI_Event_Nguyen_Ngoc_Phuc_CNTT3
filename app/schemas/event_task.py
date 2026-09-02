from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.user import UserResponse

class EventTaskBase(BaseModel):
    title: str
    description: str
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class EventTaskCreate(BaseModel):
    assignee_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class EventTaskUpdate(BaseModel):
    assignee_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: str = "TODO"
    priority: str = "MEDIUM"
    due_date: Optional[datetime] = None

class EventTaskResponse(BaseModel):
    id: int
    event_id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
    assignee: Optional[UserResponse] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )