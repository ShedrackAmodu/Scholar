from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access based on user roles"""
    allowed_roles = []
    
    def test_func(self):
        return self.request.user.role in self.allowed_roles
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to access this page.")
        return redirect('dashboard:home')


class AdminRequiredMixin(RoleRequiredMixin):
    """Restrict access to admin users"""
    allowed_roles = ['SUPER_ADMIN', 'ADMIN']


class TeacherRequiredMixin(RoleRequiredMixin):
    """Restrict access to teachers"""
    allowed_roles = ['TEACHER', 'PRINCIPAL', 'VICE_PRINCIPAL', 'ADMIN', 'SUPER_ADMIN']


class ParentRequiredMixin(RoleRequiredMixin):
    """Restrict access to parents"""
    allowed_roles = ['PARENT', 'ADMIN', 'SUPER_ADMIN']


class StudentRequiredMixin(RoleRequiredMixin):
    """Restrict access to students"""
    allowed_roles = ['STUDENT', 'ADMIN', 'SUPER_ADMIN']


class PrincipalRequiredMixin(RoleRequiredMixin):
    """Restrict access to principal and above"""
    allowed_roles = ['PRINCIPAL', 'DIRECTOR', 'ADMIN', 'SUPER_ADMIN']


class DirectorRequiredMixin(RoleRequiredMixin):
    """Restrict access to director and above"""
    allowed_roles = ['DIRECTOR', 'ADMIN', 'SUPER_ADMIN']


class OwnerRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user owns the object or is admin"""
    owner_field = 'user'
    
    def test_func(self):
        obj = self.get_object()
        owner = getattr(obj, self.owner_field)
        return owner == self.request.user or self.request.user.role in ['SUPER_ADMIN', 'ADMIN']
