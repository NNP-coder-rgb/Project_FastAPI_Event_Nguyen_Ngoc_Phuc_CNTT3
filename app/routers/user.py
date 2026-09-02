from fastapi import APIRouter, Request, Depends, status, Query
from app.services.user import get_me_ser, get_all_users_ser
from app.models.user import User
from app.dependencies.auth import get_current_user, require_role
from app.schemas.response import APIResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("/me", response_model=APIResponse)
def get_me(request: Request, current_user: User = Depends(get_current_user)):
    user_data = get_me_ser(current_user=current_user)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Lấy thông tin cá nhân thành công",
        data=user_data,
        errors=None,
        path=request.url.path
    )

@router.get("", response_model=APIResponse)
def get_all_users(
    request: Request,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("ADMIN"))
):
    result = get_all_users_ser(db=db, search=search, is_active=is_active, page=page, size=size)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách người dùng thành công",
        data=result,
        errors=None,
        path=request.url.path
    )