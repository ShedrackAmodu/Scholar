from django.urls import path
from . import views
from . import admin_views

app_name = 'parents'

urlpatterns = [
    # Parent URLs
    path('dashboard/', views.parent_dashboard, name='parent_dashboard'),
    path('children/', views.parent_dashboard, name='children_list'),  # reuse dashboard to list children
    path('children/<int:child_id>/', views.child_dashboard, name='child_detail'),
    path('children/<int:child_id>/scores/', views.child_scores, name='child_scores'),
    path('children/<int:child_id>/attendance/', views.child_attendance, name='child_attendance'),
    path('children/<int:child_id>/report-cards/', views.child_report_cards, name='child_report_cards'),
    
    # Admin URLs
    path('admin/', views.ParentListView.as_view(), name='parent_list'),
    path('admin/create/', views.ParentCreateView.as_view(), name='parent_create'),
    path('admin/<int:pk>/', views.ParentDetailView.as_view(), name='parent_detail'),
    path('admin/<int:pk>/edit/', views.ParentUpdateView.as_view(), name='parent_edit'),
    path('admin/<int:pk>/delete/', views.ParentDeleteView.as_view(), name='parent_delete'),
    path('admin/bulk/', views.bulk_link_parents, name='bulk_parent'),
    path('admin/link/', views.link_parent_to_student, name='link_parent'),
    path('admin/unlink/<int:pk>/', views.unlink_parent_from_student, name='unlink_parent'),

    # Admin CRUD routes for Django admin models
    path('admin/crud/parents/', admin_views.ParentAdminListView.as_view(), name='admin_parent_list'),
    path('admin/crud/parents/create/', admin_views.ParentAdminCreateView.as_view(), name='admin_parent_create'),
    path('admin/crud/parents/<int:pk>/', admin_views.ParentAdminDetailView.as_view(), name='admin_parent_detail'),
    path('admin/crud/parents/<int:pk>/edit/', admin_views.ParentAdminUpdateView.as_view(), name='admin_parent_edit'),
    path('admin/crud/parents/<int:pk>/delete/', admin_views.ParentAdminDeleteView.as_view(), name='admin_parent_delete'),
    
    path('admin/crud/relationships/', admin_views.ParentStudentRelationshipAdminListView.as_view(), name='admin_parentstudentrelationship_list'),
    path('admin/crud/relationships/create/', admin_views.ParentStudentRelationshipAdminCreateView.as_view(), name='admin_parentstudentrelationship_create'),
    path('admin/crud/relationships/<int:pk>/', admin_views.ParentStudentRelationshipAdminDetailView.as_view(), name='admin_parentstudentrelationship_detail'),
    path('admin/crud/relationships/<int:pk>/edit/', admin_views.ParentStudentRelationshipAdminUpdateView.as_view(), name='admin_parentstudentrelationship_edit'),
    path('admin/crud/relationships/<int:pk>/delete/', admin_views.ParentStudentRelationshipAdminDeleteView.as_view(), name='admin_parentstudentrelationship_delete'),

    # API URLs
    path('api/children/', views.get_parent_children, name='api_get_parent_children'),
    path('api/search/', views.search_parents, name='api_search_parents'),
]
