from django.urls import path
from . import views

app_name = 'admissions'

urlpatterns = [
    # Public URLs
    path('', views.admissions_home, name='admission_form'),
    path('guidelines/', views.admissions_home, name='admission_guidelines'),
    path('requirements/', views.admissions_home, name='admission_requirements'),
    path('status/', views.admissions_home, name='admission_status'),
    path('api/', views.application_api, name='application_api'),

    # Admin URLs
    path('admin/', views.admissions_home, name='admission_list'),
    path('admin/<int:app_id>/', views.application_detail, name='admission_detail'),
    path('admin/schedule-exam/<int:app_id>/', views.schedule_exam, name='schedule_exam'),
    path('admin/bulk/', views.bulk_admission, name='bulk_admission'),
]
