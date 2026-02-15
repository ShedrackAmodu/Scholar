"""
Core views for the School Management System
Includes search functionality and other core features
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model
from apps.academics.models import Subject, Assessment
from apps.classes.models import Class
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.parents.models import Parent


@login_required
def search_view(request):
    """
    AJAX search endpoint for the sidebar search functionality
    """
    query = request.GET.get('q', '').strip()
    results = []
    
    if query and len(query) >= 2:
        # Search students
        student_results = Student.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(admission_number__icontains=query)
        )[:5]
        
        for student in student_results:
            results.append({
                'type': 'student',
                'id': student.id,
                'name': student.user.get_full_name(),
                'description': f"Student - Class: {student.class_assigned.name if student.class_assigned else 'Not Assigned'}",
                'url': f'/students/{student.id}/',
                'icon': 'fas fa-user-graduate'
            })
        
        # Search teachers
        teacher_results = Teacher.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )[:3]
        
        for teacher in teacher_results:
            results.append({
                'type': 'teacher',
                'id': teacher.id,
                'name': teacher.user.get_full_name(),
                'description': f"Teacher - Subjects: {teacher.subjects.count()}",
                'url': f'/teachers/{teacher.id}/',
                'icon': 'fas fa-chalkboard-teacher'
            })
        
        # Search classes
        class_results = Class.objects.filter(
            Q(name__icontains=query) |
            Q(class_level__name__icontains=query)
        )[:3]
        
        for class_obj in class_results:
            results.append({
                'type': 'class',
                'id': class_obj.id,
                'name': class_obj.name,
                'description': f"Class Level: {class_obj.class_level.name}",
                'url': f'/classes/{class_obj.id}/',
                'icon': 'fas fa-school'
            })
        
        # Search subjects
        subject_results = Subject.objects.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query)
        )[:3]
        
        for subject in subject_results:
            results.append({
                'type': 'subject',
                'id': subject.id,
                'name': subject.name,
                'description': f"Code: {subject.code}",
                'url': f'/subjects/{subject.id}/',
                'icon': 'fas fa-book'
            })
    
    return JsonResponse({
        'results': results,
        'query': query,
        'count': len(results)
    })


@login_required
def theme_toggle_view(request):
    """
    Toggle theme preference for the user
    """
    if request.method == 'POST':
        current_theme = request.session.get('theme', 'light')
        new_theme = 'dark' if current_theme == 'light' else 'light'
        request.session['theme'] = new_theme
        request.session['theme_updated'] = True
        return JsonResponse({
            'success': True,
            'theme': new_theme
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def dashboard_view(request):
    """
    Generic dashboard view that redirects based on user role
    """
    user = request.user
    
    # Redirect based on user role
    if hasattr(user, 'profile'):
        role = user.profile.role
        
        if role == 'superadmin' or role == 'admin':
            return redirect('accounts:admin_dashboard')
        elif role == 'principal':
            return redirect('academics:class_performance')
        elif role == 'director':
            return redirect('academics:analytics_dashboard')
        elif role == 'teacher':
            return redirect('academics:teacher_dashboard')
        elif role == 'parent':
            return redirect('parents:parent_dashboard')
        elif role == 'student':
            return redirect('students:student_dashboard')
    
    # Default redirect for users without profile or unknown roles
    return redirect('accounts:profile')


def home_view(request):
    """
    Public home page view
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    # Get school information for public display
    try:
        from apps.school.models import SchoolProfile
        school_profile = SchoolProfile.objects.first()
    except:
        school_profile = None
    
    context = {
        'school_profile': school_profile,
        'show_login': True
    }
    
    return render(request, 'home.html', context)


