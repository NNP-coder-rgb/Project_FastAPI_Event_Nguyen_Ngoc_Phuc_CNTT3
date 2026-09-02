from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# class ResponseUser(BaseModel):
#     id: int
#     email: str
#     role: str
    
#     model_config = ConfigDict(
#         from_attributes=True
#     )

class TokenResponse(BaseModel):
    # user_info: ResponseUser
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str
