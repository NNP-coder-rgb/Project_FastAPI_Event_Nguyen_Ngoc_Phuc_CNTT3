from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest, TokenResponse
from sqlalchemy.orm import Session
from app.models.user import User
from fastapi import HTTPException, status, Request
from typing import Optional
from app.core.security import hashed_password, verify_password, create_access_token, create_refresh_token, decode_access_token


def register_ser(user: UserCreate, db: Session, request: Request):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )

    new_user = User(
        email = user.email,
        full_name = user.full_name,
        password_hash = hashed_password(user.password),
        role = user.role or "USER"
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def login_ser(login_data: LoginRequest, db: Session, request: Request) -> TokenResponse:
    user_db = db.query(User).filter(User.email == login_data.email).first()
    if not user_db or not verify_password(login_data.password, user_db.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email hoặc mật khẩu không chính xác"
        )

    if not user_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đã bị vô hiệu hóa"
        )

    access_token = create_access_token({
        "sub": str(user_db.id),
        "role": user_db.role
    })

    refresh_token = create_refresh_token({
        "sub": str(user_db.id)
    })

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )   

def refresh_ser(refresh_token: str, db: Session) -> TokenResponse:
    payload = decode_access_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ hoặc đã hết hạn"
        )

    user_db = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user_db or not user_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại hoặc đã bị khóa"
        )

    return TokenResponse(
        access_token=create_access_token({"sub": str(user_db.id), "role": user_db.role}),
        refresh_token=create_refresh_token({"sub": str(user_db.id)}),
        token_type="bearer"
    )