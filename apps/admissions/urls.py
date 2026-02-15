from django.urls import path
from . import views
from . import admin_views

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
    
    # Admin CRUD routes for Django admin models
    path('admin/crud/applications/', admin_views.ApplicationAdminListView.as_view(), name='admin_application_list'),
    path('admin/crud/applications/create/', admin_views.ApplicationAdminCreateView.as_view(), name='admin_application_create'),
    path('admin/crud/applications/<int:pk>/', admin_views.ApplicationAdminDetailView.as_view(), name='admin_application_detail'),
    path('admin/crud/applications/<int:pk>/edit/', admin_views.ApplicationAdminUpdateView.as_view(), name='admin_application_edit'),
    path('admin/crud/applications/<int:pk>/delete/', admin_views.ApplicationAdminDeleteView.as_view(), name='admin_application_delete'),
    
    path('admin/crud/entrance-exams/', admin_views.EntranceExamAdminListView.as_view(), name='admin_entranceexam_list'),
    path('admin/crud/entrance-exams/create/', admin_views.EntranceExamAdminCreateView.as_view(), name='admin_entranceexam_create'),
    path('admin/crud/entrance-exams/<int:pk>/', admin_views.EntranceExamAdminDetailView.as_view(), name='admin_entranceexam_detail'),
    path('admin/crud/entrance-exams/<int:pk>/edit/', admin_views.EntranceExamAdminUpdateView.as_view(), name='admin_entranceexam_edit'),
    path('admin/crud/entrance-exams/<int:pk>/delete/', admin_views.EntranceExamAdminDeleteView.as_view(), name='admin_entranceexam_delete'),
    
    path('admin/crud/comments/', admin_views.ApplicationCommentAdminListView.as_view(), name='admin_applicationcomment_list'),
    path('admin/crud/comments/<int:pk>/', admin_views.ApplicationCommentAdminDetailView.as_view(), name='admin_applicationcomment_detail'),
    path('admin/crud/comments/<int:pk>/delete/', admin_views.ApplicationCommentAdminDeleteView.as_view(), name='admin_applicationcomment_delete'),
    
    # Legacy URLs (kept for backward compatibility)
    path('admin/schedule-exam/<int:app_id>/', views.schedule_exam, name='schedule_exam'),
    path('admin/bulk/', views.bulk_admission, name='bulk_admission'),
]
