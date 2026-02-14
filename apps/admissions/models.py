from django.db import models
from django.core.validators import EmailValidator
from apps.classes.models import ClassLevel
from apps.accounts.models import User
from django.utils import timezone


class Application(models.Model):
    """Student applications for admission"""

    class ApplicationStatus(models.TextChoices):
        PENDING = 'PEND', 'Pending Review'
        UNDER_REVIEW = 'REV', 'Under Review'
        ACCEPTED = 'ACC', 'Accepted'
        REJECTED = 'REJ', 'Rejected'
        WAITLISTED = 'WAIT', 'Waitlisted'
        ENROLLED = 'ENR', 'Enrolled'

    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    # Application Info
    application_number = models.CharField(max_length=50, unique=True)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING)

    # Personal Information (Basic Biodata)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(validators=[EmailValidator()])  # Mandatory
    phone = models.CharField(max_length=15)

    # Additional Info (Optional but nice to have)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        null=True,
        blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Nigeria', blank=True)

    # Academic Info
    applying_for_class = models.ForeignKey(
        ClassLevel,
        on_delete=models.PROTECT,
        related_name='applications')
    previous_school = models.CharField(max_length=200, blank=True)
    previous_class = models.CharField(max_length=50, blank=True)

    # Parent/Guardian Info
    father_name = models.CharField(max_length=200, blank=True)
    father_phone = models.CharField(max_length=15, blank=True)
    father_email = models.EmailField(blank=True)
    mother_name = models.CharField(max_length=200, blank=True)
    mother_phone = models.CharField(max_length=15, blank=True)
    mother_email = models.EmailField(blank=True)
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)
    guardian_email = models.EmailField(blank=True)
    guardian_relationship = models.CharField(max_length=50, blank=True)

    # Documents (Optional for MVP)
    birth_certificate = models.FileField(
        upload_to='applications/birth_certificates/', null=True, blank=True)
    passport_photo = models.ImageField(
        upload_to='applications/photos/', null=True, blank=True)
    previous_results = models.FileField(
        upload_to='applications/results/', null=True, blank=True)

    # Review Info
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reviewed_applications')
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    # If accepted
    admission_number = models.CharField(max_length=50, blank=True)
    enrollment_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-application_date']

    def __str__(self):
        return f"{self.application_number} - {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.application_number:
            # Generate application number (e.g., APP20240001)
            year = timezone.now().year
            last_app = Application.objects.filter(
                application_number__startswith=f"APP{year}"
            ).order_by('application_number').last()

            if last_app:
                last_number = int(last_app.application_number[-4:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.application_number = f"APP{year}{new_number:04d}"

        super().save(*args, **kwargs)


class ApplicationComment(models.Model):
    """Comments on applications during review"""
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='comments')
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.application} - {self.user}"


class EntranceExam(models.Model):
    """Entrance exams for applicants"""
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='entrance_exams')
    exam_date = models.DateField()

    # Scores
    english_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    mathematics_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    general_knowledge = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    total_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)

    # Result
    is_passed = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)

    # Metadata
    conducted_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate total score
        total = 0
        count = 0
        if self.english_score:
            total += self.english_score
            count += 1
        if self.mathematics_score:
            total += self.mathematics_score
            count += 1
        if self.general_knowledge:
            total += self.general_knowledge
            count += 1

        if count > 0:
            self.total_score = total / count

        super().save(*args, **kwargs)
