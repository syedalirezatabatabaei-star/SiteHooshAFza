from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom user manager for phone-based authentication."""

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('شماره تلفن الزامی است')
        extra_fields.setdefault('is_active', True)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with phone number as primary identifier."""

    ROLE_CHOICES = [
        ('STUDENT', 'دانشجو'),
        ('ADMIN', 'مدیر'),
    ]

    username = None
    phone_number = models.CharField(
        'شماره تلفن',
        max_length=15,
        unique=True,
        db_index=True,
    )
    first_name = models.CharField('نام', max_length=100)
    last_name = models.CharField('نام خانوادگی', max_length=100)
    email = models.EmailField('ایمیل', blank=True, null=True)
    role = models.CharField(
        'نقش',
        max_length=10,
        choices=ROLE_CHOICES,
        default='STUDENT',
        db_index=True,
    )
    profile_image = models.ImageField(
        'عکس پروفایل',
        upload_to='users/profiles/',
        blank=True,
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.phone_number})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_admin(self):
        return self.role == 'ADMIN' or self.is_staff
