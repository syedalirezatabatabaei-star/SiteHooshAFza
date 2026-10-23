import os

# JWT uses a dedicated signing key; never fall back to Django SECRET_KEY.
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', '').strip()
DEBUG = os.environ.get('DEBUG', 'False').strip().lower() in ('true', '1', 'yes')
if not JWT_SECRET_KEY or JWT_SECRET_KEY == 'jwt-secret-dev' or JWT_SECRET_KEY == os.environ.get('SECRET_KEY', ''):
    raise RuntimeError('Set a dedicated JWT_SECRET_KEY; insecure fallback keys are disabled.')
if len(JWT_SECRET_KEY) < 32:
    raise RuntimeError('JWT_SECRET_KEY must be at least 32 characters long.')

JWT_ALGORITHM = 'HS256'
JWT_ISSUER = os.environ.get('JWT_ISSUER', 'hooshafza-api')
JWT_ACCESS_TOKEN_LIFETIME_MINUTES = int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', '15'))
JWT_REFRESH_TOKEN_LIFETIME_DAYS = int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME_DAYS', '7'))
