from django.urls import path
from . import views
from . import admin_views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('profile/', views.profile_view, name='profile'),
    path('password-reset/', views.password_reset, name='password_reset'),
    
    # Admin Dashboard
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Admin CRUD URLs for Users
    path('admin/crud/users/', admin_views.UserAdminListView.as_view(), name='admin_user_list'),
    path('admin/crud/users/create/', admin_views.UserAdminCreateView.as_view(), name='admin_user_create'),
    path('admin/crud/users/<int:pk>/', admin_views.UserAdminDetailView.as_view(), name='admin_user_detail'),
    path('admin/crud/users/<int:pk>/edit/', admin_views.UserAdminUpdateView.as_view(), name='admin_user_edit'),
    path('admin/crud/users/<int:pk>/delete/', admin_views.UserAdminDeleteView.as_view(), name='admin_user_delete'),
    
    # Admin CRUD URLs for Roles
    path('admin/crud/roles/', admin_views.RoleAdminListView.as_view(), name='admin_role_list'),
    path('admin/crud/roles/create/', admin_views.RoleAdminCreateView.as_view(), name='admin_role_create'),
    path('admin/crud/roles/<int:pk>/', admin_views.RoleAdminDetailView.as_view(), name='admin_role_detail'),
    path('admin/crud/roles/<int:pk>/edit/', admin_views.RoleAdminUpdateView.as_view(), name='admin_role_edit'),
    path('admin/crud/roles/<int:pk>/delete/', admin_views.RoleAdminDeleteView.as_view(), name='admin_role_delete'),
    
    # Admin CRUD URLs for Permissions
    path('admin/crud/permissions/', admin_views.PermissionAdminListView.as_view(), name='admin_permission_list'),
    path('admin/crud/permissions/create/', admin_views.PermissionAdminCreateView.as_view(), name='admin_permission_create'),
    path('admin/crud/permissions/<int:pk>/', admin_views.PermissionAdminDetailView.as_view(), name='admin_permission_detail'),
    path('admin/crud/permissions/<int:pk>/edit/', admin_views.PermissionAdminUpdateView.as_view(), name='admin_permission_edit'),
    path('admin/crud/permissions/<int:pk>/delete/', admin_views.PermissionAdminDeleteView.as_view(), name='admin_permission_delete'),
    
    # Admin View URLs for Login History (read-only)
    path('admin/crud/login-history/', admin_views.LoginHistoryAdminListView.as_view(), name='admin_login_history_list'),
    path('admin/crud/login-history/<int:pk>/', admin_views.LoginHistoryAdminDetailView.as_view(), name='admin_login_history_detail'),
    
    # Legacy function-based URLs (kept for backward compatibility)
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/users/create/', views.user_create, name='user_create'),
    path('admin/users/<int:pk>/detail/', views.user_detail, name='user_detail'),
    path('admin/users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('admin/users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('admin/roles/', views.role_list, name='role_list'),
    path('admin/roles/create/', views.role_create, name='role_create'),
    path('admin/roles/<int:pk>/edit/', views.role_edit, name='role_edit'),
    path('admin/roles/<int:pk>/delete/', views.role_delete, name='role_delete'),

    # Role‑based dashboards (used by redirect logic)
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/parent/', views.parent_dashboard, name='parent_dashboard'),
    path('dashboard/principal/', views.principal_dashboard, name='principal_dashboard'),
    path('dashboard/vice-principal/', views.vice_principal_dashboard, name='vice_principal_dashboard'),
    path('dashboard/director/', views.director_dashboard, name='director_dashboard'),
]