from django.db import models


class SchoolProfile(models.Model):
    """School information and settings"""

    class TermChoices(models.TextChoices):
        FIRST = 'FIRST', 'First Term'
        SECOND = 'SECOND', 'Second Term'
        THIRD = 'THIRD', 'Third Term'

    # Basic Info
    name = models.CharField(max_length=200)
    slogan = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to='school/logo/', null=True, blank=True)
    favicon = models.ImageField(upload_to='school/', null=True, blank=True)

    # Contact Info
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)

    # School Hours (Editable by admin)
    opening_time = models.TimeField(default='08:00')
    closing_time = models.TimeField(default='15:00')
    half_day_opening = models.TimeField(default='08:00', null=True, blank=True)
    half_day_closing = models.TimeField(default='12:00', null=True, blank=True)

    # Academic Settings
    current_term = models.CharField(
        max_length=10,
        choices=TermChoices.choices,
        default=TermChoices.FIRST)
    current_academic_year = models.CharField(max_length=9, default='2024/2025')
    next_term_begins = models.DateField(null=True, blank=True)

    # Branding
    primary_color = models.CharField(max_length=7, default='#ff69b4')  # Pink
    secondary_color = models.CharField(
        max_length=7, default='#ffb6c1')  # Light Pink
    accent_color = models.CharField(max_length=7, default='#ffffff')

    # Social Media
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'School Profile'
        verbose_name_plural = 'School Profile'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure only one school profile exists
        if not self.pk and SchoolProfile.objects.exists():
            return
        super().save(*args, **kwargs)


class AcademicYear(models.Model):
    """Academic year management"""
    name = models.CharField(max_length=9)  # e.g., 2024/2025
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            # Set all other academic years to not current
            AcademicYear.objects.filter(
                is_current=True).update(
                is_current=False)
        super().save(*args, **kwargs)


class Term(models.Model):
    """Term management within academic year"""
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='terms')
    term = models.CharField(max_length=10,
                            choices=SchoolProfile.TermChoices.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = ['academic_year', 'term']
        ordering = ['start_date']

    def __str__(self):
        return f"{self.academic_year} - {self.get_term_display()}"

    def save(self, *args, **kwargs):
        if self.is_current:
            Term.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class Holiday(models.Model):
    """School holidays and breaks"""
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"
