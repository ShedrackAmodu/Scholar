from django.urls import path
from . import views

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
    path('admin/academic-years/<int:pk>/edit/', views.AcademicYearUpdateView.as_view(), name='academic_year_edit'),
    path('admin/academic-years/<int:pk>/delete/', views.AcademicYearDeleteView.as_view(), name='academic_year_delete'),
    path('admin/academic-years/set-current/', views.set_current_academic_year, name='set_current_academic_year'),

    # Term CRUD
    path('admin/terms/', views.TermListView.as_view(), name='term_list'),
    path('admin/terms/create/', views.TermCreateView.as_view(), name='term_create'),
    path('admin/terms/<int:pk>/edit/', views.TermUpdateView.as_view(), name='term_edit'),
    path('admin/terms/<int:pk>/delete/', views.TermDeleteView.as_view(), name='term_delete'),
    path('admin/terms/set-current/', views.set_current_term, name='set_current_term'),

    # Holiday CRUD
    path('admin/holidays/', views.HolidayListView.as_view(), name='holiday_list'),
    path('admin/holidays/create/', views.HolidayCreateView.as_view(), name='holiday_create'),
    path('admin/holidays/<int:pk>/edit/', views.HolidayUpdateView.as_view(), name='holiday_edit'),
    path('admin/holidays/<int:pk>/delete/', views.HolidayDeleteView.as_view(), name='holiday_delete'),

    # API endpoints
    path('admin/api/terms-for-year/', views.get_terms_for_academic_year, name='api_get_terms_for_year'),
]
