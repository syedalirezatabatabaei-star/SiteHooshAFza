import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Local apps
    'apps.users',
    'apps.courses',
    'apps.enrollments',
    'apps.orders',
    'apps.payments',
    'apps.discounts',
    'apps.exams',
    'apps.certificates',
    'apps.blog',
    'apps.notifications',
    'apps.tickets',
    'apps.reviews',
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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'hooshafza'),
        'USER': os.environ.get('DB_USER', 'hooshafza_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'hooshafza_pass'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            # MySQL 5.7.x: utf8mb4 + InnoDB so unique slug indexes (up to 300
            # chars) stay under the 3072-byte large-prefix limit.
            'charset': 'utf8mb4',
            'init_command': (
                "SET sql_mode='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION',"
                " default_storage_engine=INNODB"
            ),
        },
    }
}

# Auth
AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'fa'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS', 'http://localhost,http://127.0.0.1'
).split(',')

# Site
SITE_DOMAIN = os.environ.get('SITE_DOMAIN', 'localhost')
SITE_NAME = os.environ.get('SITE_NAME', 'هوش افزا')

# Payment Gateway
PAYMENT_GATEWAY = os.environ.get('PAYMENT_GATEWAY', 'ZARINPAL')
PAYMENT_API_KEY = os.environ.get('PAYMENT_API_KEY', '')
PAYMENT_MERCHANT_ID = os.environ.get('PAYMENT_MERCHANT_ID', '')
PAYMENT_CALLBACK_URL = os.environ.get(
    'PAYMENT_CALLBACK_URL',
    f"{'http' if SITE_DOMAIN in ('localhost', '127.0.0.1') else 'https'}://{SITE_DOMAIN}/api/v1/payments/callback",
)

# SpotPlayer
SPOTPLAYER_API_KEY = os.environ.get('SPOTPLAYER_API_KEY', '')
SPOTPLAYER_BASE_URL = os.environ.get('SPOTPLAYER_BASE_URL', 'https://api.spotplayer.ir')

# JWT Settings
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
JWT_ACCESS_TOKEN_LIFETIME_MINUTES = int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', '60'))
JWT_REFRESH_TOKEN_LIFETIME_DAYS = int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME_DAYS', '7'))

# Security
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_SSL_REDIRECT = False  # Set to True if using HTTPS and want to redirect HTTP to HTTPS
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# CSRF Settings - Required for admin panel to work
CSRF_TRUSTED_ORIGINS = [
    f"https://{SITE_DOMAIN}",
    f"https://www.{SITE_DOMAIN}",
]
if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        "http://localhost",
        "http://127.0.0.1",
    ])
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    # Disable CSRF for debug mode to fix admin access issues
    CSRF_COOKIE_SECURE = False
    # Add both HTTP and HTTPS for debug
    CSRF_TRUSTED_ORIGINS.extend([
        f"http://{SITE_DOMAIN}",
        f"http://www.{SITE_DOMAIN}",
    ])

# #region agent log
def _agent_dbg_mysql57():
    try:
        import json
        import time
        import django
        log_path = os.environ.get('DEBUG_LOG_PATH')
        if not log_path:
            return
        payload = {
            'sessionId': '267002',
            'hypothesisId': 'A',
            'location': 'backend/config/settings.py',
            'message': 'django_settings_loaded',
            'data': {
                'django_version': django.get_version(),
                'django_major': django.VERSION[0],
                'db_host': os.environ.get('DB_HOST', ''),
                'db_engine': DATABASES['default']['ENGINE'],
                'charset': DATABASES['default'].get('OPTIONS', {}).get('charset'),
            },
            'timestamp': int(time.time() * 1000),
        }
        with open(log_path, 'a', encoding='utf-8') as handle:
            handle.write(json.dumps(payload) + '\n')
    except Exception:
        pass


_agent_dbg_mysql57()
# #endregion
