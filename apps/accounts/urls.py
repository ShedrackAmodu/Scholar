from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('profile/', views.profile_view, name='profile'),
    path('password-reset/', views.password_reset, name='password_reset'),
    
    # Admin URLs
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/users/create/', views.user_create, name='user_create'),
    path('admin/users/<int:pk>/', views.user_detail, name='user_detail'),
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