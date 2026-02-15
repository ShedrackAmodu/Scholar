from django.urls import path
from django.views.generic import RedirectView
from . import views

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
    
    # Legacy URLs - Redirected for backward compatibility
    # These views are no longer needed as we use proper CRUD views instead
    path('admin/create-notice/', RedirectView.as_view(url='/announcements/admin/notices/create/', permanent=False), name='create_notice'),
    path('admin/create-event/', RedirectView.as_view(url='/announcements/admin/events/create/', permanent=False), name='create_event'),
    path('admin/api/', views.announcements_api, name='announcements_api'),
]
