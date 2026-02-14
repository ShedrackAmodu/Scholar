from django.urls import path
from . import views

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
    
    # API URLs
    path('api/summary/<int:student_id>/', views.get_attendance_summary, name='get_attendance_summary'),
    path('api/close/<int:session_id>/', views.close_attendance_session, name='close_attendance_session'),
]
