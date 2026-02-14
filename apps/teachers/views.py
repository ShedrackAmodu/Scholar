from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.utils.decorators import method_decorator

from .models import Teacher, TeacherQualification, TeacherSubjectExpertise, TeacherLeave
from .forms import (
    TeacherForm, TeacherQualificationForm, TeacherSubjectExpertiseForm,
    TeacherLeaveForm, TeacherSearchForm
)
from apps.accounts.models import User
from apps.accounts.decorators import admin_required, principal_required
from apps.classes.models import Class, SubjectAllocation
from apps.school.models import AcademicYear

# Teacher List Views
@method_decorator([login_required, principal_required], name='dispatch')
class TeacherListView(ListView):
    """List all teachers"""
    model = Teacher
    template_name = 'teachers/admin/teacher_list.html'
    context_object_name = 'teachers'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Teacher.objects.select_related('user')
        
        # Search
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(staff_id__icontains=query) |
                Q(user__email__icontains=query)
            )
        
        # Filter by employment type
        emp_type = self.request.GET.get('employment_type')
        if emp_type:
            queryset = queryset.filter(employment_type=emp_type)
        
        # Filter by active status
        is_active = self.request.GET.get('is_active')
        if is_active == 'True':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'False':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employment_types'] = Teacher.EmploymentType.choices
        context['search_form'] = TeacherSearchForm(self.request.GET)
        return context

@method_decorator([login_required, principal_required], name='dispatch')
class TeacherDetailView(DetailView):
    """View teacher details"""
    model = Teacher
    template_name = 'teachers/admin/teacher_detail.html'
    context_object_name = 'teacher'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.get_object()
        
        # Get qualifications
        context['qualifications'] = TeacherQualification.objects.filter(teacher=teacher)
        
        # Get subject expertise
        context['expertise'] = TeacherSubjectExpertise.objects.filter(
            teacher=teacher
        ).select_related('subject')
        
        # Get current allocations
        context['allocations'] = SubjectAllocation.objects.filter(
            teacher=teacher.user,
            academic_year__is_current=True
        ).select_related('subject', 'class_assigned')
        
        # Get leave history
        context['leaves'] = TeacherLeave.objects.filter(teacher=teacher).order_by('-start_date')
        
        return context

# Teacher CRUD Views
@method_decorator([login_required, principal_required], name='dispatch')
class TeacherCreateView(SuccessMessageMixin, CreateView):
    """Create new teacher"""
    model = Teacher
    form_class = TeacherForm
    template_name = 'teachers/admin/teacher_form.html'
    success_url = reverse_lazy('teachers:teacher_list')
    success_message = "Teacher %(user)s created successfully."
    
    def form_valid(self, form):
        # Create user account
        user = User.objects.create_user(
            username=form.cleaned_data.get('email').split('@')[0],
            email=form.cleaned_data.get('email'),
            password='Teacher@123',  # Default password
            first_name=form.cleaned_data.get('first_name'),
            last_name=form.cleaned_data.get('last_name'),
            role='TEACHER'
        )
        form.instance.user = user
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add user fields to form
        form.fields['first_name'] = forms.CharField(max_length=100)
        form.fields['last_name'] = forms.CharField(max_length=100)
        form.fields['email'] = forms.EmailField()
        return form

@method_decorator([login_required, principal_required], name='dispatch')
class TeacherUpdateView(SuccessMessageMixin, UpdateView):
    """Update teacher"""
    model = Teacher
    form_class = TeacherForm
    template_name = 'teachers/admin/teacher_form.html'
    success_url = reverse_lazy('teachers:teacher_list')
    success_message = "Teacher %(user)s updated successfully."

@method_decorator([login_required, principal_required], name='dispatch')
class TeacherDeleteView(DeleteView):
    """Delete teacher"""
    model = Teacher
    template_name = 'teachers/admin/teacher_confirm_delete.html'
    success_url = reverse_lazy('teachers:teacher_list')
    success_message = "Teacher deleted successfully."
    
    def delete(self, request, *args, **kwargs):
        teacher = self.get_object()
        # Also delete user account
        teacher.user.delete()
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Teacher Qualification Views
@login_required
@principal_required
def add_qualification(request, teacher_id):
    """Add qualification to teacher"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        form = TeacherQualificationForm(request.POST)
        if form.is_valid():
            qualification = form.save(commit=False)
            qualification.teacher = teacher
            qualification.save()
            messages.success(request, "Qualification added successfully.")
            return redirect('teachers:teacher_detail', pk=teacher.id)
    else:
        form = TeacherQualificationForm()
    
    context = {
        'form': form,
        'teacher': teacher,
        'title': 'Add Qualification'
    }
    return render(request, 'teachers/admin/qualification_form.html', context)

@login_required
@principal_required
def delete_qualification(request, pk):
    """Delete qualification"""
    qualification = get_object_or_404(TeacherQualification, pk=pk)
    teacher_id = qualification.teacher.id
    
    if request.method == 'POST':
        qualification.delete()
        messages.success(request, "Qualification deleted successfully.")
        return redirect('teachers:teacher_detail', pk=teacher_id)
    
    context = {
        'qualification': qualification,
        'title': 'Confirm Delete'
    }
    return render(request, 'teachers/admin/qualification_confirm_delete.html', context)

# Teacher Subject Expertise
@login_required
@principal_required
def add_expertise(request, teacher_id):
    """Add subject expertise to teacher"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        form = TeacherSubjectExpertiseForm(request.POST)
        if form.is_valid():
            expertise = form.save(commit=False)
            expertise.teacher = teacher
            expertise.save()
            messages.success(request, "Subject expertise added successfully.")
            return redirect('teachers:teacher_detail', pk=teacher.id)
    else:
        form = TeacherSubjectExpertiseForm()
    
    context = {
        'form': form,
        'teacher': teacher,
        'title': 'Add Subject Expertise'
    }
    return render(request, 'teachers/admin/expertise_form.html', context)

@login_required
@principal_required
def delete_expertise(request, pk):
    """Delete subject expertise"""
    expertise = get_object_or_404(TeacherSubjectExpertise, pk=pk)
    teacher_id = expertise.teacher.id
    
    if request.method == 'POST':
        expertise.delete()
        messages.success(request, "Subject expertise removed successfully.")
        return redirect('teachers:teacher_detail', pk=teacher_id)
    
    context = {
        'expertise': expertise,
        'title': 'Confirm Delete'
    }
    return render(request, 'teachers/admin/expertise_confirm_delete.html', context)

# Teacher Leave Views
@login_required
def teacher_leave_list(request):
    """List leave requests for teacher"""
    teacher = request.user.teacher_profile
    
    leaves = TeacherLeave.objects.filter(teacher=teacher).order_by('-start_date')
    
    context = {
        'leaves': leaves,
        'title': 'My Leave Requests'
    }
    return render(request, 'teachers/leave_list.html', context)

@login_required
def teacher_leave_create(request):
    """Create leave request"""
    teacher = request.user.teacher_profile
    
    if request.method == 'POST':
        form = TeacherLeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.teacher = teacher
            leave.save()
            messages.success(request, "Leave request submitted successfully.")
            return redirect('teachers:leave_list')
    else:
        form = TeacherLeaveForm()
    
    context = {
        'form': form,
        'title': 'Request Leave'
    }
    return render(request, 'teachers/leave_form.html', context)

@login_required
@principal_required
def approve_leave(request, pk):
    """Approve leave request"""
    leave = get_object_or_404(TeacherLeave, pk=pk)
    
    if request.method == 'POST':
        leave.is_approved = True
        leave.approved_by = request.user
        leave.save()
        messages.success(request, "Leave request approved.")
        return redirect('teachers:teacher_detail', pk=leave.teacher.id)
    
    context = {
        'leave': leave,
        'title': 'Approve Leave'
    }
    return render(request, 'teachers/approve_leave.html', context)

# Teacher Dashboard Views
@login_required
def teacher_dashboard(request):
    """Teacher dashboard"""
    teacher = request.user.teacher_profile
    
    # Get current allocations
    current_allocations = SubjectAllocation.objects.filter(
        teacher=request.user,
        academic_year__is_current=True
    ).select_related('subject', 'class_assigned')
    
    # Get classes where teacher is class teacher
    class_teacher_of = Class.objects.filter(
        class_teacher=request.user,
        status='ACTIVE'
    )
    
    # Get today's schedule
    today = timezone.now().date()
    today_classes = current_allocations.filter(
        class_assigned__status='ACTIVE'
    )
    
    # Get pending tasks
    pending_attendance = AttendanceSession.objects.filter(
        class_assigned__in=[c.class_assigned for c in current_allocations],
        date=today,
        is_closed=False
    ).exists()
    
    context = {
        'teacher': teacher,
        'current_allocations': current_allocations,
        'class_teacher_of': class_teacher_of,
        'today_classes': today_classes,
        'pending_attendance': pending_attendance,
        'title': 'Teacher Dashboard'
    }
    return render(request, 'teachers/dashboard/dashboard.html', context)

@login_required
def teacher_schedule(request):
    """View teacher's schedule"""
    teacher = request.user
    
    # Get all allocations for this teacher
    allocations = SubjectAllocation.objects.filter(
        teacher=teacher,
        academic_year__is_current=True
    ).select_related('subject', 'class_assigned')
    
    # Group by day (simplified - you'd need a proper timetable model for full features)
    schedule = {
        'Monday': [],
        'Tuesday': [],
        'Wednesday': [],
        'Thursday': [],
        'Friday': []
    }
    
    context = {
        'schedule': schedule,
        'title': 'My Schedule'
    }
    return render(request, 'teachers/dashboard/schedule.html', context)

# Bulk Operations
@login_required
@principal_required
def bulk_teacher_upload(request):
    """Bulk upload teachers from CSV"""
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, "Please upload a CSV file.")
            return redirect('teachers:teacher_list')
        
        # Process CSV file
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string, delimiter=',')
        
        # Skip header
        next(reader, None)
        
        created_count = 0
        error_count = 0
        
        for row in reader:
            try:
                # Create user
                user = User.objects.create_user(
                    username=row[2].split('@')[0],
                    email=row[2],
                    password='Teacher@123',
                    first_name=row[0],
                    last_name=row[1],
                    role='TEACHER'
                )
                
                # Create teacher
                teacher = Teacher.objects.create(
                    user=user,
                    staff_id=row[3],
                    qualification=row[4],
                    specialization=row[5],
                    years_of_experience=int(row[6]),
                    employment_type=row[7],
                    date_employed=row[8],
                    phone=row[9],
                    address=row[10]
                )
                
                created_count += 1
                
            except Exception as e:
                error_count += 1
        
        messages.success(request, f"{created_count} teachers created successfully. {error_count} errors.")
        return redirect('teachers:teacher_list')
    
    return render(request, 'teachers/admin/bulk_upload.html')

# API Views
@login_required
def get_teacher_subjects(request, teacher_id):
    """API endpoint to get subjects taught by teacher"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    subjects = TeacherSubjectExpertise.objects.filter(
        teacher=teacher
    ).select_related('subject').values(
        'subject__id', 'subject__name', 'subject__code', 'is_primary'
    )
    return JsonResponse(list(subjects), safe=False)

@login_required
def get_teacher_allocations(request, teacher_id):
    """API endpoint to get current allocations for teacher"""
    teacher = get_object_or_404(User, id=teacher_id, role='TEACHER')
    allocations = SubjectAllocation.objects.filter(
        teacher=teacher,
        academic_year__is_current=True
    ).select_related('subject', 'class_assigned').values(
        'id', 'subject__name', 'class_assigned__name', 'term'
    )
    return JsonResponse(list(allocations), safe=False)
