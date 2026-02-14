from django.contrib import admin
from .models import Student, StudentDocument, StudentHistory


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'admission_number',
        'current_class',
        'enrollment_status')
    search_fields = ('user__username', 'admission_number', 'guardian_name')
    list_filter = ('enrollment_status', 'current_class')


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ('student', 'name', 'uploaded_at')
    search_fields = ('student__admission_number', 'name')


@admin.register(StudentHistory)
class StudentHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'class_assigned',
        'academic_year',
        'date_from',
        'date_to')
    search_fields = ('student__admission_number',)
