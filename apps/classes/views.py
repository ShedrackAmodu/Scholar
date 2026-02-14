from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils.decorators import method_decorator

from .models import ClassLevel, Class, Subject, SubjectAllocation
from .forms import (
    ClassLevelForm, ClassForm, SubjectForm,
    SubjectAllocationForm, BulkClassAssignmentForm
)
from apps.accounts.decorators import admin_required, teacher_required, principal_required
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.school.models import AcademicYear, Term

# Class Level Views
@method_decorator([login_required, admin_required], name='dispatch')
class ClassLevelListView(ListView):
    """List all class levels"""
    model = ClassLevel
    template_name = 'classes/admin/class_level_list.html'
    context_object_name = 'class_levels'
    ordering = ['order']

@method_decorator([login_required, admin_required], name='dispatch')
class ClassLevelCreateView(SuccessMessageMixin, CreateView):
    """Create new class level"""
    model = ClassLevel
    form_class = ClassLevelForm
    template_name = 'classes/admin/class_level_form.html'
    success_url = reverse_lazy('classes:class_level_list')
    success_message = "Class level %(name)s created successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class ClassLevelUpdateView(SuccessMessageMixin, UpdateView):
    """Update class level"""
    model = ClassLevel
    form_class = ClassLevelForm
    template_name = 'classes/admin/class_level_form.html'
    success_url = reverse_lazy('classes:class_level_list')
    success_message = "Class level %(name)s updated successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class ClassLevelDeleteView(DeleteView):
    """Delete class level"""
    model = ClassLevel
    template_name = 'classes/admin/class_level_confirm_delete.html'
    success_url = reverse_lazy('classes:class_level_list')
    success_message = "Class level deleted successfully."

# Class Views
@method_decorator([login_required, principal_required], name='dispatch')
class ClassListView(ListView):
    """List all classes"""
    model = Class
    template_name = 'classes/admin/class_list.html'
    context_object_name = 'classes'
    
    def get_queryset(self):
        queryset = Class.objects.select_related(
            'class_level', 'class_teacher', 'academic_year'
        ).prefetch_related('students')
        
        # Filter by academic year
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academic_years'] = AcademicYear.objects.all()
        context['status_choices'] = Class.Status.choices
        return context

@method_decorator([login_required, principal_required], name='dispatch')
class ClassCreateView(SuccessMessageMixin, CreateView):
    """Create new class"""
    model = Class
    form_class = ClassForm
    template_name = 'classes/admin/class_form.html'
    success_url = reverse_lazy('classes:class_list')
    success_message = "Class %(name)s created successfully."
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Set current academic year as default
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if current_year and not kwargs.get('initial'):
            kwargs['initial'] = {'academic_year': current_year}
        return kwargs

@method_decorator([login_required, principal_required], name='dispatch')
class ClassUpdateView(SuccessMessageMixin, UpdateView):
    """Update class"""
    model = Class
    form_class = ClassForm
    template_name = 'classes/admin/class_form.html'
    success_url = reverse_lazy('classes:class_list')
    success_message = "Class %(name)s updated successfully."

@method_decorator([login_required, principal_required], name='dispatch')
class ClassDeleteView(DeleteView):
    """Delete class"""
    model = Class
    template_name = 'classes/admin/class_confirm_delete.html'
    success_url = reverse_lazy('classes:class_list')
    success_message = "Class deleted successfully."

@method_decorator([login_required, principal_required], name='dispatch')
class ClassDetailView(DetailView):
    """View class details"""
    model = Class
    template_name = 'classes/admin/class_detail.html'
    context_object_name = 'class_obj'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_obj = self.get_object()
        
        # Get students in this class
        context['students'] = Student.objects.filter(
            current_class=class_obj,
            enrollment_status='ACTIVE'
        ).select_related('user')
        
        # Get subject allocations
        context['subject_allocations'] = SubjectAllocation.objects.filter(
            class_assigned=class_obj,
            academic_year=class_obj.academic_year
        ).select_related('subject', 'teacher')
        
        # Get class teacher info
        if class_obj.class_teacher:
            context['class_teacher_profile'] = Teacher.objects.filter(
                user=class_obj.class_teacher
            ).first()
        
        return context

# Subject Views
@method_decorator([login_required, principal_required], name='dispatch')
class SubjectListView(ListView):
    """List all subjects"""
    model = Subject
    template_name = 'classes/admin/subject_list.html'
    context_object_name = 'subjects'
    
    def get_queryset(self):
        queryset = Subject.objects.select_related('class_level')
        
        # Filter by class level
        class_level = self.request.GET.get('class_level')
        if class_level:
            queryset = queryset.filter(class_level_id=class_level)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_levels'] = ClassLevel.objects.all()
        return context

@method_decorator([login_required, principal_required], name='dispatch')
class SubjectCreateView(SuccessMessageMixin, CreateView):
    """Create new subject"""
    model = Subject
    form_class = SubjectForm
    template_name = 'classes/admin/subject_form.html'
    success_url = reverse_lazy('classes:subject_list')
    success_message = "Subject %(name)s created successfully."

@method_decorator([login_required, principal_required], name='dispatch')
class SubjectUpdateView(SuccessMessageMixin, UpdateView):
    """Update subject"""
    model = Subject
    form_class = SubjectForm
    template_name = 'classes/admin/subject_form.html'
    success_url = reverse_lazy('classes:subject_list')
    success_message = "Subject %(name)s updated successfully."

@method_decorator([login_required, principal_required], name='dispatch')
class SubjectDeleteView(DeleteView):
    """Delete subject"""
    model = Subject
    template_name = 'classes/admin/subject_confirm_delete.html'
    success_url = reverse_lazy('classes:subject_list')
    success_message = "Subject deleted successfully."

# Subject Allocation Views
@method_decorator([login_required, principal_required], name='dispatch')
class SubjectAllocationListView(ListView):
    """List all subject allocations"""
    model = SubjectAllocation
    template_name = 'classes/admin/allocation_list.html'
    context_object_name = 'allocations'
    
    def get_queryset(self):
        queryset = SubjectAllocation.objects.select_related(
            'teacher', 'subject', 'class_assigned', 'academic_year'
        )
        
        # Filter by academic year
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        # Filter by class
        class_id = self.request.GET.get('class')
        if class_id:
            queryset = queryset.filter(class_assigned_id=class_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academic_years'] = AcademicYear.objects.all()
        context['classes'] = Class.objects.filter(status='ACTIVE')
        return context

@method_decorator([login_required, principal_required], name='dispatch')
class SubjectAllocationCreateView(SuccessMessageMixin, CreateView):
    """Create new subject allocation"""
    model = SubjectAllocation
    form_class = SubjectAllocationForm
    template_name = 'classes/admin/allocation_form.html'
    success_url = reverse_lazy('classes:allocation_list')
    success_message = "Subject allocation created successfully."
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Set current academic year as default
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if current_year and not kwargs.get('initial'):
            kwargs['initial'] = {'academic_year': current_year}
        return kwargs

@method_decorator([login_required, principal_required], name='dispatch')
class SubjectAllocationUpdateView(SuccessMessageMixin, UpdateView):
    """Update subject allocation"""
    model = SubjectAllocation
    form_class = SubjectAllocationForm
    template_name = 'classes/admin/allocation_form.html'
    success_url = reverse_lazy('classes:allocation_list')
    success_message = "Subject allocation updated successfully."

@method_decorator([login_required, principal_required], name='dispatch')
class SubjectAllocationDeleteView(DeleteView):
    """Delete subject allocation"""
    model = SubjectAllocation
    template_name = 'classes/admin/allocation_confirm_delete.html'
    success_url = reverse_lazy('classes:allocation_list')
    success_message = "Subject allocation deleted successfully."

# Teacher Views for Classes
@login_required
@teacher_required
def teacher_classes(request):
    """View classes taught by current teacher"""
    teacher = request.user
    
    # Get classes where teacher is assigned
    classes_taught = Class.objects.filter(
        subject_allocations__teacher=teacher,
        status='ACTIVE'
    ).distinct()
    
    # Get subject allocations for this teacher
    allocations = SubjectAllocation.objects.filter(
        teacher=teacher,
        academic_year__is_current=True
    ).select_related('subject', 'class_assigned')
    
    context = {
        'classes_taught': classes_taught,
        'allocations': allocations,
        'title': 'My Classes'
    }
    return render(request, 'classes/teacher/my_classes.html', context)

@login_required
@teacher_required
def class_students(request, class_id):
    """View students in a specific class"""
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Check if teacher is authorized
    if not SubjectAllocation.objects.filter(
        teacher=request.user,
        class_assigned=class_obj
    ).exists() and class_obj.class_teacher != request.user:
        messages.error(request, "You are not authorized to view this class.")
        return redirect('classes:teacher_classes')
    
    students = Student.objects.filter(
        current_class=class_obj,
        enrollment_status='ACTIVE'
    ).select_related('user')
    
    context = {
        'class_obj': class_obj,
        'students': students,
        'title': f'Students in {class_obj.name}'
    }
    return render(request, 'classes/teacher/class_students.html', context)

# Bulk Operations
@login_required
@principal_required
def bulk_class_assignment(request):
    """Bulk assign teachers to classes"""
    if request.method == 'POST':
        form = BulkClassAssignmentForm(request.POST)
        if form.is_valid():
            teacher = form.cleaned_data['teacher']
            academic_year = form.cleaned_data['academic_year']
            term = form.cleaned_data['term']
            classes = form.cleaned_data['classes']
            
            # Create allocations for each class
            for class_obj in classes:
                # Get subjects for this class level
                subjects = Subject.objects.filter(class_level=class_obj.class_level)
                
                for subject in subjects:
                    SubjectAllocation.objects.get_or_create(
                        teacher=teacher,
                        subject=subject,
                        class_assigned=class_obj,
                        academic_year=academic_year,
                        term=term
                    )
            
            messages.success(request, f"Teacher assigned to {classes.count()} classes successfully.")
            return redirect('classes:allocation_list')
    else:
        form = BulkClassAssignmentForm()
    
    context = {
        'form': form,
        'title': 'Bulk Class Assignment'
    }
    return render(request, 'classes/admin/bulk_assignment.html', context)

# API Views
@login_required
def get_subjects_for_class(request):
    """API endpoint to get subjects for a class"""
    class_id = request.GET.get('class_id')
    if class_id:
        class_obj = get_object_or_404(Class, id=class_id)
        subjects = Subject.objects.filter(
            class_level=class_obj.class_level
        ).values('id', 'name', 'code')
        return JsonResponse(list(subjects), safe=False)
    return JsonResponse([], safe=False)

@login_required
def get_teachers_for_subject(request):
    """API endpoint to get teachers qualified for a subject"""
    subject_id = request.GET.get('subject_id')
    if subject_id:
        teachers = User.objects.filter(
            role='TEACHER',
            teacher_profile__expertise__subject_id=subject_id
        ).distinct().values('id', 'first_name', 'last_name', 'email')
        return JsonResponse(list(teachers), safe=False)
    return JsonResponse([], safe=False)
