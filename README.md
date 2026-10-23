<<<<<<< HEAD
# 🧠 هوش افزا — Hooshafza Educational Platform

> مؤسسه علمی، آموزشی و پژوهشی هوش افزا — یک پلتفرم آموزشی کامل و Production-Ready

---

## 📋 فهرست مطالب

- [معرفی پروژه](#معرفی-پروژه)
- [ویژگی‌های اصلی](#ویژگی‌های-اصلی)
- [معماری سیستم](#معماری-سیستم)
- [ساختار پروژه](#ساختار-پروژه)
- [پیش‌نیازها](#پیش‌نیازها)
- [متغیرهای محیطی](#متغیرهای-محیطی)
- [نصب و اجرای Docker](#نصب-و-اجرای-docker)
- [سیستم کاربران](#سیستم-کاربران)
- [سیستم دوره‌ها](#سیستم-دوره‌ها)
- [سیستم پرداخت](#سیستم-پرداخت)
- [سیستم آزمون](#سیستم-آزمون)
- [سیستم گواهینامه](#سیستم-گواهینامه)
- [سیستم وبلاگ](#سیستم-وبلاگ)
- [سیستم پشتیبانی](#سیستم-پشتیبانی)
- [پنل مدیریت](#پنل-مدیریت)
- [داشبورد دانشجو](#داشبورد-دانشجو)
- [API Documentation](#api-documentation)
- [Frontend](#frontend)
- [SEO](#seo)
- [امنیت](#امنیت)
- [تست‌ها](#تست‌ها)
- [Production Deployment](#production-deployment)
- [بکاپ و بازیابی](#بکاپ-و-بازیابی)
- [عیب‌یابی](#عیب‌یابی)

---

## 📖 معرفی پروژه

**هوش افزا** یک پلتفرم جامع آموزشی آنلاین است که برای مؤسسات علمی، آموزشی و پژوهشی طراحی شده است. این سیستم تمام نیازهای یک مرکز آموزشی حرفه‌ای را برآورده می‌کند، از ثبت‌نام دانشجو تا صدور گواهینامه.

### هدف پروژه

- ارائه دوره‌های حضوری و ضبط‌شده با کیفیت بالا
- مدیریت کامل دانشجویان، مدرسین و دوره‌ها
- پرداخت امن آنلاین با پشتیبانی از درگاه‌های مختلف
- آزمون آنلاین و صدور خودکار گواهینامه
- وبلاگ و مقالات آموزشی
- سیستم تیکت پشتیبانی
- پنل مدیریت قدرتمند
- طراحی ریسپانسیو و سازگار با موبایل
- پشتیبانی کامل از زبان فارسی و RTL

---

## ✨ ویژگی‌های اصلی

### 🎓 سیستم آموزشی
- **دوره‌های حضوری:** با مدیریت ظرفیت، زمان‌بندی، و پیش‌پرداخت
- **دوره‌های ضبط‌شده:** با سرفصل‌بندی، ویدئوهای SpotPlayer، و پیگیری پیشرفت
- **آزمون آنلاین:** سؤالات چندگزینه‌ای، نمره‌دهی خودکار، حد نصاب
- **گواهینامه:** صدور خودکار پس از اتمام دوره و قبولی در آزمون

### 💳 سیستم مالی
- **سبد خرید:** افزودن چند دوره، محاسبه خودکار قیمت
- **کدهای تخفیف:** درصدی یا مبلغ ثابت، محدودیت زمانی و تعداد
- **پرداخت:** درگاه‌های متعدد (Zarinpal و سایرین)
- **فاکتور:** صدور خودکار فاکتور

### 👥 مدیریت کاربران
- **ثبت‌نام با شماره موبایل:** احراز هویت امن
- **نقش‌ها:** دانشجو و مدیر
- **پروفایل:** مدیریت اطلاعات شخصی
- **اعلان‌ها:** اطلاع‌رسانی به کاربران

### 📝 وبلاگ
- **مقالات:** با دسته‌بندی و برچسب
- **SEO:** متا تگ‌ها، Schema.org، sitemap
- **دیدگاه‌ها:** نظرات کاربران

### 🎫 پشتیبانی
- **تیکت:** ایجاد و پاسخ به تیکت‌ها
- **وضعیت:** باز، در حال بررسی، پاسخ داده شده، بسته شده

---

## 🏗 معماری سیستم

```
┌─────────────────────────────────────────────────────────┐
│                      کاربر نهایی                        │
│                    (Browser/Mobile)                     │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│           Nginx (کانتینر فرانت‌اند — پورت 80/443)         │
│                                                         │
│   /            →  فایل‌های استاتیک HTML/CSS/JS           │
│   /api/        →  پروکسی به FastAPI   (hooshafza-api)   │
│   /docs        →  پروکسی به FastAPI   (hooshafza-api)   │
│   /admin/      →  پروکسی به Django    (hooshafza-backend)│
└─────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │  FastAPI    │  │   Django    │  │  MySQL 8.0  │
   │  :8000      │  │   :8001     │  │  :3306      │
   │ (loopback)  │  │ (loopback)  │  │ (loopback)  │
   └─────────────┘  └─────────────┘  └─────────────┘
```

### توضیح معماری

- **Nginx (Port 80/443):** نقطه ورود تنها سرور به اینترنت است. فایل‌های استاتیک را با کش و gzip سرو می‌کند و درخواست‌های `/api/` و `/admin/` را به کانتینرهای داخلی پروکسی می‌کند.
- **FastAPI (Port 8000):** لایه API که تمام درخواست‌های REST را مدیریت می‌کند. احراز هویت JWT، validation داده‌ها، و منطق کسب‌وکار را اجرا می‌کند. فقط روی loopback در دسترس است.
- **Django (Port 8001):** لایه مدل و ORM که با دیتابیس ارتباط برقرار می‌کند. همچنین Django Admin برای مدیریت داخلی سیستم فراهم می‌کند. فقط روی loopback در دسترس است.
- **MySQL (Port 3306):** پایگاه داده اصلی با تمام جداول و روابط. فقط روی loopback در دسترس است.

### مزایای معماری Nginx

- **امنیت:** فقط Nginx به اینترنت exposure دارد؛ FastAPI/Django/MySQL روی loopback هستند
- **یک دامنه:** سایت، API و ادمین همه زیر یک دامنه (بدون مشکل CORS)
- **HTTPS متمرکز:** گواهی SSL فقط روی Nginx نصب می‌شود
- **کش و فشرده‌سازی:** فایل‌های استاتیک با gzip و کش ۳۰ روزه سرو می‌شوند

---

## 📁 ساختار پروژه

```
hooshafza/
│
├── backend/                    # پروژه Django
│   ├── manage.py               # اسکریپت مدیریت Django
│   ├── config/                 # تنظیمات، URL‌ها، WSGI
│   │   ├── __init__.py
│   │   ├── settings.py         # تنظیمات اصلی پروژه
│   │   ├── urls.py             # URL‌های اصلی
│   │   └── wsgi.py             # WSGI entry point
│   │
│   ├── apps/                   # اپلیکیشن‌های Django
│   │   ├── users/              # مدل کاربر سفارشی (احراز هویت با شماره موبایل)
│   │   │   ├── models.py       # مدل CustomUser با نقش‌ها
│   │   │   ├── admin.py        # تنظیمات Django Admin
│   │   │   └── apps.py         # تنظیمات اپلیکیشن
│   │   │
│   │   ├── courses/            # دوره‌ها، فصل‌ها، درس‌ها
│   │   │   ├── models.py       # مدل‌های Course, Chapter, Lesson, Schedule
│   │   │   ├── admin.py        # مدیریت دوره‌ها در Admin
│   │   │   └── apps.py
│   │   │
│   │   ├── enrollments/        # ثبت‌نام دانشجویان
│   │   │   ├── models.py       # مدل Enrollment با وضعیت و پیشرفت
│   │   │   ├── admin.py
│   │   │   └── apps.py
│   │   │
│   │   ├── orders/             # سبد خرید و سفارشات
│   │   │   ├── models.py       # مدل‌های Cart, CartItem, Order, OrderItem
│   │   │   ├── admin.py
│   │   │   └── apps.py
│   │   │
│   │   ├── payments/           # پرداخت‌ها
│   │   │   ├── models.py       # مدل Payment با وضعیت‌ها
│   │   │   ├── admin.py
│   │   │   └── apps.py
│   │   │
│   │   ├── discounts/          # سیستم تخفیف
│   │   │   ├── models.py       # مدل Coupon با محدودیت‌ها
│   │   │   ├── admin.py
│   │   │   └── apps.py
│   │   │
│   │   ├── exams/              # آزمون‌ها
│   │   │   ├── models.py       # مدل‌های Exam, Question, Choice, ExamAttempt
│   │   │   ├── admin.py
│   │   │   └── apps.py
│   │   │
│   │   ├── certificates/       # گواهینامه‌ها
│   │   │   ├── models.py       # مدل Certificate با کد تأیید
│   │   │   ├── admin.py
│   │   │   └── apps.py
│   │   │
│   │   ├── blog/               # وبلاگ و مقالات
│   │   │   ├── models.py       # مدل‌های Article, BlogCategory, Tag
│   │   │   ├── admin.py
│   │   │   └── apps.py
│   │   │
│   │   ├── notifications/      # اعلان‌ها
│   │   │   ├── models.py       # مدل Notification
│   │   │   ├── admin.py
│   │   │   └── apps.py
│   │   │
│   │   ├── tickets/            # سیستم تیکت پشتیبانی
│   │   │   ├── models.py       # مدل‌های Ticket, TicketMessage
│   │   │   ├── admin.py
│   │   │   └── apps.py
│   │   │
│   │   └── reviews/            # نظرات و بررسی‌ها
│   │       ├── models.py       # مدل Review با وضعیت تأیید
│   │       ├── admin.py
│   │       └── apps.py
│   │
│   ├── requirements.txt        # وابستگی‌های Python
│   ├── Dockerfile              # فایل Docker برای Backend
│   └── migrations/             # مایگریشن‌های Django
│
├── api/                        # پروژه FastAPI
│   ├── main.py                 # نقطه ورودی اپلیکیشن
│   ├── config.py               # تنظیمات JWT و اپلیکیشن
│   ├── deps.py                 # وابستگی‌های احراز هویت
│   │
│   ├── routers/v1/             # مسیرهای API
│   │   ├── auth.py             # احراز هویت (ورود/ثبت‌نام)
│   │   ├── courses.py          # مدیریت دوره‌ها
│   │   ├── instructors.py      # مدرسین
│   │   ├── blog.py             # مقالات وبلاگ
│   │   ├── search.py           # جستجو
│   │   ├── cart.py             # سبد خرید
│   │   ├── orders.py           # سفارشات
│   │   ├── payments.py         # پرداخت‌ها
│   │   ├── enrollments.py      # ثبت‌نام‌ها
│   │   ├── exams.py            # آزمون‌ها
│   │   ├── certificates.py     # گواهینامه‌ها
│   │   ├── notifications.py    # اعلان‌ها
│   │   ├── tickets.py          # تیکت‌ها
│   │   ├── reviews.py          # نظرات
│   │   ├── users.py            # پروفایل کاربر
│   │   └── admin_panel.py      # پنل مدیریت
│   │
│   ├── schemas/v1/             # اسکیماهای Pydantic
│   │   ├── auth.py
│   │   ├── courses.py
│   │   ├── cart.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   ├── enrollments.py
│   │   ├── exams.py
│   │   ├── certificates.py
│   │   ├── blog.py
│   │   ├── notifications.py
│   │   ├── tickets.py
│   │   ├── reviews.py
│   │   ├── users.py
│   │   └── admin_panel.py
│   │
│   ├── services/               # لایه سرویس (منطق کسب‌وکار)
│   │   └── __init__.py
│   │
│   ├── dependencies/           # وابستگی‌های مشترک
│   │   └── __init__.py
│   │
│   ├── requirements.txt        # وابستگی‌های Python
│   └── Dockerfile              # فایل Docker برای API
│
├── frontend/                   # فرانت‌اند استاتیک
│   ├── index.html              # صفحه اصلی
│   │
│   ├── pages/                  # صفحات مختلف
│   │   ├── courses.html        # لیست دوره‌ها
│   │   ├── course-detail.html  # جزئیات دوره
│   │   ├── instructors.html    # مدرسین
│   │   ├── blog.html           # وبلاگ
│   │   ├── article-detail.html # جزئیات مقاله
│   │   ├── login.html          # ورود
│   │   ├── register.html       # ثبت‌نام
│   │   ├── cart.html           # سبد خرید
│   │   ├── dashboard.html      # داشبورد دانشجو
│   │   ├── admin-dashboard.html # پنل مدیریت
│   │   ├── about.html          # درباره ما
│   │   ├── contact.html        # تماس
│   │   ├── faq.html            # سؤالات متداول
│   │   ├── terms.html          # قوانین
│   │   ├── privacy.html        # حریم خصوصی
│   │   └── 404.html            # صفحه یافت نشد
│   │
│   ├── css/                    # استایل‌شیت‌ها
│   │   ├── variables.css       # متغیرهای CSS
│   │   ├── base.css            # استایل‌های پایه
│   │   ├── components.css      # کامپوننت‌ها
│   │   ├── layout.css          # لایوت
│   │   ├── pages.css           # استایل صفحات
│   │   ├── dashboard.css       # استایل داشبورد
│   │   └── admin.css           # استایل پنل مدیریت
│   │
│   ├── js/                     # ماژول‌های JavaScript
│   │   ├── api.js              # ارتباط با API
│   │   ├── auth.js             # احراز هویت
│   │   ├── utils.js            # توابع کمکی
│   │   └── components/         # کامپوننت‌های UI
│   │       ├── header.js       # هدر سایت
│   │       ├── footer.js       # فوتر سایت
│   │       └── course-card.js  # کارت دوره
│   │
│   ├── assets/                 # تصاویر و فونت‌ها
│   ├── robots.txt              # فایل robots.txt
│   ├── sitemap.xml             # نقشه سایت
│   └── Dockerfile              # فایل Docker برای فرانت‌اند
│
├── docker/                     # تنظیمات Docker
│   └── mysql/
│       └── init.sql            # اسکریپت اولیه دیتابیس
│
├── run.sh                      # اسکریپت اجرا (Linux/macOS)
├── run.ps1                     # اسکریپت اجرا (Windows)
├── .env.example                # نمونه متغیرهای محیطی
├── .gitignore                  # فایل‌های نادیده‌گرفته شده در Git
├── README.md                   # مستندات پروژه
├── package.json                # تنظیمات Node.js (اختیاری)
└── serve.py                    # سرور محلی برای توسعه
```

---

## 📦 پیش‌نیازها

- **Docker** (نسخه 20.10 یا بالاتر)
- **Git**
- **Python 3.12** (برای توسعه محلی)
- **Node.js** (اختیاری، برای ابزارهای توسعه)

### نصب Docker

#### Windows
1. دانلود Docker Desktop از [docker.com](https://www.docker.com/products/docker-desktop/)
2. نصب و راه‌اندازی
3. ری‌استارت سیستم

#### macOS
```bash
brew install --cask docker
```

#### Linux (Ubuntu/Debian)
```bash
# نصب Docker
sudo apt-get update
sudo apt-get install -y docker.io

# اضافه کردن کاربر به گروه docker
sudo usermod -aG docker $USER
```

---

## ⚙️ متغیرهای محیطی

### ایجاد فایل .env

```bash
cp .env.example .env
```

### توضیح متغیرها

| متغیر | توضیح | مقدار پیش‌فرض |
|--------|--------|---------------|
| `SECRET_KEY` | کلید مخفی Django برای امضا کردن | `django-insecure-dev-key` |
| `DEBUG` | حالت توسعه | `True` |
| `DB_NAME` | نام دیتابیس MySQL | `hooshafza` |
| `DB_USER` | نام کاربری MySQL | `hooshafza_user` |
| `DB_PASSWORD` | رمز عبور MySQL | `hooshafza_password` |
| `DB_ROOT_PASSWORD` | رمز عبور Root MySQL | `hooshafza_root` |
| `DB_HOST` | آدرس سرور MySQL | `hooshafza-mysql` |
| `DB_PORT` | پورت MySQL | `3306` |
| `JWT_SECRET_KEY` | کلید مخفی JWT | `jwt-secret-dev-key` |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | عمر توکن دسترسی (دقیقه) | `60` |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | عمر توکن رفرش (روز) | `7` |
| `PAYMENT_GATEWAY` | درگاه پرداخت | `ZARINPAL` |
| `PAYMENT_API_KEY` | کلید API درگاه پرداخت | — |
| `PAYMENT_MERCHANT_ID` | شناسه تاجر | — |
| `SPOTPLAYER_API_KEY` | کلید API SpotPlayer | — |
| `SPOTPLAYER_BASE_URL` | آدرس API SpotPlayer | `https://api.spotplayer.ir` |
| `SITE_DOMAIN` | دامنه سایت | `localhost` |
| `SITE_NAME` | نام سایت | `هوش افزا` |
| `ALLOWED_HOSTS` | هاست‌های مجاز | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | مجاز CORS | `http://localhost,http://127.0.0.1` |

> ⚠️ **هشدار:** هرگز فایل `.env` را در Git commit نکنید!

---

## 🐳 نصب و اجرای Docker

### روش ۱: استفاده از اسکریپت (توصیه شده)

#### ۱. کلون پروژه
```bash
git clone <repo-url>
cd hooshafza
```

#### ۲. تنظیم متغیرهای محیطی
```bash
cp .env.example .env
# ویرایش .env با مقادیر دلخواه
nano .env  # یا هر ویرایشگر دیگری
```

#### ۳. اجرا

**Linux/macOS:**
```bash
chmod +x run.sh
./run.sh start
```

**Windows:**
```powershell
.\run.ps1 start
```

#### ۴. ایجاد ادمین

**Linux/macOS:**
```bash
./run.sh createsuperuser
```

**Windows:**
```powershell
.\run.ps1 createsuperuser
```

#### ۵. مشاهده وضعیت

**Linux/macOS:**
```bash
./run.sh status
```

**Windows:**
```powershell
.\run.ps1 status
```

#### ۶. مشاهده لاگ‌ها

**Linux/macOS:**
```bash
./run.sh logs
```

**Windows:**
```powershell
.\run.ps1 logs
```

#### دستورات دیگر

| دستور | توضیح |
|--------|--------|
| `start` | اجرای تمام کانتینرها |
| `stop` | توقف تمام کانتینرها |
| `restart` | ری‌استارت |
| `status` | مشاهده وضعیت |
| `logs` | مشاهده لاگ‌ها |
| `build` | بیلد مجدد تصاویر |
| `migrate` | اجرای مایگریشن‌ها |
| `createsuperuser` | ایجاد ادمین |

---

### روش ۲: دستورات Docker دستی

#### ۱. ایجاد شبکه Docker
```bash
docker network create hooshafza-net
```

#### ۲. اجرای MySQL
```bash
docker run -d \
  --name hooshafza-mysql \
  --network hooshafza-net \
  -e MYSQL_ROOT_PASSWORD=hooshafza_root \
  -e MYSQL_DATABASE=hooshafza \
  -e MYSQL_USER=hooshafza_user \
  -e MYSQL_PASSWORD=hooshafza_password \
  -p 3306:3306 \
  -v hooshafza-mysql-data:/var/lib/mysql \
  -v "$(pwd)/docker/mysql/init.sql:/docker-entrypoint-initdb.d/01-init.sql" \
  mysql:8.0
```

#### ۳. بیلد و اجرای Backend (Django)
```bash
# بیلد
docker build -t hooshafza-backend ./backend

# اجرا
docker run -d \
  --name hooshafza-backend \
  --network hooshafza-net \
  -e DB_HOST=hooshafza-mysql \
  -e DB_NAME=hooshafza \
  -e DB_USER=hooshafza_user \
  -e DB_PASSWORD=hooshafza_password \
  -e SECRET_KEY=django-insecure-dev-key \
  -e DEBUG=True \
  -e JWT_SECRET_KEY=jwt-secret-dev-key \
  -e SITE_DOMAIN=localhost \
  -e SITE_NAME="هوش افزا" \   -p 127.0.0.1:8001:8001 \
  -v "$(pwd)/backend:/app" \
  hooshafza-backend

# اجرای مایگریشن
docker exec hooshafza-backend python manage.py migrate
```

#### ۴. بیلد و اجرای API (FastAPI)
```bash
# بیلد
docker build -t hooshafza-api ./api

# اجرا
docker run -d \
  --name hooshafza-api \
  --network hooshafza-net \
  -e DB_HOST=hooshafza-mysql \
  -e DB_NAME=hooshafza \
  -e DB_USER=hooshafza_user \
  -e DB_PASSWORD=hooshafza_password \
  -e SECRET_KEY=django-insecure-dev-key \
  -e DEBUG=True \
  -e JWT_SECRET_KEY=jwt-secret-dev-key \
  -e DJANGO_SETTINGS_MODULE=config.settings \
  -e PYTHONPATH=/backend:/app \   -p 127.0.0.1:8000:8000 \
  -v "$(pwd)/api:/app" \
  -v "$(pwd)/backend:/backend" \
  hooshafza-api
```

#### ۵. بیلد و اجرای Frontend
```bash
# بیلد
docker build -t hooshafza-frontend ./frontend

# اجرا
docker run -d \
  --name hooshafza-frontend \
  --network hooshafza-net \
  -p 80:80 \
  hooshafza-frontend
```

---

## 👤 سیستم کاربران

### نقش‌ها

| نقش | توضیح | دسترسی‌ها |
|-----|--------|----------|
| `STUDENT` | دانشجو | مشاهده دوره‌ها، خرید، آزمون، گواهینامه |
| `ADMIN` | مدیر | دسترسی کامل به تمام بخش‌ها |

### احراز هویت

- **روش:** شماره موبایل + رمز عبور
- **توکن:** JWT (JSON Web Token)
- **عمر توکن:** قابل تنظیم در متغیرهای محیطی

### API احراز هویت

```bash
# ثبت‌نام
POST http://localhost:8000/api/v1/auth/register
{
  "phone_number": "09123456789",
  "password": "securepassword",
  "first_name": "علی",
  "last_name": "احمدی"
}

# ورود
POST http://localhost:8000/api/v1/auth/login
{
  "phone_number": "09123456789",
  "password": "securepassword"
}

# پاسخ:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}

# دریافت اطلاعات کاربر
GET http://localhost:8000/api/v1/auth/me
Authorization: Bearer <access_token>
```

---

## 🎓 سیستم دوره‌ها

### انواع دوره

| نوع | توضیح | ویژگی‌ها |
|-----|--------|---------|
| `IN_PERSON` | حضوری | ظرفیت محدود، زمان‌بندی، پیش‌پرداخت |
| `RECORDED` | ضبط‌شده | دسترسی آنلاین، SpotPlayer، پیگیری پیشرفت |

### مدل داده‌ای

```
Course
├── title (عنوان)
├── slug (لینک دوستانه)
├── short_description (توضیح کوتاه)
├── description (توضیح کامل)
├── thumbnail (تصویر بندانگشتی)
├── instructor (مدرس)
├── category (دسته‌بندی)
├── course_type (نوع دوره)
├── price (قیمت)
├── status (وضعیت)
├── is_published (آیا منتشر شده)
│
├── Chapter (فصل‌ها)
│   └── Lesson (درس‌ها)
│       ├── title
│       ├── description
│       ├── duration
│       ├── order
│       ├── spotplayer_id
│       ├── is_preview (آیا رایگان است)
│       └── is_published
│
├── CourseSchedule (زمان‌بندی - فقط دوره حضوری)
│   ├── day_of_week
│   ├── start_time
│   └── end_time
│
└── InPersonDetail (اطلاعات تکمیلی - فقط دوره حضوری)
    ├── prepayment_amount
    ├── remaining_amount
    ├── capacity
    ├── enrolled_count
    ├── start_date
    ├── end_date
    └── location
```

### API دوره‌ها

```bash
# لیست دوره‌ها
GET http://localhost:8000/api/v1/courses

# جزئیات دوره
GET http://localhost:8000/api/v1/courses/{slug}

# دسته‌بندی‌ها
GET http://localhost:8000/api/v1/courses/categories

# دوره‌های ویژه
GET http://localhost:8000/api/v1/courses/featured

# جستجو
GET http://localhost:8000/api/v1/search?q=python
```

---

## 💳 سیستم پرداخت

### جریان خرید

```
دانشجو
  │
  ▼
افزودن به سبد خرید
  │
  ▼
اعمال کد تخفیف (اختیاری)
  │
  ▼
تکمیل خرید → ایجاد سفارش
  │
  ▼
پرداخت آنلاین
  │
  ├─► موفق → ثبت‌نام خودکار + دسترسی به دوره
  │
  └─► ناموفق → لغو سفارش
```

### درگاه پرداخت

سیستم از الگوی **Gateway Interface** استفاده می‌کند که امکان اضافه کردن درگاه‌های مختلف را فراهم می‌کند.

**درگاه‌های پشتیبانی شده:**
- Zarinpal (پیاده‌سازی شده)
- سایر درگاه‌ها (قابل اضافه شدن)

### API پرداخت

```bash
# شروع پرداخت
POST http://localhost:8000/api/v1/payments/initiate
{
  "order_id": 123
}

# برگشت از درگاه
GET http://localhost:8000/api/v1/payments/callback?authority=XXX&status=OK

# وضعیت پرداخت
GET http://localhost:8000/api/v1/payments/{payment_id}/status
```

### وضعیت‌های پرداخت

| وضعیت | توضیح |
|--------|--------|
| `PENDING` | در انتظار پرداخت |
| `SUCCESS` | پرداخت موفق |
| `FAILED` | پرداخت ناموفق |
| `CANCELED` | لغو شده |

---

## 🎫 سیستم تیکت پشتیبانی

### جریان تیکت

```
دانشجو
  │
  ▼
ایجاد تیکت (موضوع + متن)
  │
  ▼
مدیر: مشاهده + پاسخ
  │
  ▼
دانشجو: مشاهده پاسخ
  │
  ▼
تغییر وضعیت: باز → در حال بررسی → پاسخ داده شده → بسته شده
```

### API تیکت

```bash
# ایجاد تیکت
POST http://localhost:8000/api/v1/tickets
{
  "subject": "مشکل ورود به دوره",
  "message": "می‌خواهم وارد دوره پایتون شوم اما خطای 403 می‌دهم..."
}

# لیست تیکت‌ها
GET http://localhost:8000/api/v1/tickets

# جزئیات تیکت
GET http://localhost:8000/api/v1/tickets/{ticket_id}

# پاسخ به تیکت
POST http://localhost:8000/api/v1/tickets/{ticket_id}/messages
{
  "message": "لطفاً مرورگر خود را به‌روزرسانی کنید..."
}
```

---

## 🎯 پنل مدیریت

### دسترسی به پنل مدیریت

- **Django Admin:** `http://localhost:8001/admin/`
- **API Admin:** `http://localhost:8000/api/v1/admin/`

### قابلیت‌های مدیریت

#### مدیریت کاربران
- ایجاد، ویرایش، حذف کاربران
- فعال/غیرفعال کردن حساب
- تغییر نقش کاربر
- ریست رمز عبور
- مشاهده اطلاعات ورود

#### مدیریت دوره‌ها
- ایجاد دوره جدید
- افزودن فصل و درس
- تنظیم قیمت و ظرفیت
- تعیین مدرس
- انتشار/متوقف کردن
- مدیریت ویدئوها

#### مدیریت سفارشات
- مشاهده تمام سفارشات
- تغییر وضعیت سفارش
- جزئیات پرداخت

#### مدیریت تخفیف‌ها
- ایجاد کد تخفیف
- تعیین درصد یا مبلغ ثابت
- محدودیت زمانی و تعداد
- محدود کردن به دوره خاص

#### مدیریت آزمون‌ها
- ایجاد آزمون
- افزودن سؤال و گزینه
- تعیین پاسخ صحیح
- مشاهده نتایج دانشجویان

#### مدیریت مقالات
- ایجاد، ویرایش، حذف مقالات
- دسته‌بندی و برچسب‌گذاری
- تنظیمات SEO

#### مدیریت تیکت‌ها
- مشاهده تیکت‌های جدید
- پاسخ به تیکت‌ها
- تغییر وضعیت

#### آمار داشبورد
- تعداد دانشجویان
- تعداد دوره‌ها
- درآمد کل
- تعداد سفارشات
- تعداد تیکت‌های باز

---

## 📊 داشبورد دانشجو

### قابلیت‌های داشبورد

#### پروفایل
- مشاهده و ویرایش اطلاعات شخصی
- تغییر رمز عبور
- مشاهده تاریخچه فعالیت

#### دوره‌های من
- لیست دوره‌های خریداری شده
- درصد پیشرفت هر دوره
- ادامه یادگیری از آخرین درس مشاهده شده

#### سفارشات
- لیست سفارشات
- جزئیات هر سفارش
- وضعیت پرداخت

#### گواهینامه‌ها
- گواهینامه‌های دریافت شده
- کد تأیید
- دانلود گواهینامه

#### آزمون‌ها
- آزمون‌های در دسترس
- نتایج آزمون‌ها

#### اعلان‌ها
- اعلان‌های خوانده نشده
- علامت‌گذاری به عنوان خوانده شده

#### تیکت‌ها
- ایجاد تیکت جدید
- مشاهده پاسخ‌ها

---

## 📡 API Documentation

### مستندات API

FastAPI به صورت خودکار مستندات API را تولید می‌کند:

| آدرس | توضیح |
|------|--------|
| `http://localhost:8000/docs` | Swagger UI (رابط تعاملی) |
| `http://localhost:8000/redoc` | ReDoc (مستندات زیبا) |
| `http://localhost:8000/openapi.json` | فایل OpenAPI |

### مهم‌ترین Endpointها

#### احراز هویت
| Method | Endpoint | توضیح | احراز هویت |
|--------|----------|--------|------------|
| POST | `/api/v1/auth/register` | ثبت‌نام | ❌ |
| POST | `/api/v1/auth/login` | ورود | ❌ |
| GET | `/api/v1/auth/me` | اطلاعات کاربر | ✅ |
| POST | `/api/v1/auth/refresh` | رفرش توکن | ✅ |

#### دوره‌ها
| Method | Endpoint | توضیح | احراز هویت |
|--------|----------|--------|------------|
| GET | `/api/v1/courses` | لیست دوره‌ها | ❌ |
| GET | `/api/v1/courses/{slug}` | جزئیات دوره | ❌ |
| GET | `/api/v1/courses/categories` | دسته‌بندی‌ها | ❌ |
| GET | `/api/v1/courses/featured` | دوره‌های ویژه | ❌ |
| GET | `/api/v1/instructors` | مدرسین | ❌ |
| GET | `/api/v1/instructors/{slug}` | جزئیات مدرس | ❌ |

#### سبد خرید
| Method | Endpoint | توضیح | احراز هویت |
|--------|----------|--------|------------|
| GET | `/api/v1/cart` | مشاهده سبد | ✅ |
| POST | `/api/v1/cart/items` | افزودن دوره | ✅ |
| DELETE | `/api/v1/cart/items/{id}` | حذف دوره | ✅ |
| POST | `/api/v1/cart/coupon` | اعمال تخفیف | ✅ |

#### سفارشات و پرداخت
| Method | Endpoint | توضیح | احراز هویت |
|--------|----------|--------|------------|
| POST | `/api/v1/orders/checkout` | تکمیل خرید | ✅ |
| GET | `/api/v1/orders` | لیست سفارشات | ✅ |
| POST | `/api/v1/payments/initiate` | شروع پرداخت | ✅ |
| GET | `/api/v1/payments/callback` | برگشت از درگاه | ❌ |

#### ثبت‌نام
| Method | Endpoint | توضیح | احراز هویت |
|--------|----------|--------|------------|
| GET | `/api/v1/enrollments` | لیست ثبت‌نام‌ها | ✅ |
| GET | `/api/v1/enrollments/{id}` | جزئیات ثبت‌نام | ✅ |

#### آزمون و گواهینامه
| Method | Endpoint | توضیح | احراز هویت |
|--------|----------|--------|------------|
| GET | `/api/v1/exams` | لیست آزمون‌ها | ✅ |
| POST | `/api/v1/exams/{id}/start` | شروع آزمون | ✅ |
| POST | `/api/v1/exams/{id}/submit` | ارسال پاسخ | ✅ |
| GET | `/api/v1/certificates` | لیست گواهینامه‌ها | ✅ |

#### وبلاگ
| Method | Endpoint | توضیح | احراز هویت |
|--------|----------|--------|------------|
| GET | `/api/v1/articles` | لیست مقالات | ❌ |
| GET | `/api/v1/articles/{slug}` | جزئیات مقاله | ❌ |

#### جستجو
| Method | Endpoint | توضیح | احراز هویت |
|--------|----------|--------|------------|
| GET | `/api/v1/search?q=` | جستجوی سراسری | ❌ |

#### اعلان‌ها و تیکت‌ها
| Method | Endpoint | توضیح | احراز هویت |
|--------|----------|--------|------------|
| GET | `/api/v1/notifications` | لیست اعلان‌ها | ✅ |
| PUT | `/api/v1/notifications/{id}/read` | علامت‌گذاری خوانده شده | ✅ |
| GET | `/api/v1/tickets` | لیست تیکت‌ها | ✅ |
| POST | `/api/v1/tickets` | ایجاد تیکت | ✅ |

#### پنل مدیریت
| Method | Endpoint | توضیح | احراز هویت |
|--------|----------|--------|------------|
| GET | `/api/v1/admin/dashboard/stats` | آمار داشبورد | 🔒 Admin |
| GET/POST | `/api/v1/admin/users` | مدیریت کاربران | 🔒 Admin |
| POST | `/api/v1/admin/enrollments` | ثبت‌نام دستی | 🔒 Admin |
| GET | `/api/v1/admin/orders` | سفارشات | 🔒 Admin |
| POST | `/api/v1/admin/discounts` | کدهای تخفیف | 🔒 Admin |

---

## 🎨 Frontend

### ویژگی‌های فرانت‌اند

- **RTL:** تمام صفحات فارسی و راست‌چین
- **Responsive:** Mobile-First با پشتیبانی از تمام اندازه صفحه نمایش
- **SEO:** متا تگ‌ها، Schema.org، sitemap.xml، robots.txt
- **Accessible:** Semantic HTML، ARIA، alt text، keyboard navigation
- **SPA-like:** صفحات جداگانه با JavaScript مشترک

### صفحات عمومی

| URL | عنوان | توضیح |
|-----|--------|--------|
| `/` | خانه | صفحه اصلی با دوره‌های ویژه |
| `/pages/courses.html` | دوره‌ها | لیست تمام دوره‌ها |
| `/pages/course-detail.html` | جزئیات دوره | اطلاعات کامل یک دوره |
| `/pages/instructors.html` | مدرسین | لیست مدرسین |
| `/pages/blog.html` | وبلاگ | مقالات آموزشی |
| `/pages/article-detail.html` | جزئیات مقاله | متن کامل مقاله |
| `/pages/about.html` | درباره ما | معرفی مؤسسه |
| `/pages/contact.html` | تماس | فرم تماس |
| `/pages/faq.html` | سؤالات متداول | پاسخ به سؤالات رایج |
| `/pages/terms.html` | قوانین | قوانین و مقررات |
| `/pages/privacy.html` | حریم خصوصی | سیاست حفظ حریم خصوصی |
| `/pages/404.html` | یافت نشد | صفحه خطای 404 |

### صفحات کاربر

| URL | عنوان | توضیح |
|-----|--------|--------|
| `/pages/login.html` | ورود | فرم ورود با شماره موبایل |
| `/pages/register.html` | ثبت‌نام | فرم ثبت‌نام |
| `/pages/cart.html` | سبد خرید | مدیریت سبد خرید |
| `/pages/dashboard.html` | داشبورد | پنل دانشجو |

### صفحات مدیریت

| URL | عنوان | توضیح |
|-----|--------|--------|
| `/pages/admin-dashboard.html` | پنل مدیریت | داشبورد مدیر |
| `/django-admin/` | Django Admin | مدیریت داخلی سیستم |

### ماژول‌های JavaScript

| فایل | توضیح |
|------|--------|
| `api.js` | ارتباط با API سرور |
| `auth.js` | مدیریت احراز هویت و توکن‌ها |
| `utils.js` | توابع کمکی (تاریخ، فرمت، اعتبارسنجی) |
| `components/header.js` | کامپوننت هدر سایت |
| `components/footer.js` | کامپوننت فوتر سایت |
| `components/course-card.js` | کامپوننت کارت دوره |

---

## 🔍 SEO

### متا تگ‌ها

هر صفحه شامل متا تگ‌های زیر است:

```html
<title>عنوان صفحه | هوش افزا</title>
<meta name="description" content="توضیحات صفحه">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://example.com/page">

<!-- Open Graph -->
<meta property="og:title" content="عنوان صفحه">
<meta property="og:description" content="توضیحات">
<meta property="og:image" content="https://example.com/image.jpg">
<meta property="og:url" content="https://example.com/page">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="عنوان صفحه">
<meta name="twitter:description" content="توضیحات">
```

### Schema.org

```json
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "عنوان دوره",
  "description": "توضیحات دوره",
  "provider": {
    "@type": "Organization",
    "name": "هوش افزا"
  }
}
```

### فایل‌های SEO

- `robots.txt`: راهنمای خزشگرها
- `sitemap.xml`: نقشه سایت برای موتورهای جستجو

---

## 🔒 امنیت

### اقدامات امنیتی

1. **HTTPS:** استفاده از گواهی SSL در Production
2. **CORS:** پیکربندی صحیح Cross-Origin
3. **CSRF:** محافظت در برابر حملات CSRF
4. **XSS:** فیلتر ورودی‌ها و خروجی‌ها
5. **SQL Injection:** استفاده از ORM
6. **Password Hashing:** استفاده از Django Password Hasher
7. **JWT Security:** عمر محدود توکن‌ها
8. **Rate Limiting:** محدود کردن درخواست‌ها
9. **Input Validation:** اعتبارسنجی تمام ورودی‌ها
10. **Server-Side Validation:** محاسبه قیمت و تخفیف در سمت سرور

### نکات امنیتی مهم

> ⚠️ **هرگز قیمت نهایی را از فرانت‌اند قبول نکنید!**
> قیمت باید همیشه در سمت سرور محاسبه شود.

> ⚠️ **هرگز Secret Key را در کد قرار ندهید!**
> از متغیرهای محیطی استفاده کنید.

---

## 🧪 تست‌ها

### تست‌های مهم

| تست | توضیح |
|-----|--------|
| Authentication | احراز هویت کاربران |
| Course Access | دسترسی به دوره‌ها |
| Cart Operations | عملیات سبد خرید |
| Discount Validation | اعتبارسنجی تخفیف |
| Order Creation | ایجاد سفارش |
| Payment Status | وضعیت پرداخت |
| Capacity Check | بررسی ظرفیت |
| Enrollment | ثبت‌نام دانشجو |
| Exam Submission | ارسال آزمون |
| Certificate Eligibility | واجد شرایط بودن گواهینامه |
| Admin Manual Enrollment | ثبت‌نام دستی توسط ادمین |

### اجرای تست‌ها

```bash
# داخل کانتینر Backend
docker exec hooshafza-backend python manage.py test

# یا برای تست‌های خاص
docker exec hooshafza-backend python manage.py test users
docker exec hooshafza-backend python manage.py test courses
```

---

## 🚀 Production Deployment

### مراحل استقرار

1. **تنظیم متغیرهای محیطی:**
   ```bash
   DEBUG=False
   SECRET_KEY=<کلید امن و تصادفی>
   ALLOWED_HOSTS=yourdomain.com
   ```

2. **جمع‌آوری فایل‌های استاتیک:**
   ```bash
   docker exec hooshafza-backend python manage.py collectstatic --noinput
   ```

3. **استفاده از Gunicorn:**
   ```bash
   # تغییر دستور در Backend
   gunicorn config.wsgi:application --bind 0.0.0.0:8001 --workers 4
   ```

4. **بکاپ خودکار:**
   ```bash
   # اسکریپت بکاپ روزانه
   0 2 * * * docker exec hooshafza-mysql mysqldump -u root -p<password> hooshafza | gzip > /backup/hooshafza-$(date +\%Y\%m\%d).sql.gz
   ```

---

## 💾 بکاپ و بازیابی

### بکاپ دیتابیس

```bash
# بکاپ کامل
docker exec hooshafza-mysql mysqldump -u root -p hooshafza > backup.sql

# بکاپ فشرده
docker exec hooshafza-mysql mysqldump -u root -p hooshafza | gzip > backup.sql.gz
```

### بازیابی دیتابیس

```bash
# بازیابی از فایل
docker exec -T hooshafza-mysql mysql -u root -p hooshafza < backup.sql

# بازیابی از فایل فشرده
gunzip < backup.sql.gz | docker exec -T hooshafza-mysql mysql -u root -p hooshafza
```

### بکاپ فایل‌ها

```bash
# بکاپ فایل‌های رسانه
docker cp hooshafza-backend:/app/media ./media-backup

# بکاپ فایل‌های آپلود شده
tar -czf media-backup-$(date +%Y%m%d).tar.gz ./media
```

---

## 🔧 عیب‌یابی

### مشکلات رایج

| مشکل | علت | راه‌حل |
|------|------|--------|
| MySQL اتصال نمی‌دهد | کانتینر MySQL آماده نیست | ۱۰ ثانیه صبر کنید یا `docker logs hooshafza-mysql` |
| Migration خطا | تغییرات مدل اعمال نشده | `docker exec hooshafza-backend python manage.py migrate` |
| API 404 | FastAPI اجرا نیست | `docker logs hooshafza-api` |
| CORS error | Origins مجاز تنظیم نشده | `CORS_ALLOWED_ORIGINS` در `.env` |
| Permission denied | مجوز فایل‌ها | `chmod +x run.sh` |
| Port already in use | پورت اشغال شده | پورت دیگری انتخاب کنید |

### مشاهده لاگ‌ها

```bash
# لاگ همه کانتینرها
docker logs hooshafza-mysql
docker logs hooshafza-backend
docker logs hooshafza-api
docker logs hooshafza-frontend

# مشاهده زنده
docker logs -f hooshafza-backend
```

### بررسی وضعیت کانتینرها

```bash
docker ps -a | grep hooshafza
```

### ورود به کانتینر

```bash
# ورود به Backend
docker exec -it hooshafza-backend bash

# ورود به MySQL
docker exec -it hooshafza-mysql mysql -u root -p
```

---

## 📄 مجوز

© 2025 هوش افزا — مؤسسه علمی، آموزشی و پژوهشی. تمامی حقوق محفوظ است.

---

## 🤝 مشارکت

برای مشارکت در توسعه این پروژه:

1. Fork کنید
2. Branch جدید ایجاد کنید (`git checkout -b feature/amazing-feature`)
3. تغییرات را Commit کنید (`git commit -m 'Add amazing feature'`)
4. Push کنید (`git push origin feature/amazing-feature`)
5. Pull Request ایجاد کنید

---

## 📞 پشتیبانی

- **ایمیل:** support@hooshafza.ir
- **تلفن:** 021-XXXXXXXX
- **آدرس:** تهران، خیابان ...
=======
# Welcome to GitHub Desktop!

This is your README. READMEs are where you can communicate what your project is and how to use it.

Write your name on line 6, save it, and then head back to GitHub Desktop.
>>>>>>> 606c2a5b2a8e22ef63580d45b4734eaaa5ac3f74
