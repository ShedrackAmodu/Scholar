"""
Context processors for the School Management System
Provides dynamic data for templates, especially the comprehensive sidebar
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.school.models import SchoolProfile


def sidebar_context(request):
    """
    Context processor to provide sidebar data for authenticated users
    """
    context = {}
    
    if request.user.is_authenticated:
        user = request.user
        
        # User statistics based on role
        if hasattr(user, 'profile') and user.profile.role == 'teacher':
            context['user_stats'] = {
                'classes': 0,  # Would be calculated from teacher's classes
                'students': 0,  # Would be calculated from teacher's students
                'pending_scores': 0,  # Would be calculated from assessments
                'pending_attendance': 0  # Would be calculated from attendance
            }
        elif hasattr(user, 'profile') and user.profile.role == 'parent':
            context['user_stats'] = {
                'children': 0,  # Would be calculated from parent's children
                'unread_messages': 0,  # Would be calculated from messages
                'pending_payments': 0  # Would be calculated from invoices
            }
        elif hasattr(user, 'profile') and user.profile.role == 'student':
            context['user_stats'] = {
                'class_name': 'Not Assigned',  # Would be calculated from student's class
                'pending_assignments': 0,  # Would be calculated from assignments
                'unread_notifications': 0  # Would be calculated from notifications
            }
        
        # Notification counts
        context['unread_notifications_count'] = 0
        context['unread_messages_count'] = 0
        context['pending_applications_count'] = 0
        context['unread_notices_count'] = 0
        
        # Calculate notification counts based on user role
        if user.is_admin:
            # Admin sees pending applications
            from apps.admissions.models import Application
            context['pending_applications_count'] = Application.objects.filter(
                status='Pending'
            ).count()
            
            # Admin sees unread notices
            from apps.announcements.models import Notice
            context['unread_notices_count'] = Notice.objects.filter(
                is_pinned=True
            ).count()
            
        elif user.is_teacher:
            # Teacher sees pending scores to enter, attendance to mark
            # This would be calculated based on assessments and attendance models
            pass
            
        elif user.is_parent:
            # Parent sees unread messages and pending payments
            # This would be calculated from messages and invoices
            pass
            
        elif user.is_student:
            # Student sees pending assignments and unread notifications
            # This would be calculated from assignments and notifications
            pass
        
        # School information
        try:
            school_profile = SchoolProfile.objects.first()
            if school_profile:
                context['school_hours'] = f"{school_profile.opening_time} - {school_profile.closing_time}"
                context['current_term'] = "First Term"  # Would be dynamic in production
                context['school_name'] = school_profile.name
            else:
                context['school_hours'] = "8:00 AM - 3:00 PM"
                context['current_term'] = "Not Set"
                context['school_name'] = "School Management System"
        except:
            context['school_hours'] = "8:00 AM - 3:00 PM"
            context['current_term'] = "Not Set"
            context['school_name'] = "School Management System"
        
        # Theme preference
        context['user_theme'] = request.session.get('theme', 'light')
        
        # Current year for footer
        context['current_year'] = timezone.now().year
        
        # User's full name for sidebar
        context['user_full_name'] = user.get_full_name() or user.username
        
    return context


def global_context(request):
    """
    Global context processor for site-wide variables
    """
    context = {}
    
    # Site-wide settings
    context['site_name'] = getattr(settings, 'SITE_NAME', 'School Management System')
    context['site_description'] = getattr(settings, 'SITE_DESCRIPTION', 'A comprehensive school management solution')
    
    # Academic year
    context['academic_year'] = timezone.now().year
    
    # Current term (would be dynamic in production)
    context['current_term'] = "First Term"  # This should come from SchoolProfile
    
    # Contact information (would come from SchoolProfile)
    context['school_contact'] = {
        'phone': '+234-XXX-XXXX',
        'email': 'info@school.edu',
        'address': '123 School Street, City, Country'
    }
    
    # Social media links
    context['social_links'] = {
        'facebook': '#',
        'twitter': '#',
        'instagram': '#',
        'linkedin': '#'
    }
    
    return context


def user_permissions_context(request):
    """
    Context processor for user permissions and capabilities
    """
    context = {}
    
    if request.user.is_authenticated:
        user = request.user
        
        # Role-based capabilities
        profile_role = user.profile.role if hasattr(user, 'profile') else 'student'
        
        context['user_capabilities'] = {
            'can_manage_users': profile_role in ['superadmin', 'admin'],
            'can_manage_classes': profile_role in ['superadmin', 'admin', 'principal'],
            'can_manage_students': profile_role in ['superadmin', 'admin', 'principal'],
            'can_manage_payments': profile_role in ['superadmin', 'admin', 'director'],
            'can_create_announcements': profile_role in ['superadmin', 'admin'],
            'can_view_reports': profile_role in ['superadmin', 'admin', 'principal', 'director'],
            'can_enter_scores': profile_role == 'teacher',
            'can_take_attendance': profile_role == 'teacher',
            'can_view_performance': profile_role in ['teacher', 'parent', 'student'],
            'can_make_payments': profile_role == 'parent',
            'can_view_messages': profile_role in ['parent', 'teacher'],
        }
        
        # Quick action permissions
        context['can_perform_quick_actions'] = {
            'enter_scores': profile_role == 'teacher',
            'take_attendance': profile_role == 'teacher',
            'create_assignment': profile_role == 'teacher',
            'make_payment': profile_role == 'parent',
            'check_messages': profile_role in ['parent', 'teacher'],
            'view_performance': profile_role in ['parent', 'student'],
        }
    
    return context