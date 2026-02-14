from django.urls import path
from . import views

app_name = 'announcements'

urlpatterns = [
    # Public URLs
    path('', views.noticeboard, name='noticeboard'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('notices/<int:notice_id>/', views.notice_detail, name='notice_detail'),
    
    # Admin URLs
    path('admin/create-notice/', views.create_notice, name='create_notice'),
    path('admin/create-event/', views.create_event, name='create_event'),
    path('admin/api/', views.announcements_api, name='announcements_api'),
]
