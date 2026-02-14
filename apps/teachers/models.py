from django.db import models
from apps.accounts.models import User
from apps.classes.models import Subject
from django.utils import timezone


class Teacher(models.Model):
    """Teacher profile extending User"""

    class Qualification(models.TextChoices):
        NCE = 'NCE', 'NCE'
        BED = 'BED', "Bachelor's in Education"
        BA = 'BA', "Bachelor's Degree"
        MSC = 'MSC', "Master's Degree"
        PHD = 'PHD', 'PhD'
        OTHER = 'OTHER', 'Other'

    class EmploymentType(models.TextChoices):
        FULL_TIME = 'FULL', 'Full Time'
        PART_TIME = 'PART', 'Part Time'
        CONTRACT = 'CONT', 'Contract'
        VISITING = 'VISIT', 'Visiting'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile')
    staff_id = models.CharField(max_length=50, unique=True)

    # Professional Info
    qualification = models.CharField(
        max_length=10, choices=Qualification.choices)
    specialization = models.CharField(max_length=200)
    years_of_experience = models.PositiveIntegerField(default=0)
    employment_type = models.CharField(
        max_length=10,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME)
    date_employed = models.DateField()

    # Contact
    phone = models.CharField(max_length=15)
    address = models.TextField()
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=15)

    # Professional Documents
    cv = models.FileField(upload_to='teachers/cv/', null=True, blank=True)
    certificates = models.FileField(
        upload_to='teachers/certificates/',
        null=True,
        blank=True)

    # Bank Details (for payroll)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    pension_number = models.CharField(max_length=50, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)

    # Status
    is_class_teacher = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.staff_id}"

    def save(self, *args, **kwargs):
        if not self.staff_id:
            # Generate staff ID (e.g., TCH2024001)
            year = timezone.now().year
            last_teacher = Teacher.objects.filter(
                staff_id__startswith=f"TCH{year}"
            ).order_by('staff_id').last()

            if last_teacher:
                last_number = int(last_teacher.staff_id[-3:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.staff_id = f"TCH{year}{new_number:03d}"

        super().save(*args, **kwargs)


class TeacherQualification(models.Model):
    """Additional qualifications"""
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='qualifications')
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year_obtained = models.PositiveIntegerField()
    grade = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.teacher} - {self.degree}"


class TeacherSubjectExpertise(models.Model):
    """Subjects teacher is qualified to teach"""
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='expertise')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)  # Main subject

    class Meta:
        unique_together = ['teacher', 'subject']
        verbose_name_plural = 'Teacher Subject Expertise'

    def __str__(self):
        return f"{self.teacher} - {self.subject}"


class TeacherLeave(models.Model):
    """Teacher leave management"""
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='leaves')
    leave_type = models.CharField(max_length=50)  # Sick, Annual, etc.
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_leaves')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{
            self.teacher} - {
            self.leave_type} ({
            self.start_date} to {
                self.end_date})"
