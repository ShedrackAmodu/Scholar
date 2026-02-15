from django.urls import path
from . import views

app_name = 'admissions'

urlpatterns = [
    # Public URLs
    path('', views.admissions_home, name='admission_form'),
    path('apply/', views.ApplicationCreateView.as_view(), name='application_create'),
    path('guidelines/', views.admissions_home, name='admission_guidelines'),
    path('requirements/', views.admissions_home, name='admission_requirements'),
    path('status/', views.admissions_home, name='admission_status'),
    path('api/', views.application_api, name='application_api'),

    # Admin URLs - Applications
    path('admin/', views.ApplicationListView.as_view(), name='admission_list'),
    path('admin/applications/', views.ApplicationListView.as_view(), name='application_list'),
    path('admin/<int:pk>/', views.ApplicationDetailView.as_view(), name='admission_detail'),
    path('admin/applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('admin/applications/<int:pk>/edit/', views.ApplicationUpdateView.as_view(), name='application_edit'),
    path('admin/applications/<int:pk>/delete/', views.ApplicationDeleteView.as_view(), name='application_delete'),
    
    # Admin URLs - Entrance Exams
    path('admin/entrance-exams/', views.EntranceExamListView.as_view(), name='entrance_exam_list'),
    path('admin/entrance-exams/create/', views.EntranceExamCreateView.as_view(), name='entrance_exam_create'),
    path('admin/entrance-exams/<int:pk>/', views.EntranceExamDetailView.as_view(), name='entrance_exam_detail'),
    path('admin/entrance-exams/<int:pk>/edit/', views.EntranceExamUpdateView.as_view(), name='entrance_exam_edit'),
    path('admin/entrance-exams/<int:pk>/delete/', views.EntranceExamDeleteView.as_view(), name='entrance_exam_delete'),
    
    # Legacy URLs (kept for backward compatibility)
    path('admin/schedule-exam/<int:app_id>/', views.schedule_exam, name='schedule_exam'),
    path('admin/bulk/', views.bulk_admission, name='bulk_admission'),
]
