from django.contrib import admin
from .models import Application, ApplicationComment, EntranceExam


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'application_number',
        'first_name',
        'last_name',
        'status',
        'application_date')
    list_filter = ('status',)
    search_fields = ('application_number', 'first_name', 'last_name', 'email')


@admin.register(ApplicationComment)
class ApplicationCommentAdmin(admin.ModelAdmin):
    list_display = ('application', 'user', 'created_at')


@admin.register(EntranceExam)
class EntranceExamAdmin(admin.ModelAdmin):
    list_display = ('application', 'exam_date', 'total_score', 'is_passed')
