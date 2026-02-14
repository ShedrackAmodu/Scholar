from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    """
    Decorator that checks if the user is an admin.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return user_passes_test(lambda u: False)(view_func)(request, *args, **kwargs)
        
        if not request.user.is_admin:
            raise PermissionDenied("You do not have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def staff_required(view_func):
    """
    Decorator that checks if the user is staff.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return user_passes_test(lambda u: False)(view_func)(request, *args, **kwargs)
        
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def teacher_required(view_func):
    """
    Decorator that checks if the user is a teacher.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return user_passes_test(lambda u: False)(view_func)(request, *args, **kwargs)
        
        if not request.user.is_teacher:
            raise PermissionDenied("You do not have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def parent_required(view_func):
    """
    Decorator that checks if the user is a parent.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return user_passes_test(lambda u: False)(view_func)(request, *args, **kwargs)
        
        if not request.user.is_parent:
            raise PermissionDenied("You do not have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def student_required(view_func):
    """
    Decorator that checks if the user is a student.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return user_passes_test(lambda u: False)(view_func)(request, *args, **kwargs)
        
        if not request.user.is_student:
            raise PermissionDenied("You do not have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def principal_required(view_func):
    """
    Decorator that checks if the user is a principal.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return user_passes_test(lambda u: False)(view_func)(request, *args, **kwargs)
        
        if request.user.role != 'PRINCIPAL':
            raise PermissionDenied("You do not have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def director_required(view_func):
    """
    Decorator that checks if the user is a director.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return user_passes_test(lambda u: False)(view_func)(request, *args, **kwargs)
        
        if request.user.role != 'DIRECTOR':
            raise PermissionDenied("You do not have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def accountant_required(view_func):
    """
    Decorator that checks if the user is an accountant.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return user_passes_test(lambda u: False)(view_func)(request, *args, **kwargs)
        
        if request.user.role != 'ACCOUNTANT':
            raise PermissionDenied("You do not have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
