from django.db import models
from apps.accounts.models import User
from apps.school.models import AcademicYear, SchoolProfile


class ClassLevel(models.Model):
    """Educational levels (Primary 1, JSS 1, etc.)"""

    LEVEL_TYPES = [
        ('PRIMARY', 'Primary'),
        ('JSS', 'Junior Secondary'),
        ('SSS', 'Senior Secondary'),
    ]

    name = models.CharField(max_length=50)  # e.g., "Primary 1", "JSS 2"
    level_type = models.CharField(max_length=10, choices=LEVEL_TYPES)
    order = models.PositiveIntegerField(unique=True)  # For sorting
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Class(models.Model):
    """Actual classes (e.g., Primary 1A, JSS 2B)"""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        GRADUATED = 'GRADUATED', 'Graduated'

    name = models.CharField(max_length=50)  # e.g., "Primary 1A"
    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.PROTECT,
        related_name='classes')
    class_teacher = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='class_teacher_of',
        limit_choices_to={'role': 'TEACHER'}
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name='classes')

    # Capacity
    capacity = models.PositiveIntegerField(default=40)
    current_enrollment = models.PositiveIntegerField(default=0)

    # Details
    room_number = models.CharField(max_length=20, blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Classes'
        unique_together = ['name', 'academic_year']
        ordering = ['class_level__order', 'name']

    def __str__(self):
        return f"{self.name} - {self.academic_year}"

    @property
    def available_slots(self):
        return self.capacity - self.current_enrollment

    @property
    def is_full(self):
        return self.current_enrollment >= self.capacity


class Subject(models.Model):
    """School subjects"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.PROTECT,
        related_name='subjects')
    is_compulsory = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    # For report card ordering
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['class_level__order', 'display_order', 'name']
        unique_together = ['name', 'class_level']

    def __str__(self):
        return f"{self.name} ({self.code})"


class SubjectAllocation(models.Model):
    """Assign subjects to teachers for specific classes"""
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subject_allocations',
        limit_choices_to={'role': 'TEACHER'}
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='allocations')
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='subject_allocations')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)

    # For multiple terms
    term = models.CharField(
        max_length=10,
        choices=SchoolProfile.TermChoices.choices,
        null=True,
        blank=True)

    class Meta:
        unique_together = [
            'teacher',
            'subject',
            'class_assigned',
            'academic_year',
            'term']

    def __str__(self):
        teacher_name = self.teacher.get_full_name()
        subject_name = self.subject.name
        return f"{teacher_name} - {subject_name} - {self.class_assigned}"
