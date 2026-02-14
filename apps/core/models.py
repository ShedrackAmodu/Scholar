from django.db import models
from django.conf import settings


# Converted previous CustomUser to a profile linked to the project's user model
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile')

    ROLE_CHOICES = [
        ("superadmin", "Super Admin"),
        ("admin", "Admin"),
        ("principal", "Principal"),
        ("vice_principal", "Vice Principal"),
        ("director", "Director"),
        ("teacher", "Teacher"),
        ("student", "Student"),
        ("parent", "Parent"),
    ]

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default="student")
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profiles/", blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class SchoolProfile(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="school/logo/", blank=True, null=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    opening_time = models.TimeField(blank=True, null=True)
    closing_time = models.TimeField(blank=True, null=True)
    academic_year_start = models.DateField(blank=True, null=True)
    academic_year_end = models.DateField(blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#ff69b4")
    secondary_color = models.CharField(max_length=7, default="#ffb6c1")

    def __str__(self):
        return self.name
