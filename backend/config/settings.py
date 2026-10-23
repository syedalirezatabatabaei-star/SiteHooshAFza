import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get('DEBUG', 'False').strip().lower() in ('true', '1', 'yes')
SECRET_KEY = os.environ.get('SECRET_KEY', '').strip()
if not SECRET_KEY or SECRET_KEY == 'django-insecure-dev-key-change-in-production':
    raise RuntimeError('SECRET_KEY must be set to a unique secret in the environment.')
if not DEBUG and len(SECRET_KEY) < 50:
    raise RuntimeError('Production SECRET_KEY must be at least 50 characters long.')

ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'apps.users', 'apps.courses', 'apps.enrollments', 'apps.orders', 'apps.payments',
    'apps.discounts', 'apps.exams', 'apps.certificates', 'apps.blog',
    'apps.notifications', 'apps.tickets', 'apps.reviews',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': os.environ.get('DB_NAME', 'hooshafza'),
    'USER': os.environ.get('DB_USER', 'hooshafza_user'),
    'PASSWORD': os.environ.get('DB_PASSWORD', 'hooshafza_pass'),
    'HOST': os.environ.get('DB_HOST', 'localhost'),
    'PORT': os.environ.get('DB_PORT', '3306'),
    'OPTIONS': {
        'charset': 'utf8mb4',
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION', default_storage_engine=INNODB",
    },
}}

AUTH_USER_MODEL = 'users.User'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fa'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.environ.get(
    'CORS_ALLOWED_ORIGINS', 'http://localhost,http://127.0.0.1'
).split(',') if origin.strip()]

SITE_DOMAIN = os.environ.get('SITE_DOMAIN', 'localhost')
SITE_NAME = os.environ.get('SITE_NAME', 'هوش افزا')
PAYMENT_GATEWAY = os.environ.get('PAYMENT_GATEWAY', 'ZARINPAL')
PAYMENT_API_KEY = os.environ.get('PAYMENT_API_KEY', '')
PAYMENT_MERCHANT_ID = os.environ.get('PAYMENT_MERCHANT_ID', '')
PAYMENT_CALLBACK_URL = os.environ.get(
    'PAYMENT_CALLBACK_URL',
    f"{'http' if SITE_DOMAIN in ('localhost', '127.0.0.1') else 'https'}://{SITE_DOMAIN}/api/v1/payments/callback",
)
SPOTPLAYER_API_KEY = os.environ.get('SPOTPLAYER_API_KEY', '')
SPOTPLAYER_BASE_URL = os.environ.get('SPOTPLAYER_BASE_URL', 'https://api.spotplayer.ir')

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', '').strip()
if not JWT_SECRET_KEY or JWT_SECRET_KEY == SECRET_KEY:
    raise RuntimeError('JWT_SECRET_KEY must be set and must differ from SECRET_KEY.')
if len(JWT_SECRET_KEY) < 32:
    raise RuntimeError('JWT_SECRET_KEY must be at least 32 characters long.')
JWT_ACCESS_TOKEN_LIFETIME_MINUTES = int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', '15'))
JWT_REFRESH_TOKEN_LIFETIME_DAYS = int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME_DAYS', '7'))

if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').strip().lower() in ('true', '1', 'yes')
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

CSRF_TRUSTED_ORIGINS = [f"https://{SITE_DOMAIN}", f"https://www.{SITE_DOMAIN}"]
if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend(['http://localhost', 'http://127.0.0.1',
                                f"http://{SITE_DOMAIN}", f"http://www.{SITE_DOMAIN}"])
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
