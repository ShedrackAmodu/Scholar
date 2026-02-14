from django.contrib import admin
from .models import AttendanceSession, Attendance, AttendanceSummary


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = (
        'class_assigned',
        'date',
        'term',
        'academic_year',
        'session_taken_by',
        'is_closed')
    list_filter = ('term', 'academic_year', 'is_closed')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'session',
        'student',
        'status',
        'minutes_late',
        'is_approved')
    list_filter = ('status', 'is_approved')


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'term',
        'academic_year',
        'attendance_percentage')
