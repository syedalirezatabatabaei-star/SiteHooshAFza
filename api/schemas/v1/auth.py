from pydantic import BaseModel, field_validator
from typing import Optional
import re


class RegisterRequest(BaseModel):
    phone_number: str
    password: str
    first_name: str
    last_name: str

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        v = v.strip()
        if not re.match(r'^0[0-9]{10}$', v):
            raise ValueError('شماره تلفن نامعتبر است')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('رمز عبور باید حداقل ۶ کاراکتر باشد')
        return v


class LoginRequest(BaseModel):
    phone_number: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    user: 'UserInfo'


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('رمز عبور جدید باید حداقل ۶ کاراکتر باشد')
        return v


class UserInfo(BaseModel):
    id: int
    phone_number: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    role: str
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
