from django.urls import path
from . import views
from . import admin_views

app_name = 'academics'

urlpatterns = [
    # Student URLs (students view their own performance; parents can specify a student_id)
    path('student/performance/<int:student_id>/', views.student_performance, name='student_performance'),
    path('student/performance/', views.student_performance, name='student_performance'),

    # Teacher URLs
    path('teacher/score-entry/', views.score_entry, name='score_entry'),
    path('teacher/score-entry/bulk/', views.bulk_score_entry, name='bulk_score_entry'),
    path('teacher/score-entry/individual/', views.individual_score_entry, name='individual_score_entry'),
    path('teacher/score-entry/edit/<int:class_id>/<int:subject_id>/', views.edit_scores, name='edit_scores'),
    path('teacher/score-entry/approve/<int:class_id>/<int:subject_id>/', views.approve_scores, name='approve_scores'),
    path('teacher/score-entry/save/', views.save_scores_ajax, name='save_scores_ajax'),

    path('teacher/report-cards/', views.report_card_list, name='report_card_list'),
    path('teacher/report-cards/<int:class_id>/', views.report_card_list, name='report_card_list'),
    path('teacher/report-cards/generate/', views.generate_report_cards, name='generate_report_cards'),
    path('teacher/report-cards/<int:pk>/', views.view_report_card, name='report_card_detail'),
    # PDF download for individual report card (teachers, students, parents)
    path('teacher/report-cards/<int:pk>/download/', views.download_report_card_pdf, name='download_report_card_pdf'),

    # Principal URLs
    path('principal/class-performance/', views.class_performance, name='class_performance'),
    path('principal/class-performance/<int:class_id>/<int:term>/<int:year_id>/', views.class_performance_detail, name='class_performance_detail'),
    path('principal/approve-report-cards/<int:class_id>/', views.approve_report_cards, name='approve_report_cards'),

    # Calendar URL
    path('academic-calendar/', views.academic_calendar, name='academic_calendar'),

    # API URLs
    path('api/assessments/', views.get_assessments_for_subject, name='api_get_assessments_for_subject'),
    path('api/students-with-scores/', views.get_students_with_scores, name='api_get_students_with_scores'),

    # Admin URLs (existing)
    path('admin/assessments/', views.AssessmentListView.as_view(), name='assessment_list'),
    path('admin/assessments/create/', views.AssessmentCreateView.as_view(), name='assessment_create'),
    path('admin/assessments/<int:pk>/edit/', views.AssessmentUpdateView.as_view(), name='assessment_edit'),
    path('admin/assessments/<int:pk>/delete/', views.AssessmentDeleteView.as_view(), name='assessment_delete'),
    path('admin/subject-assessments/', views.SubjectAssessmentListView.as_view(), name='subject_assessment_list'),
    path('admin/subject-assessments/create/', views.SubjectAssessmentCreateView.as_view(), name='subject_assessment_create'),
    path('admin/subject-assessments/<int:pk>/edit/', views.SubjectAssessmentUpdateView.as_view(), name='subject_assessment_edit'),
    path('admin/subject-assessments/<int:pk>/delete/', views.SubjectAssessmentDeleteView.as_view(), name='subject_assessment_delete'),

    # New Admin CRUD URLs (mirroring Django admin)
    path('admin/crud/assessments/', admin_views.AssessmentAdminListView.as_view(), name='admin_assessment_list'),
    path('admin/crud/assessments/create/', admin_views.AssessmentAdminCreateView.as_view(), name='admin_assessment_create'),
    path('admin/crud/assessments/<int:pk>/edit/', admin_views.AssessmentAdminUpdateView.as_view(), name='admin_assessment_edit'),
    path('admin/crud/assessments/<int:pk>/', admin_views.AssessmentAdminDetailView.as_view(), name='admin_assessment_detail'),
    path('admin/crud/assessments/<int:pk>/delete/', admin_views.AssessmentAdminDeleteView.as_view(), name='admin_assessment_delete'),

    path('admin/crud/subject-assessments/', admin_views.SubjectAssessmentAdminListView.as_view(), name='admin_subject_assessment_list'),
    path('admin/crud/subject-assessments/create/', admin_views.SubjectAssessmentAdminCreateView.as_view(), name='admin_subject_assessment_create'),
    path('admin/crud/subject-assessments/<int:pk>/edit/', admin_views.SubjectAssessmentAdminUpdateView.as_view(), name='admin_subject_assessment_edit'),
    path('admin/crud/subject-assessments/<int:pk>/', admin_views.SubjectAssessmentAdminDetailView.as_view(), name='admin_subject_assessment_detail'),
    path('admin/crud/subject-assessments/<int:pk>/delete/', admin_views.SubjectAssessmentAdminDeleteView.as_view(), name='admin_subject_assessment_delete'),

    path('admin/crud/scores/', admin_views.ScoreAdminListView.as_view(), name='admin_score_list'),
    path('admin/crud/scores/<int:pk>/', admin_views.ScoreAdminDetailView.as_view(), name='admin_score_detail'),
    path('admin/crud/scores/<int:pk>/delete/', admin_views.ScoreAdminDeleteView.as_view(), name='admin_score_delete'),

    path('admin/crud/subject-scores/', admin_views.SubjectScoreAdminListView.as_view(), name='admin_subject_score_list'),
    path('admin/crud/subject-scores/<int:pk>/', admin_views.SubjectScoreAdminDetailView.as_view(), name='admin_subject_score_detail'),

    path('admin/crud/report-cards/', admin_views.ReportCardAdminListView.as_view(), name='admin_report_card_list'),
    path('admin/crud/report-cards/<int:pk>/', admin_views.ReportCardAdminDetailView.as_view(), name='admin_report_card_detail'),
    path('admin/crud/report-cards/<int:pk>/delete/', admin_views.ReportCardAdminDeleteView.as_view(), name='admin_report_card_delete'),

    path('admin/crud/class-performances/', admin_views.ClassPerformanceAdminListView.as_view(), name='admin_class_performance_list'),
    path('admin/crud/class-performances/<int:pk>/', admin_views.ClassPerformanceAdminDetailView.as_view(), name='admin_class_performance_detail'),
    path('admin/crud/class-performances/<int:pk>/delete/', admin_views.ClassPerformanceAdminDeleteView.as_view(), name='admin_class_performance_delete'),
]
