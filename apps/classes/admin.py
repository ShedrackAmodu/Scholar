from django.contrib import admin
from .models import ClassLevel, Class, Subject, SubjectAllocation


@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'level_type', 'order')
    search_fields = ('name',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'class_level',
        'academic_year',
        'capacity',
        'current_enrollment',
        'status')
    list_filter = ('status', 'academic_year')
    search_fields = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'class_level', 'is_compulsory')
    search_fields = ('name', 'code')


@admin.register(SubjectAllocation)
class SubjectAllocationAdmin(admin.ModelAdmin):
    list_display = (
        'teacher',
        'subject',
        'class_assigned',
        'academic_year',
        'term')
    search_fields = ('teacher__username', 'subject__name')
