"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Core app (dashboard and core functionality) with namespace
    path('', include('apps.core.urls', namespace='core')),
    
    # School app (public pages) with namespace so reverse('school:...') works
    path('school/', include('apps.school.urls', namespace='school')),
    
    # Other app URLs (namespaced for reversing)
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('admissions/', include('apps.admissions.urls', namespace='admissions')),
    path('academics/', include('apps.academics.urls', namespace='academics')),
    path('attendance/', include('apps.attendance.urls', namespace='attendance')),
    path('classes/', include('apps.classes.urls', namespace='classes')),
    path('parents/', include('apps.parents.urls', namespace='parents')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('students/', include('apps.students.urls', namespace='students')),
    path('teachers/', include('apps.teachers.urls', namespace='teachers')),
    path('announcements/', include('apps.announcements.urls', namespace='announcements')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
