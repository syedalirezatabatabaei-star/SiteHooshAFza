from fastapi import APIRouter, Depends, HTTPException, status

from deps import get_current_user, get_current_admin
from schemas.v1.tickets import (
    TicketCreateRequest, TicketResponse, TicketDetailResponse,
    TicketReplyRequest, TicketUpdateStatusRequest, TicketMessageResponse,
)
from apps.tickets.models import Ticket, TicketMessage
from apps.notifications.models import Notification

router = APIRouter()


@router.get('')
def list_tickets(user=Depends(get_current_user)):
    """لیست تیکت‌های کاربر"""
    tickets = Ticket.objects.filter(user=user)
    result = []
    for t in tickets:
        last_msg = t.messages.order_by('-created_at').first()
        result.append(TicketResponse(
            id=t.id, subject=t.subject, status=t.status,
            priority=t.priority, created_at=t.created_at,
            updated_at=t.updated_at,
            message_count=t.messages.count(),
            last_message=last_msg.message[:100] if last_msg else None,
        ))
    return result


@router.post('', response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(data: TicketCreateRequest, user=Depends(get_current_user)):
    """ایجاد تیکت جدید"""
    ticket = Ticket.objects.create(
        user=user,
        subject=data.subject,
        priority=data.priority,
    )
    TicketMessage.objects.create(
        ticket=ticket,
        sender=user,
        message=data.message,
    )

    return TicketResponse(
        id=ticket.id, subject=ticket.subject, status=ticket.status,
        priority=ticket.priority, created_at=ticket.created_at,
        updated_at=ticket.updated_at, message_count=1,
        last_message=data.message[:100],
    )


@router.get('/{ticket_id}')
def get_ticket(ticket_id: int, user=Depends(get_current_user)):
    """جزئیات تیکت"""
    try:
        ticket = Ticket.objects.get(pk=ticket_id, user=user)
    except Ticket.DoesNotExist:
        raise HTTPException(status_code=404, detail='تیکت یافت نشد')

    messages = []
    for msg in ticket.messages.select_related('sender').order_by('created_at'):
        messages.append(TicketMessageResponse(
            id=msg.id, sender_id=msg.sender_id,
            sender_name=msg.sender.full_name,
            message=msg.message, is_read=msg.is_read,
            created_at=msg.created_at,
        ))

    return TicketDetailResponse(
        id=ticket.id, subject=ticket.subject, status=ticket.status,
        priority=ticket.priority, messages=messages,
        created_at=ticket.created_at, updated_at=ticket.updated_at,
    )


@router.post('/{ticket_id}/reply')
def reply_ticket(
    ticket_id: int,
    data: TicketReplyRequest,
    user=Depends(get_current_user),
):
    """پاسخ به تیکت"""
    try:
        ticket = Ticket.objects.get(pk=ticket_id, user=user)
    except Ticket.DoesNotExist:
        raise HTTPException(status_code=404, detail='تیکت یافت نشد')

    if ticket.status == 'CLOSED':
        raise HTTPException(status_code=400, detail='تیکت بسته شده است')

    msg = TicketMessage.objects.create(
        ticket=ticket,
        sender=user,
        message=data.message,
    )

    ticket.status = 'IN_PROGRESS'
    ticket.save(update_fields=['status', 'updated_at'])

    # Notify admins
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admins = User.objects.filter(role='ADMIN', is_active=True)
    for admin in admins:
        Notification.objects.create(
            user=admin,
            title=f'پاسخ جدید به تیکت: {ticket.subject}',
            message=f'{user.full_name}: {data.message[:200]}',
            type='INFO',
        )

    return {'message': 'پاسخ ارسال شد'}


@router.put('/{ticket_id}/status')
def update_ticket_status(
    ticket_id: int,
    data: TicketUpdateStatusRequest,
    user=Depends(get_current_user),
):
    """تغییر وضعیت تیکت"""
    try:
        ticket = Ticket.objects.get(pk=ticket_id, user=user)
    except Ticket.DoesNotExist:
        raise HTTPException(status_code=404, detail='تیکت یافت نشد')

    valid_statuses = ['CLOSED']
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail='وضعیت نامعتبر')

    ticket.status = data.status
    ticket.save(update_fields=['status', 'updated_at'])
    return {'message': 'وضعیت تیکت به‌روزرسانی شد'}
