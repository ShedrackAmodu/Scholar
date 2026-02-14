from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Student URLs
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('documents/', views.student_documents, name='student_documents'),
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('scores/', views.student_scores, name='student_scores'),
    path('attendance/', views.student_attendance, name='student_attendance'),
    path('report-cards/', views.student_report_cards, name='student_report_cards'),
    
    # Admin URLs
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
