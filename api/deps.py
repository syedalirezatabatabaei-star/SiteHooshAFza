from datetime import datetime, timedelta, timezone
from typing import Optional
from pathlib import Path

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from django.contrib.auth import get_user_model

# Load local config directly
BASE_DIR = Path(__file__).resolve().parent
config_path = BASE_DIR / 'config.py'

import importlib.util
spec = importlib.util.spec_from_file_location('api_config', config_path)
api_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_config)

JWT_SECRET_KEY = api_config.JWT_SECRET_KEY
JWT_ALGORITHM = api_config.JWT_ALGORITHM
JWT_ACCESS_TOKEN_LIFETIME_MINUTES = api_config.JWT_ACCESS_TOKEN_LIFETIME_MINUTES
JWT_REFRESH_TOKEN_LIFETIME_DAYS = api_config.JWT_REFRESH_TOKEN_LIFETIME_DAYS

User = get_user_model()
security = HTTPBearer(auto_error=False)


def create_access_token(user_id: int, phone_number: str, role: str) -> str:
    """Create JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_LIFETIME_MINUTES)
    payload = {
        'sub': str(user_id),
        'phone': phone_number,
        'role': role,
        'type': 'access',
        'exp': expire,
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """Create JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_LIFETIME_DAYS)
    payload = {
        'sub': str(user_id),
        'type': 'refresh',
        'exp': expire,
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='توکن منقضی شده است',
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='توکن نامعتبر است',
        )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> User:
    """Get current authenticated user from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='احراز هویت لازم است',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    payload = decode_token(credentials.credentials)
    if payload.get('type') != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='توکن نامعتبر است',
        )

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='توکن نامعتبر است',
        )

    try:
        user = User.objects.get(pk=int(user_id), is_active=True)
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='کاربر یافت نشد',
        )

    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """Get current user and verify admin role."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='دسترسی مدیریت لازم است',
        )
    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        if payload.get('type') != 'access':
            return None
        user_id = payload.get('sub')
        if not user_id:
            return None
        return User.objects.get(pk=int(user_id), is_active=True)
    except Exception:
        return None
