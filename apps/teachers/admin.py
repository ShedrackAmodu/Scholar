from django.contrib import admin
from .models import (
    Teacher,
    TeacherQualification,
    TeacherSubjectExpertise,
    TeacherLeave,
)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'staff_id',
        'qualification',
        'employment_type',
        'is_active')
    search_fields = ('user__username', 'staff_id')
    list_filter = ('qualification', 'employment_type', 'is_active')


@admin.register(TeacherQualification)
class TeacherQualificationAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'degree', 'institution', 'year_obtained')


@admin.register(TeacherSubjectExpertise)
class TeacherSubjectExpertiseAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'is_primary')


@admin.register(TeacherLeave)
class TeacherLeaveAdmin(admin.ModelAdmin):
    list_display = (
        'teacher',
        'leave_type',
        'start_date',
        'end_date',
        'is_approved')
    list_filter = ('is_approved',)
