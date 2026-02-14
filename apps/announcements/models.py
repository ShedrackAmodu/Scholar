from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.classes.models import Class


class Event(models.Model):
    """Events for hero section and calendar"""

    class EventType(models.TextChoices):
        ACADEMIC = 'ACAD', 'Academic'
        SPORTS = 'SPORT', 'Sports'
        CULTURAL = 'CULT', 'Cultural'
        HOLIDAY = 'HOL', 'Holiday'
        MEETING = 'MEET', 'Meeting'
        EXAM = 'EXAM', 'Examination'
        OTHER = 'OTHER', 'Other'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        NORMAL = 'NORM', 'Normal'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRIT', 'Critical'

    title = models.CharField(max_length=200)
    description = models.TextField()

    # Event Details
    event_type = models.CharField(
        max_length=10,
        choices=EventType.choices,
        default=EventType.ACADEMIC)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)

    # Media
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    banner_image = models.ImageField(
        upload_to='events/banners/', null=True, blank=True)

    # Display Options
    is_featured = models.BooleanField(default=False)  # For hero section
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL)

    # Target Audience
    is_public = models.BooleanField(default=True)
    target_classes = models.ManyToManyField(Class, blank=True)
    target_roles = models.JSONField(
        default=list, blank=True)  # ["STUDENT", "TEACHER"]

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # RSVP
    requires_rsvp = models.BooleanField(default=False)
    max_attendees = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-is_featured', '-start_date']

    def __str__(self):
        return self.title

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date


class EventRSVP(models.Model):
    """RSVP for events"""
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='rsvps')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('GOING', 'Going'),
        ('MAYBE', 'Maybe'),
        ('NOT_GOING', 'Not Going')
    ])
    response_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['event', 'user']


class Notice(models.Model):
    """General notices and announcements"""

    class NoticeType(models.TextChoices):
        GENERAL = 'GEN', 'General'
        ACADEMIC = 'ACAD', 'Academic'
        ADMIN = 'ADMIN', 'Administrative'
        EMERGENCY = 'EMER', 'Emergency'
        HOLIDAY = 'HOL', 'Holiday'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        NORMAL = 'NORM', 'Normal'
        HIGH = 'HIGH', 'High'
        URGENT = 'URG', 'Urgent'

    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.CharField(max_length=300, blank=True)

    # Notice Details
    notice_type = models.CharField(
        max_length=10,
        choices=NoticeType.choices,
        default=NoticeType.GENERAL)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL)

    # Display Settings
    publish_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_pinned = models.BooleanField(default=False)  # Stays at top

    # Media
    attachment = models.FileField(upload_to='notices/', null=True, blank=True)
    image = models.ImageField(
        upload_to='notices/images/',
        null=True,
        blank=True)

    # Target Audience
    is_public = models.BooleanField(default=True)  # Show on public noticeboard
    target_classes = models.ManyToManyField(Class, blank=True)
    target_roles = models.JSONField(
        default=list, blank=True)  # ["STUDENT", "TEACHER"]

    # Tracking
    view_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_notices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-publish_date']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        now = timezone.now()
        if self.expiry_date:
            return self.publish_date <= now <= self.expiry_date
        return self.publish_date <= now


class NoticeRead(models.Model):
    """Track who has read notices"""
    notice = models.ForeignKey(
        Notice,
        on_delete=models.CASCADE,
        related_name='reads')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['notice', 'user']


class Assignment(models.Model):
    """Class assignments created by teachers"""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUB', 'Published'
        CANCELLED = 'CANC', 'Cancelled'
        COMPLETED = 'COMP', 'Completed'

    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField(blank=True)

    # Assignment Details
    subject = models.ForeignKey(
        'classes.Subject',
        on_delete=models.CASCADE,
        related_name='assignments')
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='assignments')

    # Dates
    date_assigned = models.DateField(default=timezone.now)
    due_date = models.DateTimeField()

    # Files
    attachment = models.FileField(
        upload_to='assignments/', null=True, blank=True)

    # Grading
    total_marks = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    is_graded = models.BooleanField(default=False)

    # Status
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PUBLISHED)

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.title} - {self.class_assigned}"

    @property
    def is_past_due(self):
        return timezone.now() > self.due_date


class AssignmentSubmission(models.Model):
    """Student submissions for assignments"""

    class Status(models.TextChoices):
        SUBMITTED = 'SUB', 'Submitted'
        LATE = 'LATE', 'Late'
        GRADED = 'GRAD', 'Graded'
        RETURNED = 'RET', 'Returned'

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions')
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='assignment_submissions')

    # Submission
    submission_file = models.FileField(
        upload_to='submissions/', null=True, blank=True)
    submission_text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Status
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.SUBMITTED)

    # Grading
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='graded_assignments')
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student} - {self.assignment}"


class Notification(models.Model):
    """In-app notifications"""

    class NotificationType(models.TextChoices):
        ASSIGNMENT = 'ASSIGN', 'New Assignment'
        SCORE = 'SCORE', 'Score Posted'
        ATTENDANCE = 'ATTEND', 'Attendance'
        EVENT = 'EVENT', 'Event'
        PAYMENT = 'PAY', 'Payment'
        GENERAL = 'GEN', 'General'
        ALERT = 'ALERT', 'Alert'

    notification_type = models.CharField(
        max_length=10, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()

    # Links
    link = models.CharField(
        max_length=500,
        blank=True)  # URL to related content

    # Target
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications')
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_notifications')

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.recipient} - {self.title}"


class ClassMessage(models.Model):
    """Messages sent to specific classes"""
    class_assigned = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='sent_class_messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    attachment = models.FileField(
        upload_to='class_messages/',
        null=True,
        blank=True)

    # Send options
    send_to_students = models.BooleanField(default=True)
    send_to_parents = models.BooleanField(default=True)

    # Tracking
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.class_assigned} - {self.subject}"
