from fastapi import APIRouter, Depends, Request, status
from app.schemas.user import UserCreate
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.services.auth import register_ser, login_ser, refresh_ser
from app.schemas.user import UserResponse
from app.schemas.auth import LoginRequest, RefreshTokenRequest
from app.schemas.response import APIResponse
from slowapi import Limiter
from slowapi.util import get_remote_address


router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=None)
def register(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    new_user = register_ser(user=user,db=db, request=request)
    return APIResponse(
        status_code=status.HTTP_201_CREATED,
        message="Tạo tài khoản thành công",
        data=UserResponse.model_validate(new_user),
        errors=None,
        path=request.url.path
    )

@router.post("/login", response_model=None)
@limiter.limit("5/minute")
def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    tokens = login_ser(login_data=login_data, db=db, request = request)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Tạo Token thành công",
        data=tokens,
        errors=None,
        path=request.url.path
    )

@router.post("/refresh", response_model=None)
def refresh_token(body: RefreshTokenRequest, request: Request, db: Session = Depends(get_db)):
    tokens = refresh_ser(refresh_token=body.refresh_token, db=db)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Làm mới Token thành công",
        data=tokens,
        errors=None,
        path=request.url.path
    )