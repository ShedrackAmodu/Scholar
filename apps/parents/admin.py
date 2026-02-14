from django.contrib import admin
from .models import Parent, ParentStudentRelationship


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'receive_sms', 'receive_email')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(ParentStudentRelationship)
class ParentStudentRelationshipAdmin(admin.ModelAdmin):
    list_display = ('parent', 'student', 'relationship', 'is_primary_contact')
    search_fields = ('parent__user__username', 'student__admission_number')
