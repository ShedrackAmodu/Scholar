from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.decorators import method_decorator

from .models import User, LoginHistory, Permission, Role
from .forms import CustomUserCreationForm, CustomUserChangeForm, RoleForm, PermissionForm
from apps.accounts.decorators import admin_required


# ============ User Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class UserAdminListView(ListView):
    """Admin list view for Users"""
    model = User
    template_name = 'accounts/admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Filter by role
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by active status
        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=is_active == 'True')
        
        return queryset.order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = User.Roles.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_role'] = self.request.GET.get('role', '')
        context['selected_is_active'] = self.request.GET.get('is_active', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class UserAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Users"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/admin/user_form.html'
    success_url = reverse_lazy('accounts:admin_user_list')
    success_message = "User %(username)s created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New User'
        context['button_text'] = 'Create User'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class UserAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Users"""
    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/admin/user_form.html'
    success_url = reverse_lazy('accounts:admin_user_list')
    success_message = "User %(username)s updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit User: {self.object.get_full_name()}'
        context['button_text'] = 'Update User'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class UserAdminDetailView(DetailView):
    """Admin detail view for Users"""
    model = User
    template_name = 'accounts/admin/user_detail.html'
    context_object_name = 'user'


@method_decorator([login_required, admin_required], name='dispatch')
class UserAdminDeleteView(DeleteView):
    """Admin delete view for Users"""
    model = User
    template_name = 'accounts/admin/user_confirm_delete.html'
    success_url = reverse_lazy('accounts:admin_user_list')
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        messages.success(self.request, f"User {user.get_full_name()} deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ Role Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class RoleAdminListView(ListView):
    """Admin list view for Roles"""
    model = Role
    template_name = 'accounts/admin/role_list.html'
    context_object_name = 'roles'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Role.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class RoleAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Roles"""
    model = Role
    form_class = RoleForm
    template_name = 'accounts/admin/role_form.html'
    success_url = reverse_lazy('accounts:admin_role_list')
    success_message = "Role %(name)s created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Role'
        context['button_text'] = 'Create Role'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


@method_decorator([login_required, admin_required], name='dispatch')
class RoleAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Roles"""
    model = Role
    form_class = RoleForm
    template_name = 'accounts/admin/role_form.html'
    success_url = reverse_lazy('accounts:admin_role_list')
    success_message = "Role %(name)s updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Role: {self.object.name}'
        context['button_text'] = 'Update Role'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class RoleAdminDetailView(DetailView):
    """Admin detail view for Roles"""
    model = Role
    template_name = 'accounts/admin/role_detail.html'
    context_object_name = 'role'


@method_decorator([login_required, admin_required], name='dispatch')
class RoleAdminDeleteView(DeleteView):
    """Admin delete view for Roles"""
    model = Role
    template_name = 'accounts/admin/role_confirm_delete.html'
    success_url = reverse_lazy('accounts:admin_role_list')
    
    def delete(self, request, *args, **kwargs):
        role = self.get_object()
        messages.success(self.request, f"Role {role.name} deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ Permission Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class PermissionAdminListView(ListView):
    """Admin list view for Permissions"""
    model = Permission
    template_name = 'accounts/admin/permission_list.html'
    context_object_name = 'permissions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Permission.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(codename__icontains=search_query)
            )
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class PermissionAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Permissions"""
    model = Permission
    form_class = PermissionForm
    template_name = 'accounts/admin/permission_form.html'
    success_url = reverse_lazy('accounts:admin_permission_list')
    success_message = "Permission %(name)s created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Permission'
        context['button_text'] = 'Create Permission'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class PermissionAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Permissions"""
    model = Permission
    form_class = PermissionForm
    template_name = 'accounts/admin/permission_form.html'
    success_url = reverse_lazy('accounts:admin_permission_list')
    success_message = "Permission %(name)s updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Permission: {self.object.name}'
        context['button_text'] = 'Update Permission'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class PermissionAdminDetailView(DetailView):
    """Admin detail view for Permissions"""
    model = Permission
    template_name = 'accounts/admin/permission_detail.html'
    context_object_name = 'permission'


@method_decorator([login_required, admin_required], name='dispatch')
class PermissionAdminDeleteView(DeleteView):
    """Admin delete view for Permissions"""
    model = Permission
    template_name = 'accounts/admin/permission_confirm_delete.html'
    success_url = reverse_lazy('accounts:admin_permission_list')
    
    def delete(self, request, *args, **kwargs):
        permission = self.get_object()
        messages.success(self.request, f"Permission {permission.name} deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ LoginHistory Admin View (Read-only) ============

@method_decorator([login_required, admin_required], name='dispatch')
class LoginHistoryAdminListView(ListView):
    """Admin list view for Login History (read-only)"""
    model = LoginHistory
    template_name = 'accounts/admin/login_history_list.html'
    context_object_name = 'login_histories'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = LoginHistory.objects.select_related('user').all()
        
        # Filter by user
        user = self.request.GET.get('user')
        if user:
            queryset = queryset.filter(user_id=user)
        
        return queryset.order_by('-login_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        context['selected_user'] = self.request.GET.get('user', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class LoginHistoryAdminDetailView(DetailView):
    """Admin detail view for Login History"""
    model = LoginHistory
    template_name = 'accounts/admin/login_history_detail.html'
    context_object_name = 'login_history'
