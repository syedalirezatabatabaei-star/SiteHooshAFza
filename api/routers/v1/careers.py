from fastapi import APIRouter, Depends, HTTPException, Request
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from deps import get_current_admin
from apps.careers.models import CareerApplication
from schemas.v1.careers import CareerApplicationCreate, CareerApplicationUpdate

router = APIRouter()


@router.post('/applications', status_code=201)
def submit_application(data: CareerApplicationCreate, request: Request):
    if data.application_type not in {'INSTITUTE', 'SUBSIDIARY', 'JOB'}:
        raise HTTPException(status_code=422, detail='نوع درخواست معتبر نیست')
    # Basic per-client throttling is expected at the reverse proxy; never trust
    # forwarded IP headers unless Nginx is configured to overwrite them.
    phone = ''.join(ch for ch in data.phone if ch.isdigit() or ch == '+')
    if len(phone) < 7:
        raise HTTPException(status_code=422, detail='شماره تماس معتبر نیست')
    resume_url = data.resume_url or ''
    if resume_url:
        try:
            URLValidator(schemes=['https', 'http'])(resume_url)
        except ValidationError:
            raise HTTPException(status_code=422, detail='لینک رزومه معتبر نیست')
    item = CareerApplication.objects.create(
        application_type=data.application_type,
        full_name=data.full_name.strip(),
        phone=phone,
        email=str(data.email or ''),
        organization=data.organization.strip(),
        position=data.position.strip(),
        message=data.message.strip(),
        resume_url=resume_url,
    )
    return {'id': item.id, 'status': item.status, 'message': 'درخواست شما ثبت شد.'}


@router.get('/applications')
def list_applications(status: str = None, application_type: str = None, admin=Depends(get_current_admin)):
    qs = CareerApplication.objects.all()
    if status:
        qs = qs.filter(status=status)
    if application_type:
        qs = qs.filter(application_type=application_type)
    return [{
        'id': x.id, 'application_type': x.application_type, 'full_name': x.full_name,
        'phone': x.phone, 'email': x.email, 'organization': x.organization,
        'position': x.position, 'message': x.message, 'resume_url': x.resume_url,
        'status': x.status, 'admin_notes': x.admin_notes, 'created_at': x.created_at,
    } for x in qs[:500]]


@router.patch('/applications/{application_id}')
def update_application(application_id: int, data: CareerApplicationUpdate, admin=Depends(get_current_admin)):
    if data.status not in {'NEW', 'REVIEWING', 'CONTACTED', 'REJECTED'}:
        raise HTTPException(status_code=422, detail='وضعیت درخواست معتبر نیست')
    try:
        item = CareerApplication.objects.get(pk=application_id)
    except CareerApplication.DoesNotExist:
        raise HTTPException(status_code=404, detail='درخواست یافت نشد')
    item.status = data.status
    item.admin_notes = data.admin_notes
    item.save(update_fields=['status', 'admin_notes'])
    return {'id': item.id, 'status': item.status, 'message': 'درخواست به‌روزرسانی شد.'}
