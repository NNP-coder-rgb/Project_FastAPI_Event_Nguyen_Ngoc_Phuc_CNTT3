from fastapi import Request
from sqlalchemy import or_
from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse
from typing import List, Optional
from typing import Any, Dict

def get_me_ser(current_user: User) -> UserResponse:
    return UserResponse.model_validate(current_user)

def get_all_users_ser(
    db: Session,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    size: int = 10
) -> Dict[str, Any]:
    query = db.query(User)

    if search:
        query = query.filter(
            or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total_items = query.count()
    offset = (page - 1) * size
    users = query.offset(offset).limit(size).all()

    return {
        "items": [UserResponse.model_validate(u) for u in users]
    }