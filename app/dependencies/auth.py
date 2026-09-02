from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import  decode_access_token, create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.auth import TokenResponse

security = HTTPBearer()

def get_current_user(
        auth: HTTPAuthorizationCredentials = Depends(security), 
        db: Session = Depends(get_db)
    ):
    token = auth.credentials
    payload = decode_access_token(token)
    if not payload or not payload.get("sub") or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn"
        )

    user_id = payload.get("sub")
    user_db = db.query(User).filter(User.id == int(user_id)).first()

    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy người dùng"
        )

    if not user_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đã bị vô hiệu hóa"
        )

    return user_db

def refresh_ser(refresh_token: str, db: Session) -> TokenResponse:
    payload = decode_access_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Refresh token không hợp lệ hoặc đã hết hạn")

    user_db = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user_db or not user_db.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Người dùng không tồn tại hoặc đã bị khoá")

    return TokenResponse(
        access_token=create_access_token({"sub": str(user_db.id), "role": user_db.role}),
        refresh_token=create_refresh_token({"sub": str(user_db.id)}),  # rotate luôn
        token_type="bearer"
    )

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập tài nguyên này"
            )
        return current_user
    return role_checker