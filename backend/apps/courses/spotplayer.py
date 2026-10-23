"""Server-side SpotPlayer adapter.

The request format follows the public spotplayer PHP client as a compatibility
reference. Confirm endpoint, headers, response keys and device/watermark rules
against the merchant's current official account documentation before production.
"""
import os
import requests
from django.conf import settings


class SpotPlayerConfigurationError(RuntimeError):
    pass


class SpotPlayerAPIError(RuntimeError):
    pass


def create_license(*, name, course_id, watermark_text=None):
    api_key = getattr(settings, 'SPOTPLAYER_API_KEY', '') or os.environ.get('SPOTPLAYER_API_KEY', '')
    base_url = (os.environ.get('SPOTPLAYER_BASE_URL') or getattr(settings, 'SPOTPLAYER_BASE_URL', '') or 'https://panel.spotplayer.ir').rstrip('/')
    endpoint = os.environ.get('SPOTPLAYER_LICENSE_ENDPOINT', '/license/edit/').strip()
    if not api_key:
        raise SpotPlayerConfigurationError('SPOTPLAYER_API_KEY تنظیم نشده است.')
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    try:
        device_limit = max(1, min(99, int(os.environ.get('SPOTPLAYER_DEVICE_LIMIT', '2'))))
    except ValueError:
        device_limit = 2
    body = {
        'test': os.environ.get('SPOTPLAYER_MODE', 'test').lower() == 'test',
        'name': name,
        'course': [str(course_id)],
        'watermark': {'texts': [{'text': watermark_text}]} if watermark_text else {'texts': []},
        'device': {
            'p0': device_limit, 'p1': 0, 'p2': 0, 'p3': 0,
            'p4': 0, 'p5': 0, 'p6': 0,
        },
    }
    try:
        response = requests.post(
            base_url + endpoint,
            json=body,
            headers={'$API': api_key, '$LEVEL': '-1', 'Content-Type': 'application/json'},
            timeout=(5, 20),
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise SpotPlayerAPIError('ارتباط با SpotPlayer ناموفق بود؛ لاگ سرور را بررسی کنید.') from exc
    if not isinstance(data, dict) or data.get('ex') or not data.get('_id'):
        raise SpotPlayerAPIError('پاسخ SpotPlayer شناسه لایسنس معتبر نداشت.')
    return data


def issue_license_for_order_item(order_item):
    """Issue once per purchased recorded course; safe to retry from admin."""
    from django.db import transaction
    from .models import SpotPlayerLicense

    course = order_item.course
    if not course.is_recorded or not course.spotplayer_course_id:
        return None
    record, _ = SpotPlayerLicense.objects.get_or_create(order_item=order_item)
    if record.status == 'CREATED':
        return record
    user = order_item.order.user
    display_name = (getattr(user, 'full_name', '') or f'{user.first_name} {user.last_name}').strip()
    watermark = f'{display_name} | {user.phone_number}'
    try:
        result = create_license(
            name=display_name or user.phone_number,
            course_id=course.spotplayer_course_id,
            watermark_text=watermark,
        )
        record.external_license_id = str(result.get('_id', ''))
        record.license_key = str(result.get('key', ''))
        record.license_url = str(result.get('url', ''))
        record.provider_response = result
        record.status = 'CREATED'
        record.error_message = ''
    except (SpotPlayerConfigurationError, SpotPlayerAPIError) as exc:
        record.status = 'FAILED'
        record.error_message = str(exc)
    with transaction.atomic():
        record.save()
    return record
