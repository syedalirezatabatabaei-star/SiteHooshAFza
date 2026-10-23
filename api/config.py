import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR.parent / 'backend'

# JWT Config
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', os.environ.get('SECRET_KEY', 'jwt-secret-dev'))
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_LIFETIME_MINUTES = int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', '60'))
JWT_REFRESH_TOKEN_LIFETIME_DAYS = int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME_DAYS', '7'))
