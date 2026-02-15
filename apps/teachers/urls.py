from django.urls import path
from . import views
from . import admin_views

app_name = 'teachers'

urlpatterns = [
    # Teacher URLs
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('schedule/', views.teacher_schedule, name='teacher_schedule'),
    path('leave/', views.teacher_leave_list, name='teacher_leave_list'),
    path('leave/create/', views.teacher_leave_create, name='teacher_leave_create'),
    path('leave/approve/<int:pk>/', views.approve_leave, name='approve_leave'),
    
    # Admin CRUD URLs for Teachers
    path('admin/crud/teachers/', admin_views.TeacherAdminListView.as_view(), name='admin_teacher_list'),
    path('admin/crud/teachers/create/', admin_views.TeacherAdminCreateView.as_view(), name='admin_teacher_create'),
    path('admin/crud/teachers/<int:pk>/', admin_views.TeacherAdminDetailView.as_view(), name='admin_teacher_detail'),
    path('admin/crud/teachers/<int:pk>/edit/', admin_views.TeacherAdminUpdateView.as_view(), name='admin_teacher_edit'),
    path('admin/crud/teachers/<int:pk>/delete/', admin_views.TeacherAdminDeleteView.as_view(), name='admin_teacher_delete'),
    
    # Admin CRUD URLs for Teacher Qualifications
    path('admin/crud/qualifications/', admin_views.TeacherQualificationAdminListView.as_view(), name='admin_teacher_qualification_list'),
    path('admin/crud/qualifications/create/', admin_views.TeacherQualificationAdminCreateView.as_view(), name='admin_teacher_qualification_create'),
    path('admin/crud/qualifications/<int:pk>/', admin_views.TeacherQualificationAdminDetailView.as_view(), name='admin_teacher_qualification_detail'),
    path('admin/crud/qualifications/<int:pk>/edit/', admin_views.TeacherQualificationAdminUpdateView.as_view(), name='admin_teacher_qualification_edit'),
    path('admin/crud/qualifications/<int:pk>/delete/', admin_views.TeacherQualificationAdminDeleteView.as_view(), name='admin_teacher_qualification_delete'),
    
    # Admin CRUD URLs for Teacher Subject Expertise
    path('admin/crud/expertise/', admin_views.TeacherSubjectExpertiseAdminListView.as_view(), name='admin_teacher_subject_expertise_list'),
    path('admin/crud/expertise/create/', admin_views.TeacherSubjectExpertiseAdminCreateView.as_view(), name='admin_teacher_subject_expertise_create'),
    path('admin/crud/expertise/<int:pk>/', admin_views.TeacherSubjectExpertiseAdminDetailView.as_view(), name='admin_teacher_subject_expertise_detail'),
    path('admin/crud/expertise/<int:pk>/edit/', admin_views.TeacherSubjectExpertiseAdminUpdateView.as_view(), name='admin_teacher_subject_expertise_edit'),
    path('admin/crud/expertise/<int:pk>/delete/', admin_views.TeacherSubjectExpertiseAdminDeleteView.as_view(), name='admin_teacher_subject_expertise_delete'),
    
    # Admin CRUD URLs for Teacher Leaves
    path('admin/crud/leaves/', admin_views.TeacherLeaveAdminListView.as_view(), name='admin_teacher_leave_list'),
    path('admin/crud/leaves/create/', admin_views.TeacherLeaveAdminCreateView.as_view(), name='admin_teacher_leave_create'),
    path('admin/crud/leaves/<int:pk>/', admin_views.TeacherLeaveAdminDetailView.as_view(), name='admin_teacher_leave_detail'),
    path('admin/crud/leaves/<int:pk>/edit/', admin_views.TeacherLeaveAdminUpdateView.as_view(), name='admin_teacher_leave_edit'),
    path('admin/crud/leaves/<int:pk>/delete/', admin_views.TeacherLeaveAdminDeleteView.as_view(), name='admin_teacher_leave_delete'),
    
    # Legacy function-based URLs (kept for backward compatibility)
    path('admin/', views.TeacherListView.as_view(), name='teacher_list'),
    path('admin/create/', views.TeacherCreateView.as_view(), name='teacher_create'),
    path('admin/<int:pk>/', views.TeacherDetailView.as_view(), name='teacher_detail'),
    path('admin/<int:pk>/edit/', views.TeacherUpdateView.as_view(), name='teacher_edit'),
    path('admin/<int:pk>/delete/', views.TeacherDeleteView.as_view(), name='teacher_delete'),
    path('admin/qualifications/add/<int:teacher_id>/', views.add_qualification, name='add_qualification'),
    path('admin/qualifications/delete/<int:pk>/', views.delete_qualification, name='delete_qualification'),
    path('admin/expertise/add/<int:teacher_id>/', views.add_expertise, name='add_expertise'),
    path('admin/expertise/delete/<int:pk>/', views.delete_expertise, name='delete_expertise'),
    path('admin/bulk-upload/', views.bulk_teacher_upload, name='bulk_teacher_upload'),
    path('admin/get-subjects/<int:teacher_id>/', views.get_teacher_subjects, name='get_teacher_subjects'),
    path('admin/get-allocations/<int:teacher_id>/', views.get_teacher_allocations, name='get_teacher_allocations'),
]

