from django.urls import path
from . import views
from . import admin_views

app_name = 'students'

urlpatterns = [
    # Student URLs
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('documents/', views.student_documents, name='student_documents'),
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('scores/', views.student_scores, name='student_scores'),
    path('attendance/', views.student_attendance, name='student_attendance'),
    path('report-cards/', views.student_report_cards, name='student_report_cards'),
    
    # Admin CRUD URLs for Students
    path('admin/crud/students/', admin_views.StudentAdminListView.as_view(), name='admin_student_list'),
    path('admin/crud/students/create/', admin_views.StudentAdminCreateView.as_view(), name='admin_student_create'),
    path('admin/crud/students/<int:pk>/', admin_views.StudentAdminDetailView.as_view(), name='admin_student_detail'),
    path('admin/crud/students/<int:pk>/edit/', admin_views.StudentAdminUpdateView.as_view(), name='admin_student_edit'),
    path('admin/crud/students/<int:pk>/delete/', admin_views.StudentAdminDeleteView.as_view(), name='admin_student_delete'),
    
    # Admin CRUD URLs for Student Documents
    path('admin/crud/documents/', admin_views.StudentDocumentAdminListView.as_view(), name='admin_student_document_list'),
    path('admin/crud/documents/create/', admin_views.StudentDocumentAdminCreateView.as_view(), name='admin_student_document_create'),
    path('admin/crud/documents/<int:pk>/', admin_views.StudentDocumentAdminDetailView.as_view(), name='admin_student_document_detail'),
    path('admin/crud/documents/<int:pk>/delete/', admin_views.StudentDocumentAdminDeleteView.as_view(), name='admin_student_document_delete'),
    
    # Admin CRUD URLs for Student History
    path('admin/crud/histories/', admin_views.StudentHistoryAdminListView.as_view(), name='admin_student_history_list'),
    path('admin/crud/histories/create/', admin_views.StudentHistoryAdminCreateView.as_view(), name='admin_student_history_create'),
    path('admin/crud/histories/<int:pk>/', admin_views.StudentHistoryAdminDetailView.as_view(), name='admin_student_history_detail'),
    path('admin/crud/histories/<int:pk>/edit/', admin_views.StudentHistoryAdminUpdateView.as_view(), name='admin_student_history_edit'),
    path('admin/crud/histories/<int:pk>/delete/', admin_views.StudentHistoryAdminDeleteView.as_view(), name='admin_student_history_delete'),
    
    # Legacy function-based URLs (kept for backward compatibility)
    path('admin/', views.StudentListView.as_view(), name='student_list'),
    path('admin/create/', views.StudentCreateView.as_view(), name='student_create'),
    path('admin/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('admin/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_edit'),
    path('admin/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    path('admin/enrollment/', views.student_enrollment, name='student_enrollment'),
    path('admin/bulk-upload/', views.bulk_student_upload, name='bulk_student_upload'),
    path('admin/get-students/', views.get_students_for_class, name='get_students_for_class'),
    path('admin/promote/', views.promote_students, name='promote_students'),
]

