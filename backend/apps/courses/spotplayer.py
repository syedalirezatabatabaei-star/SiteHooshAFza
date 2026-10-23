"""SpotPlayer server-to-server adapter.

Do not call this from the browser: SPOTPLAYER_API_KEY is a secret.
The API base URL and endpoint are configurable because SpotPlayer API
contracts can differ by merchant/account; verify them against the account docs.
"""
import os
import requests
from django.conf import settings


class SpotPlayerConfigurationError(RuntimeError):
    pass


class SpotPlayerAPIError(RuntimeError):
    pass


def create_license(*, name, course_id, watermark=None, payload=None):
    api_key = getattr(settings, 'SPOTPLAYER_API_KEY', '') or os.environ.get('SPOTPLAYER_API_KEY', '')
    base_url = (getattr(settings, 'SPOTPLAYER_BASE_URL', '') or os.environ.get('SPOTPLAYER_BASE_URL', '')).rstrip('/')
    endpoint = os.environ.get('SPOTPLAYER_LICENSE_ENDPOINT', '').strip()
    if not api_key or not base_url or not endpoint:
        raise SpotPlayerConfigurationError(
            'SPOTPLAYER_API_KEY, SPOTPLAYER_BASE_URL و SPOTPLAYER_LICENSE_ENDPOINT باید طبق مستندات حساب تنظیم شوند.'
        )
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    body = {'name': name, 'course': [str(course_id)]}
    if watermark:
        body['watermark'] = watermark
    if payload:
        body['payload'] = payload
    try:
        response = requests.post(
            base_url + endpoint,
            json=body,
            headers={'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'},
            timeout=(5, 20),
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise SpotPlayerAPIError('ارتباط با SpotPlayer ناموفق بود؛ جزئیات در لاگ سرور بررسی شود.') from exc
    if not isinstance(data, dict) or data.get('error') or data.get('ex'):
        raise SpotPlayerAPIError('SpotPlayer پاسخ موفق و قابل‌شناسایی برنگرداند.')
    return data
