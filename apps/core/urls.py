"""
URL patterns for the core app
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('search/', views.search_view, name='search'),
    path('theme-toggle/', views.theme_toggle_view, name='theme_toggle'),
]