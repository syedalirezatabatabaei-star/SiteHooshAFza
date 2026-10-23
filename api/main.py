"""
Run this file to start the API server:
    cd api && python main.py [--port PORT]
"""
import os
import sys
from pathlib import Path

# Setup paths to find Django config
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR.parent / 'backend'

# In Docker, backend is mounted at /backend, not relative to api
if os.environ.get('IN_DOCKER') == '1':
    BACKEND_DIR = Path('/backend')
    # Add /backend to sys.path so we can import backend.config.settings
    sys.path.insert(0, str(BACKEND_DIR))
    sys.path.insert(0, str(BACKEND_DIR.parent))  # For import backend.config
else:
    sys.path.insert(0, str(BACKEND_DIR))
    sys.path.insert(0, str(BASE_DIR))

# Parse port argument
port = int(sys.argv[sys.argv.index('--port') + 1]) if '--port' in sys.argv else 8000

# Setup Django ORM before importing anything else.
# Production (Docker): the API container imports backend/config/settings.py directly
# via sys.path so Django uses the same MySQL as the backend container.
# Local dev: DB_ENGINE=sqlite in settings_local.py when run outside Docker.
import importlib.util

if os.environ.get('IN_DOCKER') == '1':
    # Docker/production path: use the real settings module
    os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.config.settings'
elif (BACKEND_DIR / 'config' / 'settings.py').exists() and os.environ.get('DB_ENGINE') != 'sqlite':
    # Production path outside Docker
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
else:
    # Local dev path: lightweight settings_local shim
    spec = importlib.util.spec_from_file_location(
        'settings_local',
        str(BACKEND_DIR / 'config' / 'settings_local.py')
    )
    settings_local = importlib.util.module_from_spec(spec)
    sys.modules['backend.settings_local'] = settings_local
    spec.loader.exec_module(settings_local)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings_local'

import django
django.setup()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from django.conf import settings as django_settings

from routers.v1 import auth, courses, instructors, blog, search
from routers.v1 import cart, orders, payments, enrollments, exams, certificates
from routers.v1 import notifications, tickets, reviews, users, admin_panel

app = FastAPI(
    title="هوش افزا API",
    description="API for Hooshafza Educational Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Uploaded course and instructor images must be reachable in both local and Docker setups.
media_directory = Path('/app/media') if BACKEND_DIR == Path('/backend') else Path(django_settings.MEDIA_ROOT)
media_directory.mkdir(parents=True, exist_ok=True)
app.mount('/media', StaticFiles(directory=str(media_directory), check_dir=False), name='media')

# CORS
cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost,http://127.0.0.1').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# V1 Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["احراز هویت"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["دوره‌ها"])
app.include_router(instructors.router, prefix="/api/v1/instructors", tags=["مدرسین"])
app.include_router(blog.router, prefix="/api/v1/articles", tags=["مقالات"])
app.include_router(search.router, prefix="/api/v1/search", tags=["جستجو"])
app.include_router(cart.router, prefix="/api/v1/cart", tags=["سبد خرید"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["سفارشات"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["پرداخت"])
app.include_router(enrollments.router, prefix="/api/v1/enrollments", tags=["ثبت‌نام‌ها"])
app.include_router(exams.router, prefix="/api/v1/exams", tags=["آزمون‌ها"])
app.include_router(certificates.router, prefix="/api/v1/certificates", tags=["گواهینامه‌ها"])
app.include_router(users.router, prefix="/api/v1/users", tags=["کاربر"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["اعلان‌ها"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["تیکت‌ها"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["نظرات"])
app.include_router(admin_panel.router, prefix="/api/v1/admin", tags=["پنل مدیریت"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "هوش افزا API در حال اجراست"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=port)
