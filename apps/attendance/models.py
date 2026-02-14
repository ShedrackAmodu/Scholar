from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.students.models import Student
from apps.classes.models import Class
from apps.school.models import AcademicYear, SchoolProfile


class AttendanceSession(models.Model):
    """Attendance session for a class"""
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='attendance_sessions')
    date = models.DateField(default=timezone.now)
    term = models.CharField(max_length=10,
                            choices=SchoolProfile.TermChoices.choices)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    # Session info
    session_taken_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='taken_attendance')
    taken_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # Status
    is_closed = models.BooleanField(default=False)  # No more edits allowed
    closed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='closed_attendance')
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['class_assigned', 'date', 'term', 'academic_year']
        ordering = ['-date']

    def __str__(self):
        return f"{self.class_assigned} - {self.date}"


class Attendance(models.Model):
    """Individual student attendance"""

    class Status(models.TextChoices):
        PRESENT = 'P', 'Present'
        ABSENT = 'A', 'Absent'
        LATE = 'L', 'Late'
        EXCUSED = 'E', 'Excused'
        HOLIDAY = 'H', 'Holiday'

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='attendances')
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendances')

    # Attendance details
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.PRESENT)
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)

    # For late arrivals
    minutes_late = models.PositiveIntegerField(default=0)

    # Notes
    reason_for_absence = models.TextField(blank=True)
    note = models.TextField(blank=True)

    # For approval
    is_approved = models.BooleanField(
        default=True)  # Auto-approved for teachers
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_attendance')

    class Meta:
        unique_together = ['session', 'student']
        verbose_name_plural = 'Attendances'

    def __str__(self):
        return f"{self.student} - {self.session.date} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if self.status == 'L' and not self.minutes_late:
            # Auto-calculate minutes late if time_in is provided
            if self.time_in:
                # Compare with school opening time (simplified)
                self.minutes_late = 15  # Placeholder
        super().save(*args, **kwargs)


class AttendanceSummary(models.Model):
    """Monthly/termly attendance summary for students"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_summaries')
    term = models.CharField(max_length=10,
                            choices=SchoolProfile.TermChoices.choices)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    # Counts
    total_days = models.PositiveIntegerField(default=0)
    days_present = models.PositiveIntegerField(default=0)
    days_absent = models.PositiveIntegerField(default=0)
    days_late = models.PositiveIntegerField(default=0)
    days_excused = models.PositiveIntegerField(default=0)

    # Percentage
    attendance_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ['student', 'term', 'academic_year']

    def __str__(self):
        parts = (
            str(self.student),
            str(self.term),
            str(self.academic_year),
            f"{self.attendance_percentage}%",
        )
        return " - ".join(parts)

    def calculate_percentage(self):
        if self.total_days > 0:
            self.attendance_percentage = (
                self.days_present / self.total_days) * 100
        return self.attendance_percentage
