from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User
from apps.students.models import Student
from apps.classes.models import Class, Subject, ClassLevel
from apps.school.models import AcademicYear, SchoolProfile


class Assessment(models.Model):
    """Types of assessments (Test, Exam, etc.)"""

    class AssessmentType(models.TextChoices):
        TEST = 'TEST', 'Test'
        MID_TERM = 'MIDTERM', 'Mid-Term Exam'
        EXAM = 'EXAM', 'Final Exam'
        ASSIGNMENT = 'ASSIGN', 'Assignment'
        PROJECT = 'PROJ', 'Project'
        PRACTICAL = 'PRAC', 'Practical'

    name = models.CharField(max_length=100)
    assessment_type = models.CharField(
        max_length=10, choices=AssessmentType.choices)
    code = models.CharField(max_length=20, unique=True)

    # Scoring
    max_score = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[
            MinValueValidator(0)])
    weight_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[
            MinValueValidator(0), MaxValueValidator(100)])

    # Applicability
    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.PROTECT,
        null=True,
        blank=True)
    is_active = models.BooleanField(default=True)

    # For automated grading
    grade_boundaries = models.JSONField(
        default=dict, blank=True)  # {"A": 70, "B": 60, etc.}

    class Meta:
        ordering = ['assessment_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_assessment_type_display()})"


class SubjectAssessment(models.Model):
    """Link assessments to subjects for specific terms"""
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='assessments')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    term = models.CharField(max_length=10,
                            choices=SchoolProfile.TermChoices.choices)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    # Override max_score if different from assessment default
    max_score = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[
            MinValueValidator(0)])

    class Meta:
        unique_together = ['subject', 'assessment', 'term', 'academic_year']

    def __str__(self):
        return f"{self.subject} - {self.assessment} ({self.term})"


class Score(models.Model):
    """Individual student scores for assessments"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='scores')
    subject_assessment = models.ForeignKey(
        SubjectAssessment,
        on_delete=models.CASCADE,
        related_name='scores')

    # Score
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0)])
    remarks = models.TextField(blank=True)

    # Metadata
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='recorded_scores')
    recorded_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # For approval workflow
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_scores')
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'subject_assessment']
        ordering = ['student', 'subject_assessment__subject']

    def __str__(self):
        return f"{self.student} - {self.subject_assessment} - {self.score}"

    @property
    def percentage(self):
        """Calculate percentage score"""
        if self.subject_assessment.max_score > 0:
            return (self.score / self.subject_assessment.max_score) * 100
        return 0

    @property
    def grade(self):
        """Calculate grade based on percentage"""
        percentage = self.percentage
        boundaries = self.subject_assessment.assessment.grade_boundaries

        if boundaries:
            for grade, min_score in sorted(
                    boundaries.items(), key=lambda x: x[1], reverse=True):
                if percentage >= min_score:
                    return grade

        # Default grading if no boundaries set
        if percentage >= 70:
            return 'A'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C'
        elif percentage >= 40:
            return 'D'
        else:
            return 'F'


class SubjectScore(models.Model):
    """Aggregated scores for a subject in a term"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='subject_scores')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.CharField(max_length=10,
                            choices=SchoolProfile.TermChoices.choices)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)

    # Computed scores
    first_test = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True)
    second_test = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    exam_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True)
    total_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)

    # Grade
    grade = models.CharField(max_length=2, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ['student', 'subject', 'term', 'academic_year']

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.total_score}"

    def calculate_total(self):
        """Calculate total score based on assessment weights"""
        total = 0
        assessments = SubjectAssessment.objects.filter(
            subject=self.subject,
            term=self.term,
            academic_year=self.academic_year
        )

        for assessment in assessments:
            try:
                score = Score.objects.get(
                    student=self.student,
                    subject_assessment=assessment
                )
                weighted_score = (score.score / assessment.max_score) * \
                    assessment.assessment.weight_percentage
                total += weighted_score
            except Score.DoesNotExist:
                continue

        self.total_score = total
        return total


class ReportCard(models.Model):
    """Student report card for a term"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='report_cards')
    class_assigned = models.ForeignKey(Class, on_delete=models.PROTECT)
    term = models.CharField(max_length=10,
                            choices=SchoolProfile.TermChoices.choices)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)

    # Results summary (JSON for flexibility)
    # {"Mathematics": 78, "English": 82}
    subject_scores = models.JSONField(default=dict)
    # {"Mathematics": "A", "English": "B"}
    subject_grades = models.JSONField(default=dict)

    # Calculated fields
    total_score = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True)
    average_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    position = models.PositiveIntegerField(null=True, blank=True)
    total_students = models.PositiveIntegerField(default=0)

    # Comments
    class_teacher_comment = models.TextField(blank=True)
    principal_comment = models.TextField(blank=True)

    # Attendance summary
    total_school_days = models.PositiveIntegerField(default=0)
    days_present = models.PositiveIntegerField(default=0)
    days_absent = models.PositiveIntegerField(default=0)

    # Next term info
    next_term_begins = models.DateField(null=True, blank=True)
    promoted_to = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promoted_students')

    # Metadata
    generated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_reports')
    approved_at = models.DateTimeField(null=True, blank=True)

    # PDF
    pdf_file = models.FileField(upload_to='reports/', null=True, blank=True)

    class Meta:
        unique_together = ['student', 'term', 'academic_year']
        ordering = ['-academic_year', '-term', 'position']

    def __str__(self):
        return f"{self.student} - {self.term} {self.academic_year}"

    @property
    def is_promoted(self):
        """Determine if student is promoted to next class"""
        if self.average_score and self.average_score >= 50:  # Passing mark
            return True
        return False


class ClassPerformance(models.Model):
    """Overall class performance for a term"""
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='performances')
    term = models.CharField(max_length=10,
                            choices=SchoolProfile.TermChoices.choices)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    # Statistics
    total_students = models.PositiveIntegerField()
    # {"Mathematics": 65, "English": 70}
    subject_averages = models.JSONField(default=dict)
    class_average = models.DecimalField(max_digits=5, decimal_places=2)
    highest_score = models.DecimalField(max_digits=5, decimal_places=2)
    lowest_score = models.DecimalField(max_digits=5, decimal_places=2)
    pass_rate = models.DecimalField(
        max_digits=5, decimal_places=2)  # Percentage

    class Meta:
        unique_together = ['class_assigned', 'term', 'academic_year']

    def __str__(self):
        return f"{self.class_assigned} - {self.term} {self.academic_year}"
