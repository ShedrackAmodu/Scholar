from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LoginHistory, Permission, Role


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)


admin.site.register(LoginHistory)
admin.site.register(Permission)
admin.site.register(Role)
