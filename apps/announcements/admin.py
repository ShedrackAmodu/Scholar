from django.contrib import admin
from .models import (
    Event,
    EventRSVP,
    Notice,
    NoticeRead,
    Assignment,
    AssignmentSubmission,
    Notification,
    ClassMessage,
)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'event_type',
        'start_date',
        'end_date',
        'is_featured')
    list_filter = ('event_type', 'is_featured')


@admin.register(EventRSVP)
class EventRSVPAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'status', 'response_date')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'notice_type',
        'priority',
        'publish_date',
        'is_pinned')
    list_filter = ('notice_type', 'priority')


@admin.register(NoticeRead)
class NoticeReadAdmin(admin.ModelAdmin):
    list_display = ('notice', 'user', 'read_at')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_assigned', 'subject', 'due_date', 'status')
    list_filter = ('status',)


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'status', 'score')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'recipient',
        'notification_type',
        'title',
        'is_read',
        'created_at')
    list_filter = ('notification_type', 'is_read')


@admin.register(ClassMessage)
class ClassMessageAdmin(admin.ModelAdmin):
    list_display = ('class_assigned', 'sender', 'subject', 'sent_at')
