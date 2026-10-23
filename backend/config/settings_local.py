# Local development settings (SQLite for testing without MySQL)
import os
import sys
from pathlib import Path

# Get base dir from this file's location
BASE_DIR = Path(__file__).resolve().parent.parent

# Import settings as a module
sys.path.insert(0, str(BASE_DIR))
import config.settings as base_settings  # noqa: E402

# Re-export all base settings
globals().update({k: v for k, v in base_settings.__dict__.items() if not k.startswith('_')})

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Use SQLite for local development when MySQL is not available
DB_ENGINE = os.environ.get('DB_ENGINE', 'sqlite')

if DB_ENGINE == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Disable CSRF for API testing (use with caution!)
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
PAYMENT_GATEWAY = os.environ.get('PAYMENT_GATEWAY', 'MANUAL')

# Allow the local frontend preview origin (FastAPI reads CORS_ALLOWED_ORIGINS)
os.environ.setdefault(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:8080,http://127.0.0.1:8080,http://localhost,http://127.0.0.1'
)
