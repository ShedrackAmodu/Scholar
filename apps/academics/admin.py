from django.contrib import admin
from .models import (
    Assessment,
    SubjectAssessment,
    Score,
    SubjectScore,
    ReportCard,
    ClassPerformance,
)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'assessment_type',
        'code',
        'max_score',
        'weight_percentage')
    search_fields = ('name', 'code')


@admin.register(SubjectAssessment)
class SubjectAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        'subject',
        'assessment',
        'term',
        'academic_year',
        'max_score')
    search_fields = ('subject__name', 'assessment__name')


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'subject_assessment',
        'score',
        'recorded_by',
        'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('student__admission_number',)


@admin.register(SubjectScore)
class SubjectScoreAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'subject',
        'total_score',
        'term',
        'academic_year')


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'term',
        'academic_year',
        'average_score',
        'position')
    search_fields = ('student__admission_number',)


@admin.register(ClassPerformance)
class ClassPerformanceAdmin(admin.ModelAdmin):
    list_display = ('class_assigned', 'term', 'academic_year', 'class_average')
