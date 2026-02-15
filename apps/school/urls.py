from django.urls import path
from . import views
from . import admin_views

app_name = 'school'

urlpatterns = [
    # public pages
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about'),
    path('contact/', views.contact_us, name='contact'),
    path('noticeboard/', views.noticeboard, name='noticeboard'),
    path('events/', views.events, name='events'),

    # Admin / backend pages (accessible to administrators)
    path('admin/settings/', views.school_settings, name='settings'),
    path('admin/hours/', views.school_hours, name='school_hours'),

    # Academic year CRUD
    path('admin/academic-years/', views.AcademicYearListView.as_view(), name='academic_year_list'),
    path('admin/academic-years/create/', views.AcademicYearCreateView.as_view(), name='academic_year_create'),
    path('admin/academic-years/<int:pk>/', views.AcademicYearDetailView.as_view(), name='academic_year_detail'),
    path('admin/academic-years/<int:pk>/edit/', views.AcademicYearUpdateView.as_view(), name='academic_year_edit'),
    path('admin/academic-years/<int:pk>/delete/', views.AcademicYearDeleteView.as_view(), name='academic_year_delete'),
    path('admin/academic-years/set-current/', views.set_current_academic_year, name='set_current_academic_year'),

    # Term CRUD
    path('admin/terms/', views.TermListView.as_view(), name='term_list'),
    path('admin/terms/create/', views.TermCreateView.as_view(), name='term_create'),
    path('admin/terms/<int:pk>/', views.TermDetailView.as_view(), name='term_detail'),
    path('admin/terms/<int:pk>/edit/', views.TermUpdateView.as_view(), name='term_edit'),
    path('admin/terms/<int:pk>/delete/', views.TermDeleteView.as_view(), name='term_delete'),
    path('admin/terms/set-current/', views.set_current_term, name='set_current_term'),

    # Holiday CRUD
    path('admin/holidays/', views.HolidayListView.as_view(), name='holiday_list'),
    path('admin/holidays/create/', views.HolidayCreateView.as_view(), name='holiday_create'),
    path('admin/holidays/<int:pk>/', views.HolidayDetailView.as_view(), name='holiday_detail'),
    path('admin/holidays/<int:pk>/edit/', views.HolidayUpdateView.as_view(), name='holiday_edit'),
    path('admin/holidays/<int:pk>/delete/', views.HolidayDeleteView.as_view(), name='holiday_delete'),

    # Admin CRUD routes for Django admin models (admin_views prefix)
    path('admin/crud/school-profile/', admin_views.SchoolProfileAdminListView.as_view(), name='admin_schoolprofile_list'),
    path('admin/crud/school-profile/<int:pk>/', admin_views.SchoolProfileAdminDetailView.as_view(), name='admin_schoolprofile_detail'),
    path('admin/crud/school-profile/<int:pk>/edit/', admin_views.SchoolProfileAdminUpdateView.as_view(), name='admin_schoolprofile_edit'),
    
    path('admin/crud/academic-years/', admin_views.AcademicYearAdminListView.as_view(), name='admin_academicyear_list'),
    path('admin/crud/academic-years/create/', admin_views.AcademicYearAdminCreateView.as_view(), name='admin_academicyear_create'),
    path('admin/crud/academic-years/<int:pk>/', admin_views.AcademicYearAdminDetailView.as_view(), name='admin_academicyear_detail'),
    path('admin/crud/academic-years/<int:pk>/edit/', admin_views.AcademicYearAdminUpdateView.as_view(), name='admin_academicyear_edit'),
    path('admin/crud/academic-years/<int:pk>/delete/', admin_views.AcademicYearAdminDeleteView.as_view(), name='admin_academicyear_delete'),
    
    path('admin/crud/terms/', admin_views.TermAdminListView.as_view(), name='admin_term_list'),
    path('admin/crud/terms/create/', admin_views.TermAdminCreateView.as_view(), name='admin_term_create'),
    path('admin/crud/terms/<int:pk>/', admin_views.TermAdminDetailView.as_view(), name='admin_term_detail'),
    path('admin/crud/terms/<int:pk>/edit/', admin_views.TermAdminUpdateView.as_view(), name='admin_term_edit'),
    path('admin/crud/terms/<int:pk>/delete/', admin_views.TermAdminDeleteView.as_view(), name='admin_term_delete'),
    
    path('admin/crud/holidays/', admin_views.HolidayAdminListView.as_view(), name='admin_holiday_list'),
    path('admin/crud/holidays/create/', admin_views.HolidayAdminCreateView.as_view(), name='admin_holiday_create'),
    path('admin/crud/holidays/<int:pk>/', admin_views.HolidayAdminDetailView.as_view(), name='admin_holiday_detail'),
    path('admin/crud/holidays/<int:pk>/edit/', admin_views.HolidayAdminUpdateView.as_view(), name='admin_holiday_edit'),
    path('admin/crud/holidays/<int:pk>/delete/', admin_views.HolidayAdminDeleteView.as_view(), name='admin_holiday_delete'),

    # API endpoints
    path('admin/api/terms-for-year/', views.get_terms_for_academic_year, name='api_get_terms_for_year'),
]
