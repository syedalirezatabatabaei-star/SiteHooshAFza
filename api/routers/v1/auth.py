from fastapi import APIRouter, Depends, HTTPException, status
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from deps import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from schemas.v1.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    ChangePasswordRequest,
    UserInfo,
)
from schemas.v1.users import UserProfileResponse, UserProfileUpdateRequest

User = get_user_model()
router = APIRouter()


def user_to_info(user) -> UserInfo:
    return UserInfo(
        id=user.id,
        phone_number=user.phone_number,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.role,
        profile_image=user.profile_image.url if user.profile_image else None,
    )


@router.post('/register', response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    """ثبت‌نام کاربر جدید"""
    try:
        user = User.objects.create_user(
            phone_number=data.phone_number,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='شماره تلفن قبلاً ثبت شده است',
        )

    access_token = create_access_token(user.id, user.phone_number, user.role)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_to_info(user),
    )


@router.post('/login', response_model=TokenResponse)
def login(data: LoginRequest):
    """ورود کاربر"""
    try:
        user = User.objects.get(phone_number=data.phone_number)
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='شماره تلفن یا رمز عبور اشتباه است',
        )

    if not user.check_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='شماره تلفن یا رمز عبور اشتباه است',
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='حساب کاربری غیرفعال است',
        )

    access_token = create_access_token(user.id, user.phone_number, user.role)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_to_info(user),
    )


@router.post('/refresh', response_model=dict)
def refresh_token(data: RefreshRequest):
    """بازیابی توکن"""
    payload = decode_token(data.refresh_token)
    if payload.get('type') != 'refresh':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='توکن نامعتبر است',
        )

    user_id = int(payload.get('sub'))
    try:
        user = User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='کاربر یافت نشد',
        )

    access_token = create_access_token(user.id, user.phone_number, user.role)
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/me', response_model=UserInfo)
def get_me(user=Depends(get_current_user)):
    """دریافت اطلاعات کاربر جاری"""
    return user_to_info(user)


@router.put('/me', response_model=UserInfo)
def update_me(
    data: UserProfileUpdateRequest,
    user=Depends(get_current_user),
):
    """به‌روزرسانی اطلاعات کاربر جاری"""
    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name
    if data.email is not None:
        user.email = data.email
    user.save()
    return user_to_info(user)


@router.post('/change-password')
def change_password(
    data: ChangePasswordRequest,
    user=Depends(get_current_user),
):
    """تغییر رمز عبور"""
    if not user.check_password(data.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='رمز عبور فعلی اشتباه است',
        )
    user.set_password(data.new_password)
    user.save()
    return {'message': 'رمز عبور با موفقیت تغییر کرد'}
