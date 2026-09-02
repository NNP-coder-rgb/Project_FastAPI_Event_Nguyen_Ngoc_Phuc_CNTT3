from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.user import UserResponse
from datetime import datetime

class EventStaffBase(BaseModel):
    role: str = "MEMBER"

class EventStaffCreate(BaseModel):
    role: Optional[str] = "MEMBER"
    user_id: int

class EventStaffResponse(BaseModel):
    user_id: int
    event_id: int
    role: str
    user: Optional[UserResponse] = None
    joined_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
