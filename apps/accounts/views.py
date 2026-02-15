from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse_lazy, reverse, NoReverseMatch
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone

from .models import User, LoginHistory, Role, Permission
from django.contrib import admin as django_admin
from .forms import (
    CustomAuthenticationForm, CustomUserCreationForm, CustomUserChangeForm,
    ProfileUpdateForm, RoleForm, PermissionForm, CustomPasswordResetForm
)
from apps.school.models import SchoolProfile
from apps.accounts.decorators import admin_required, teacher_required, student_required, parent_required, principal_required, director_required
from apps.classes.models import Class, Subject
from apps.academics.models import Score, ReportCard
from apps.payments.models import Payment
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.announcements.models import Assignment, Notification
from apps.attendance.models import AttendanceSession, AttendanceSummary

def login_view(request):
    """Handle user login and role-based redirection"""
    if request.user.is_authenticated:
        return redirect_based_on_role(request.user)
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # session expiry based on "remember me" checkbox
            remember = form.cleaned_data.get('remember_me')
            if remember is False:
                # expire on browser close
                request.session.set_expiry(0)
            else:
                # keep default expiry (2 weeks or SESSION_COOKIE_AGE)
                request.session.set_expiry(None)

            # Record login history
            LoginHistory.objects.create(
                user=user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                session_key=request.session.session_key
            )

            messages.success(request, f"Welcome back, {user.get_full_name()}!")
            return redirect_based_on_role(user)
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = CustomAuthenticationForm()
    
    # Get school profile for branding
    school = SchoolProfile.objects.first()
    
    context = {
        'form': form,
        'school': school,
        'title': 'Login - School Management System'
    }
    return render(request, 'accounts/login.html', context)

def redirect_based_on_role(user):
    """Redirect user based on their role or superuser status"""
    # superuser flag takes precedence; often used during development
    if getattr(user, 'is_superuser', False):
        return redirect('accounts:admin_dashboard')

    role_redirects = {
        'SUPER_ADMIN': 'accounts:admin_dashboard',
        'ADMIN': 'accounts:admin_dashboard',
        'PRINCIPAL': 'accounts:principal_dashboard',
        'VICE_PRINCIPAL': 'accounts:vice_principal_dashboard',
        'DIRECTOR': 'accounts:director_dashboard',
        'TEACHER': 'accounts:teacher_dashboard',
        'STUDENT': 'accounts:student_dashboard',
        'PARENT': 'accounts:parent_dashboard',
    }
    return redirect(role_redirects.get(user.role, 'home'))

@login_required
def logout_view(request):
    """Handle user logout and update history"""
    # update logout_time for the most recent login record matching this session
    session_key = request.session.session_key
    if session_key:
        history = LoginHistory.objects.filter(
            user=request.user,
            session_key=session_key,
            logout_time__isnull=True
        ).order_by('-login_time').first()
        if history:
            history.logout_time = timezone.now()
            history.save()

    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('accounts:login')

@login_required
def profile_view(request):
    """View and edit user profile"""
    user = request.user
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'title': 'My Profile'
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeView.form_class(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeView.form_class(request.user)
    
    context = {
        'form': form,
        'title': 'Change Password'
    }
    return render(request, 'accounts/change_password.html', context)

# Admin Views
@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard view"""
    school = SchoolProfile.objects.first()
    
    # Statistics
    total_students = User.objects.filter(role='STUDENT').count()
    total_teachers = User.objects.filter(role='TEACHER').count()
    total_parents = User.objects.filter(role='PARENT').count()
    total_staff = User.objects.filter(role__in=['ADMIN', 'PRINCIPAL', 'VICE_PRINCIPAL', 'DIRECTOR']).count()
    
    # Recent activities
    recent_logins = LoginHistory.objects.select_related('user').order_by('-login_time')[:10]
    
    # Build list of all models registered with Django admin and any matching custom admin CRUD links
    registered = []
    for model, model_admin in django_admin.site._registry.items():
        opts = model._meta
        app_label = opts.app_label
        model_name = opts.model_name
        try:
            django_admin_url = reverse('admin:%s_%s_changelist' % (app_label, model_name))
        except NoReverseMatch:
            django_admin_url = None
        custom_url = None
        try:
            custom_url = reverse(f"{app_label}:admin_{model_name}_list")
        except NoReverseMatch:
            custom_url = None

        registered.append({
            'app_label': app_label,
            'model_name': model_name,
            'verbose_name': getattr(opts, 'verbose_name_plural', model_name).title(),
            'django_admin_url': django_admin_url,
            'custom_url': custom_url,
        })

    context = {
        'school': school,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_parents': total_parents,
        'total_staff': total_staff,
        'recent_logins': recent_logins,
        'title': 'Admin Dashboard',
        'registered_admin_models': registered,
    }
    return render(request, 'accounts/admin/dashboard.html', context)

@login_required
@admin_required
def user_list(request):
    """List all users with filters"""
    query = request.GET.get('q', '')
    role = request.GET.get('role', '')
    
    users = User.objects.all()
    
    if query:
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    if role:
        users = users.filter(role=role)
    
    context = {
        'users': users,
        'query': query,
        'selected_role': role,
        'roles': User.Roles.choices,
        'title': 'User Management'
    }
    return render(request, 'accounts/admin/user_list.html', context)

@login_required
@admin_required
def user_create(request):
    """Create new user"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User {user.get_full_name()} created successfully.")
            return redirect('accounts:user_list')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Create New User'
    }
    return render(request, 'accounts/admin/user_form.html', context)

@login_required
@admin_required
def user_edit(request, pk):
    """Edit existing user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"User {user.get_full_name()} updated successfully.")
            return redirect('accounts:user_list')
    else:
        form = CustomUserChangeForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'title': f'Edit User: {user.get_full_name()}'
    }
    return render(request, 'accounts/admin/user_form.html', context)

@login_required
@admin_required
def user_detail(request, pk):
    """View user details"""
    user = get_object_or_404(User, pk=pk)
    
    context = {
        'user': user,
        'title': f'User Details: {user.get_full_name()}'
    }
    return render(request, 'accounts/admin/user_detail.html', context)

@login_required
@admin_required
def user_delete(request, pk):
    """Delete user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, f"User {user.get_full_name()} deleted successfully.")
        return redirect('accounts:user_list')
    
    context = {
        'user': user,
        'title': 'Confirm Delete'
    }
    return render(request, 'accounts/admin/user_confirm_delete.html', context)

@login_required
@admin_required
def role_list(request):
    """List all roles"""
    roles = Role.objects.all()
    context = {
        'roles': roles,
        'title': 'Role Management'
    }
    return render(request, 'accounts/admin/role_list.html', context)

@login_required
@admin_required
def role_create(request):
    """Create new role"""
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.created_by = request.user
            role.save()
            form.save_m2m()
            messages.success(request, f"Role {role.name} created successfully.")
            return redirect('accounts:role_list')
    else:
        form = RoleForm()
    
    context = {
        'form': form,
        'title': 'Create New Role'
    }
    return render(request, 'accounts/admin/role_form.html', context)

@login_required
@admin_required
def role_edit(request, pk):
    """Edit existing role"""
    role = get_object_or_404(Role, pk=pk)
    
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, f"Role {role.name} updated successfully.")
            return redirect('accounts:role_list')
    else:
        form = RoleForm(instance=role)
    
    context = {
        'form': form,
        'role': role,
        'title': f'Edit Role: {role.name}'
    }
    return render(request, 'accounts/admin/role_form.html', context)

@login_required
@admin_required
def role_delete(request, pk):
    """Delete role"""
    role = get_object_or_404(Role, pk=pk)
    
    if request.method == 'POST':
        role.delete()
        messages.success(request, f"Role {role.name} deleted successfully.")
        return redirect('accounts:role_list')
    
    context = {
        'role': role,
        'title': 'Confirm Delete'
    }
    return render(request, 'accounts/admin/role_confirm_delete.html', context)

# Teacher Dashboard
@login_required
@teacher_required
def teacher_dashboard(request):
    """Teacher dashboard view"""
    # already decorated with @teacher_required, redirecting if role mismatch
    teacher = request.user.teacher_profile
    
    # Get classes taught by this teacher
    classes_taught = Class.objects.filter(
        subject_allocations__teacher=request.user
    ).distinct()
    
    # Get subjects taught
    subjects_taught = Subject.objects.filter(
        allocations__teacher=request.user
    ).distinct()
    
    # Get today's schedule
    today = timezone.now().date()
    today_attendance = AttendanceSession.objects.filter(
        class_assigned__in=classes_taught,
        date=today
    ).exists()
    
    context = {
        'teacher': teacher,
        'classes_taught': classes_taught,
        'subjects_taught': subjects_taught,
        'today_attendance': today_attendance,
        'title': 'Teacher Dashboard'
    }
    return render(request, 'accounts/teacher/dashboard.html', context)

# Student Dashboard
@login_required
@student_required
def student_dashboard(request):
    """Student dashboard view"""
    # decorated; any mismatch will be handled by decorator
    student = request.user.student_profile
    
    # Get recent scores
    recent_scores = Score.objects.filter(
        student=student
    ).select_related('subject_assessment__subject').order_by('-recorded_at')[:10]
    
    # Get attendance summary
    attendance_summary = AttendanceSummary.objects.filter(
        student=student
    ).first()
    
    # Get pending assignments
    pending_assignments = Assignment.objects.filter(
        class_assigned=student.current_class,
        due_date__gte=timezone.now()
    )[:5]
    
    context = {
        'student': student,
        'recent_scores': recent_scores,
        'attendance_summary': attendance_summary,
        'pending_assignments': pending_assignments,
        'title': 'Student Dashboard'
    }
    return render(request, 'accounts/student/dashboard.html', context)

# Parent Dashboard
@login_required
@parent_required
def parent_dashboard(request):
    """Parent dashboard view"""
    parent = request.user.parent_profile
    
    # Get children
    children = parent.children.all()
    
    # Get notifications for all children
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:20]
    
    context = {
        'parent': parent,
        'children': children,
        'notifications': notifications,
        'title': 'Parent Dashboard'
    }
    return render(request, 'accounts/parent/dashboard.html', context)

# Principal Dashboard
@login_required
@principal_required
def principal_dashboard(request):
    """Principal dashboard view"""
    school = SchoolProfile.objects.first()
    
    # School-wide statistics
    total_students = Student.objects.filter(enrollment_status='ACTIVE').count()
    total_teachers = Teacher.objects.filter(is_active=True).count()
    total_classes = Class.objects.filter(status='ACTIVE').count()
    
    # Performance overview
    recent_reports = ReportCard.objects.order_by('-generated_at')[:10]
    
    context = {
        'school': school,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'recent_reports': recent_reports,
        'title': 'Principal Dashboard'
    }
    return render(request, 'accounts/principal/dashboard.html', context)


# Vice Principal Dashboard
@login_required
@principal_required
# vice principals are included in principal_required mixin
def vice_principal_dashboard(request):
    """Vice principal dashboard view"""
    school = SchoolProfile.objects.first()
    
    # basic overview (can be extended later)
    total_students = Student.objects.filter(enrollment_status='ACTIVE').count()
    total_teachers = Teacher.objects.filter(is_active=True).count()
    
    context = {
        'school': school,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'title': 'Vice Principal Dashboard'
    }
    return render(request, 'accounts/vice_principal/dashboard.html', context)

# Director Dashboard
@login_required
@director_required
def director_dashboard(request):
    """Director dashboard view"""
    school = SchoolProfile.objects.first()
    
    # Financial overview
    from django.db.models import Sum
    total_fees_collected = Payment.objects.filter(
        status='SUCC'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Enrollment trends
    enrollments_this_year = Student.objects.filter(
        date_of_admission__year=timezone.now().year
    ).count()
    
    context = {
        'school': school,
        'total_fees_collected': total_fees_collected,
        'enrollments_this_year': enrollments_this_year,
        'title': 'Director Dashboard'
    }
    return render(request, 'accounts/director/dashboard.html', context)

# Password Reset View
def password_reset(request):
    """Handle password reset requests"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='registration/password_reset_email.html',
                subject_template_name='registration/password_reset_subject.txt'
            )
            messages.success(request, 'Password reset email has been sent. Please check your email.')
            return redirect('accounts:login')
    else:
        form = PasswordResetForm()
    
    context = {
        'form': form,
        'title': 'Password Reset'
    }
    return render(request, 'registration/password_reset_form.html', context)
