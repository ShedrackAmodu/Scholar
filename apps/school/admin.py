from django.contrib import admin
from .models import SchoolProfile, AcademicYear, Term, Holiday


@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'current_academic_year')
    search_fields = ('name', 'phone', 'email')


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = (
        'academic_year',
        'term',
        'start_date',
        'end_date',
        'is_current')
    list_filter = ('term', 'is_current')


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name',)
