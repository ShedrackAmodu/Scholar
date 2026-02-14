from django.db import models
from apps.accounts.models import User
from apps.classes.models import Class
from apps.school.models import AcademicYear
from django.utils import timezone


class Student(models.Model):
    """Student profile extending User"""

    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        GRADUATED = 'GRADUATED', 'Graduated'
        TRANSFERRED = 'TRANSFERRED', 'Transferred'
        SUSPENDED = 'SUSPENDED', 'Suspended'
        WITHDRAWN = 'WITHDRAWN', 'Withdrawn'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile')
    admission_number = models.CharField(max_length=50, unique=True)

    # Personal Information
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)
    blood_group = models.CharField(max_length=5, blank=True)
    religion = models.CharField(max_length=50, blank=True)

    # Contact
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nigeria')

    # Guardian Information
    guardian_name = models.CharField(max_length=200)
    guardian_phone = models.CharField(max_length=15)
    guardian_email = models.EmailField()
    guardian_address = models.TextField()
    relationship = models.CharField(max_length=50)  # Father, Mother, etc.

    # Medical Information
    medical_notes = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    doctor_name = models.CharField(max_length=200, blank=True)
    doctor_phone = models.CharField(max_length=15, blank=True)

    # Academic
    current_class = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        related_name='students')
    date_of_admission = models.DateField(auto_now_add=True)
    enrollment_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE)

    # Previous School
    previous_school = models.CharField(max_length=200, blank=True)
    previous_class = models.CharField(max_length=50, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        indexes = [
            models.Index(fields=['admission_number']),
            models.Index(fields=['enrollment_status']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.admission_number}"

    def save(self, *args, **kwargs):
        if not self.admission_number:
            # Generate admission number (e.g., STU2024001)
            year = timezone.now().year
            last_student = Student.objects.filter(
                admission_number__startswith=f"STU{year}"
            ).order_by('admission_number').last()

            if last_student:
                last_number = int(last_student.admission_number[-3:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.admission_number = f"STU{year}{new_number:03d}"

        super().save(*args, **kwargs)


class StudentDocument(models.Model):
    """Student documents (birth certificate, etc.)"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='documents')
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='students/documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.name}"


class StudentHistory(models.Model):
    """Track student class changes over time"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='history')
    class_assigned = models.ForeignKey(Class, on_delete=models.PROTECT)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)
    date_from = models.DateField()
    date_to = models.DateField(null=True, blank=True)
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-date_from']
        verbose_name_plural = 'Student Histories'

    def __str__(self):
        return f"{self.student} - {self.class_assigned} ({self.academic_year})"
