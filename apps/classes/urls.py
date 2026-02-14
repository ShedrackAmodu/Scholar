from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    # Teacher URLs
    path('teacher/', views.teacher_classes, name='teacher_classes'),
    path('teacher/class/<int:class_id>/students/', views.class_students, name='class_students'),
    
    # Admin URLs
    path('admin/', views.ClassListView.as_view(), name='class_list'),
    path('admin/create/', views.ClassCreateView.as_view(), name='class_create'),
    path('admin/<int:pk>/edit/', views.ClassUpdateView.as_view(), name='class_edit'),
    path('admin/<int:pk>/delete/', views.ClassDeleteView.as_view(), name='class_delete'),
    path('admin/<int:pk>/', views.ClassDetailView.as_view(), name='class_detail'),
    
    # Class Level URLs
    path('levels/', views.ClassLevelListView.as_view(), name='class_level_list'),
    path('levels/create/', views.ClassLevelCreateView.as_view(), name='class_level_create'),
    path('levels/<int:pk>/edit/', views.ClassLevelUpdateView.as_view(), name='class_level_edit'),
    path('levels/<int:pk>/delete/', views.ClassLevelDeleteView.as_view(), name='class_level_delete'),
    
    # Subject URLs
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/create/', views.SubjectCreateView.as_view(), name='subject_create'),
    path('subjects/<int:pk>/edit/', views.SubjectUpdateView.as_view(), name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.SubjectDeleteView.as_view(), name='subject_delete'),
    
    # Subject Allocation URLs
    path('allocations/', views.SubjectAllocationListView.as_view(), name='allocation_list'),
    path('allocations/create/', views.SubjectAllocationCreateView.as_view(), name='allocation_create'),
    path('allocations/<int:pk>/edit/', views.SubjectAllocationUpdateView.as_view(), name='allocation_edit'),
    path('allocations/<int:pk>/delete/', views.SubjectAllocationDeleteView.as_view(), name='allocation_delete'),
    
    # Bulk Operations
    path('bulk/assignment/', views.bulk_class_assignment, name='bulk_class_assignment'),
    
    # API URLs
    path('api/subjects/', views.get_subjects_for_class, name='get_subjects_for_class'),
    path('api/teachers/', views.get_teachers_for_subject, name='get_teachers_for_subject'),
]
