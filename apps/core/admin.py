from django.contrib import admin
from .models import UserProfile, SchoolProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username', 'user__email')


@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'phone',
        'academic_year_start',
        'academic_year_end')
