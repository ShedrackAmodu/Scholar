from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    # Teacher URLs
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('schedule/', views.teacher_schedule, name='teacher_schedule'),
    path('leave/', views.teacher_leave_list, name='teacher_leave_list'),
    path('leave/create/', views.teacher_leave_create, name='teacher_leave_create'),
    path('leave/approve/<int:pk>/', views.approve_leave, name='approve_leave'),
    
    # Admin URLs
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
