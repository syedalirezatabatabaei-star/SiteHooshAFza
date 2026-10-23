from fastapi import APIRouter, Depends, HTTPException

from deps import get_current_user
from schemas.v1.notifications import NotificationResponse, NotificationCountResponse
from apps.notifications.models import Notification

router = APIRouter()


@router.get('')
def list_notifications(user=Depends(get_current_user)):
    """لیست اعلان‌ها"""
    notifications = Notification.objects.filter(user=user)
    return [NotificationResponse(
        id=n.id, title=n.title, message=n.message,
        type=n.type, is_read=n.is_read, created_at=n.created_at,
    ) for n in notifications[:50]]


@router.get('/count', response_model=NotificationCountResponse)
def notification_count(user=Depends(get_current_user)):
    """تعداد اعلان‌ها"""
    total = Notification.objects.filter(user=user).count()
    unread = Notification.objects.filter(user=user, is_read=False).count()
    return NotificationCountResponse(total=total, unread=unread)


@router.put('/{notification_id}/read')
def mark_read(notification_id: int, user=Depends(get_current_user)):
    """علامت‌گذاری اعلان به عنوان خوانده شده"""
    try:
        notification = Notification.objects.get(pk=notification_id, user=user)
    except Notification.DoesNotExist:
        raise HTTPException(status_code=404, detail='اعلان یافت نشد')

    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return {'message': 'اعلان خوانده شد'}


@router.put('/read-all')
def mark_all_read(user=Depends(get_current_user)):
    """علامت‌گذاری همه اعلان‌ها به عنوان خوانده شده"""
    updated = Notification.objects.filter(user=user, is_read=False).update(is_read=True)
    return {'message': f'{updated} اعلان خوانده شد'}
