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
        
        # `is_admin` property defined on custom User model
        if not getattr(request.user, 'is_admin', False):
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
        
        if not getattr(request.user, 'is_teacher', False):
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
        
        if not getattr(request.user, 'is_parent', False):
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
        
        if not getattr(request.user, 'is_student', False):
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
        
        if not getattr(request.user, 'is_principal', False):
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
        
        if not getattr(request.user, 'is_director', False):
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
        
        # accountants may not have their own boolean property, check role directly
        if request.user.role != 'ACCOUNTANT':
            raise PermissionDenied("You do not have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
