from django.urls import path
from . import views
from . import admin_views

app_name = 'attendance'

urlpatterns = [
    # Student URLs
    path('student/', views.view_attendance, name='view_attendance'),
    
    # Parent URLs
    path('parent/history/', views.attendance_history, name='parent_attendance_history'),
    
    # Teacher URLs
    path('teacher/', views.take_attendance, name='teacher_attendance'),
    path('teacher/mark/<int:session_id>/', views.mark_attendance, name='mark_attendance'),
    path('teacher/history/', views.attendance_history, name='teacher_history'),
    
    # Admin URLs
    path('admin/', views.attendance_history, name='attendance_list'),
    path('admin/report/', views.attendance_report, name='attendance_report'),
    
    # Admin CRUD routes for Django admin models
    path('admin/crud/sessions/', admin_views.AttendanceSessionAdminListView.as_view(), name='admin_attendancesession_list'),
    path('admin/crud/sessions/create/', admin_views.AttendanceSessionAdminCreateView.as_view(), name='admin_attendancesession_create'),
    path('admin/crud/sessions/<int:pk>/', admin_views.AttendanceSessionAdminDetailView.as_view(), name='admin_attendancesession_detail'),
    path('admin/crud/sessions/<int:pk>/delete/', admin_views.AttendanceSessionAdminDeleteView.as_view(), name='admin_attendancesession_delete'),
    
    path('admin/crud/records/', admin_views.AttendanceAdminListView.as_view(), name='admin_attendance_list'),
    path('admin/crud/records/<int:pk>/', admin_views.AttendanceAdminDetailView.as_view(), name='admin_attendance_detail'),
    path('admin/crud/records/<int:pk>/edit/', admin_views.AttendanceAdminUpdateView.as_view(), name='admin_attendance_edit'),
    path('admin/crud/records/<int:pk>/delete/', admin_views.AttendanceAdminDeleteView.as_view(), name='admin_attendance_delete'),
    
    path('admin/crud/summaries/', admin_views.AttendanceSummaryAdminListView.as_view(), name='admin_attendancesummary_list'),
    path('admin/crud/summaries/<int:pk>/', admin_views.AttendanceSummaryAdminDetailView.as_view(), name='admin_attendancesummary_detail'),
    
    # API URLs
    path('api/summary/<int:student_id>/', views.get_attendance_summary, name='get_attendance_summary'),
    path('api/close/<int:session_id>/', views.close_attendance_session, name='close_attendance_session'),
]
