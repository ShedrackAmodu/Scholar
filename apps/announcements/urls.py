from django.urls import path
from django.views.generic import RedirectView
from . import views
from . import admin_views

app_name = 'announcements'

urlpatterns = [
    # Public URLs
    path('', views.noticeboard, name='noticeboard'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('notices/<int:notice_id>/', views.notice_detail, name='notice_detail'),
    
    # Event CRUD
    path('admin/events/', views.EventListView.as_view(), name='event_list'),
    path('admin/events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('admin/events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('admin/events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_edit'),
    path('admin/events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    
    # Notice CRUD
    path('admin/notices/', views.NoticeListView.as_view(), name='notice_list'),
    path('admin/notices/create/', views.NoticeCreateView.as_view(), name='notice_create'),
    path('admin/notices/<int:pk>/', views.NoticeDetailView.as_view(), name='notice_detail'),
    path('admin/notices/<int:pk>/edit/', views.NoticeUpdateView.as_view(), name='notice_edit'),
    path('admin/notices/<int:pk>/delete/', views.NoticeDeleteView.as_view(), name='notice_delete'),
    
    # Assignment CRUD
    path('admin/assignments/', views.AssignmentListView.as_view(), name='assignment_list'),
    path('admin/assignments/create/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('admin/assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('admin/assignments/<int:pk>/edit/', views.AssignmentUpdateView.as_view(), name='assignment_edit'),
    path('admin/assignments/<int:pk>/delete/', views.AssignmentDeleteView.as_view(), name='assignment_delete'),
    
    # Admin CRUD routes for Django admin models
    path('admin/crud/events/', admin_views.EventAdminListView.as_view(), name='admin_event_list'),
    path('admin/crud/events/create/', admin_views.EventAdminCreateView.as_view(), name='admin_event_create'),
    path('admin/crud/events/<int:pk>/', admin_views.EventAdminDetailView.as_view(), name='admin_event_detail'),
    path('admin/crud/events/<int:pk>/edit/', admin_views.EventAdminUpdateView.as_view(), name='admin_event_edit'),
    path('admin/crud/events/<int:pk>/delete/', admin_views.EventAdminDeleteView.as_view(), name='admin_event_delete'),
    
    path('admin/crud/notices/', admin_views.NoticeAdminListView.as_view(), name='admin_notice_list'),
    path('admin/crud/notices/create/', admin_views.NoticeAdminCreateView.as_view(), name='admin_notice_create'),
    path('admin/crud/notices/<int:pk>/', admin_views.NoticeAdminDetailView.as_view(), name='admin_notice_detail'),
    path('admin/crud/notices/<int:pk>/edit/', admin_views.NoticeAdminUpdateView.as_view(), name='admin_notice_edit'),
    path('admin/crud/notices/<int:pk>/delete/', admin_views.NoticeAdminDeleteView.as_view(), name='admin_notice_delete'),
    
    path('admin/crud/assignments/', admin_views.AssignmentAdminListView.as_view(), name='admin_assignment_list'),
    path('admin/crud/assignments/create/', admin_views.AssignmentAdminCreateView.as_view(), name='admin_assignment_create'),
    path('admin/crud/assignments/<int:pk>/', admin_views.AssignmentAdminDetailView.as_view(), name='admin_assignment_detail'),
    path('admin/crud/assignments/<int:pk>/edit/', admin_views.AssignmentAdminUpdateView.as_view(), name='admin_assignment_edit'),
    path('admin/crud/assignments/<int:pk>/delete/', admin_views.AssignmentAdminDeleteView.as_view(), name='admin_assignment_delete'),
    
    path('admin/crud/submissions/', admin_views.AssignmentSubmissionAdminListView.as_view(), name='admin_assignmentsubmission_list'),
    path('admin/crud/submissions/<int:pk>/', admin_views.AssignmentSubmissionAdminDetailView.as_view(), name='admin_assignmentsubmission_detail'),
    
    path('admin/crud/notifications/', admin_views.NotificationAdminListView.as_view(), name='admin_notification_list'),
    path('admin/crud/notifications/<int:pk>/', admin_views.NotificationAdminDetailView.as_view(), name='admin_notification_detail'),
    
    path('admin/crud/messages/', admin_views.ClassMessageAdminListView.as_view(), name='admin_classmessage_list'),
    path('admin/crud/messages/create/', admin_views.ClassMessageAdminCreateView.as_view(), name='admin_classmessage_create'),
    path('admin/crud/messages/<int:pk>/', admin_views.ClassMessageAdminDetailView.as_view(), name='admin_classmessage_detail'),
    path('admin/crud/messages/<int:pk>/delete/', admin_views.ClassMessageAdminDeleteView.as_view(), name='admin_classmessage_delete'),
    
    # Legacy URLs - Redirected for backward compatibility
    # These views are no longer needed as we use proper CRUD views instead
    path('admin/create-notice/', RedirectView.as_view(url='/announcements/admin/notices/create/', permanent=False), name='create_notice'),
    path('admin/create-event/', RedirectView.as_view(url='/announcements/admin/events/create/', permanent=False), name='create_event'),
    path('admin/api/', views.announcements_api, name='announcements_api'),
]
