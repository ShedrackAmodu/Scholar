from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid


class User(AbstractUser):
    """Custom User Model extending Django's AbstractUser"""

    # Roles
    class Roles(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
        ADMIN = 'ADMIN', 'School Admin'
        PRINCIPAL = 'PRINCIPAL', 'Principal'
        VICE_PRINCIPAL = 'VICE_PRINCIPAL', 'Vice Principal'
        DIRECTOR = 'DIRECTOR', 'Director'
        TEACHER = 'TEACHER', 'Teacher'
        STUDENT = 'STUDENT', 'Student'
        PARENT = 'PARENT', 'Parent'

    # Basic Information
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.STUDENT)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True
    )
    profile_picture = models.ImageField(
        upload_to='profiles/', null=True, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    # Metadata
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    last_active = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def has_admin_access(self):
        return self.role in [self.Roles.SUPER_ADMIN, self.Roles.ADMIN,
                             self.Roles.PRINCIPAL, self.Roles.DIRECTOR]

    def has_teaching_access(self):
        return self.role in [self.Roles.TEACHER, self.Roles.PRINCIPAL,
                             self.Roles.VICE_PRINCIPAL]

    # convenience properties used in templates and decorators
    @property
    def is_admin(self):
        # superuser flag should also qualify
        return self.is_superuser or self.has_admin_access()

    @property
    def is_teacher(self):
        return self.role == self.Roles.TEACHER

    @property
    def is_student(self):
        return self.role == self.Roles.STUDENT

    @property
    def is_parent(self):
        return self.role == self.Roles.PARENT

    @property
    def is_principal(self):
        return self.role == self.Roles.PRINCIPAL

    @property
    def is_vice_principal(self):
        return self.role == self.Roles.VICE_PRINCIPAL

    @property
    def is_director(self):
        return self.role == self.Roles.DIRECTOR


class LoginHistory(models.Model):
    """Track user login history"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    session_key = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = 'Login Histories'
        ordering = ['-login_time']


class Permission(models.Model):
    """Custom permissions for roles"""
    name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    """Dynamic role creation by admin"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_roles')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
