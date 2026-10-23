from fastapi import APIRouter, Depends

from deps import get_current_user
from schemas.v1.users import UserProfileResponse, UserProfileUpdateRequest

router = APIRouter()


@router.get('/me', response_model=UserProfileResponse)
def get_my_profile(user=Depends(get_current_user)):
    """دریافت پروفایل کاربر جاری"""
    return _serialize(user)


@router.put('/me', response_model=UserProfileResponse)
def update_my_profile(
    data: UserProfileUpdateRequest,
    user=Depends(get_current_user),
):
    """به‌روزرسانی پروفایل کاربر جاری"""
    return _apply_update(data, user)


def _serialize(user):
    return UserProfileResponse(
        id=user.id,
        phone_number=user.phone_number,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.role,
        profile_image=user.profile_image.url if user.profile_image else None,
        date_joined=user.date_joined,
    )


def _apply_update(data, user):
    """به‌روزرسانی پروفایل"""
    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name
    if data.email is not None:
        user.email = data.email
    user.save()

    return _serialize(user)
