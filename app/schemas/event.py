from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from app.schemas.user import UserResponse

class EventBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Tên sự kiên không trống, tối đa 100 ký tự")
    description: Optional[str] = None


class EventCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Tên sự kiện không trống, tối đã 100 ký tự")
    description: str


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class EventResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner: Optional[UserResponse] = None
    created_at: datetime
    is_delete: bool

    model_config = ConfigDict(
        from_attributes=True
    )
