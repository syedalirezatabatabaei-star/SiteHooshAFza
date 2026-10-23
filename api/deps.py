from datetime import datetime, timedelta, timezone
from typing import Optional
from pathlib import Path
import importlib.util

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from django.contrib.auth import get_user_model

BASE_DIR = Path(__file__).resolve().parent
config_path = BASE_DIR / 'config.py'
spec = importlib.util.spec_from_file_location('api_config', config_path)
api_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_config)

JWT_SECRET_KEY = api_config.JWT_SECRET_KEY
JWT_ALGORITHM = api_config.JWT_ALGORITHM
JWT_ISSUER = api_config.JWT_ISSUER
JWT_ACCESS_TOKEN_LIFETIME_MINUTES = api_config.JWT_ACCESS_TOKEN_LIFETIME_MINUTES
JWT_REFRESH_TOKEN_LIFETIME_DAYS = api_config.JWT_REFRESH_TOKEN_LIFETIME_DAYS

User = get_user_model()
security = HTTPBearer(auto_error=False)


def create_access_token(user_id: int, phone_number: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({
        'sub': str(user_id), 'phone': phone_number, 'role': role,
        'type': 'access', 'iss': JWT_ISSUER, 'iat': now,
        'exp': now + timedelta(minutes=JWT_ACCESS_TOKEN_LIFETIME_MINUTES),
    }, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({
        'sub': str(user_id), 'type': 'refresh', 'iss': JWT_ISSUER, 'iat': now,
        'exp': now + timedelta(days=JWT_REFRESH_TOKEN_LIFETIME_DAYS),
    }, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], issuer=JWT_ISSUER,
            options={'require': ['exp', 'iat', 'sub', 'type', 'iss']},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='توکن منقضی شده است',
                            headers={'WWW-Authenticate': 'Bearer'})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='توکن نامعتبر است',
                            headers={'WWW-Authenticate': 'Bearer'})


def _get_active_user_from_subject(subject: object) -> User:
    try:
        user_id = int(subject)
        if user_id <= 0:
            raise ValueError
        return User.objects.get(pk=user_id, is_active=True)
    except (TypeError, ValueError, User.DoesNotExist):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='کاربر یافت نشد یا توکن نامعتبر است',
                            headers={'WWW-Authenticate': 'Bearer'})


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='احراز هویت لازم است',
                            headers={'WWW-Authenticate': 'Bearer'})
    payload = decode_token(credentials.credentials)
    if payload.get('type') != 'access':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='توکن دسترسی معتبر نیست',
                            headers={'WWW-Authenticate': 'Bearer'})
    return _get_active_user_from_subject(payload.get('sub'))


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='دسترسی مدیریت لازم است')
    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        if payload.get('type') != 'access':
            return None
        return _get_active_user_from_subject(payload.get('sub'))
    except HTTPException:
        return None
