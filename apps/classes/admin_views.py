from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.decorators import method_decorator

from .models import ClassLevel, Class, Subject, SubjectAllocation
from .forms import ClassLevelForm, ClassForm, SubjectForm, SubjectAllocationForm
from apps.accounts.decorators import admin_required
from apps.accounts.models import User
from apps.school.models import AcademicYear


# ============ ClassLevel Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class ClassLevelAdminListView(ListView):
    """Admin list view for Class Levels"""
    model = ClassLevel
    template_name = 'classes/admin/class_level_list.html'
    context_object_name = 'class_levels'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ClassLevel.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by type
        level_type = self.request.GET.get('level_type')
        if level_type:
            queryset = queryset.filter(level_type=level_type)
        
        return queryset.order_by('order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level_types'] = ClassLevel.LEVEL_TYPES
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_level_type'] = self.request.GET.get('level_type', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ClassLevelAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Class Levels"""
    model = ClassLevel
    form_class = ClassLevelForm
    template_name = 'classes/admin/class_level_form.html'
    success_url = reverse_lazy('classes:admin_class_level_list')
    success_message = "Class level '%(name)s' created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Class Level'
        context['button_text'] = 'Create Class Level'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ClassLevelAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Class Levels"""
    model = ClassLevel
    form_class = ClassLevelForm
    template_name = 'classes/admin/class_level_form.html'
    success_url = reverse_lazy('classes:admin_class_level_list')
    success_message = "Class level '%(name)s' updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Class Level: {self.object.name}'
        context['button_text'] = 'Update Class Level'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ClassLevelAdminDetailView(DetailView):
    """Admin detail view for Class Levels"""
    model = ClassLevel
    template_name = 'classes/admin/class_level_detail.html'
    context_object_name = 'class_level'


@method_decorator([login_required, admin_required], name='dispatch')
class ClassLevelAdminDeleteView(DeleteView):
    """Admin delete view for Class Levels"""
    model = ClassLevel
    template_name = 'classes/admin/class_level_confirm_delete.html'
    success_url = reverse_lazy('classes:admin_class_level_list')
    
    def delete(self, request, *args, **kwargs):
        class_level = self.get_object()
        messages.success(self.request, f"Class level {class_level.name} deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ Class Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class ClassAdminListView(ListView):
    """Admin list view for Classes"""
    model = Class
    template_name = 'classes/admin/class_list.html'
    context_object_name = 'classes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Class.objects.select_related('class_level', 'class_teacher', 'academic_year').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(room_number__icontains=search_query) |
                Q(class_teacher__first_name__icontains=search_query) |
                Q(class_teacher__last_name__icontains=search_query)
            )
        
        # Filter by class level
        class_level = self.request.GET.get('class_level')
        if class_level:
            queryset = queryset.filter(class_level_id=class_level)
        
        # Filter by academic year
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('class_level__order', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_levels'] = ClassLevel.objects.all()
        context['academic_years'] = AcademicYear.objects.all()
        context['statuses'] = Class.Status.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_class_level'] = self.request.GET.get('class_level', '')
        context['selected_academic_year'] = self.request.GET.get('academic_year', '')
        context['selected_status'] = self.request.GET.get('status', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ClassAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Classes"""
    model = Class
    form_class = ClassForm
    template_name = 'classes/admin/class_form.html'
    success_url = reverse_lazy('classes:admin_class_list')
    success_message = "Class '%(name)s' created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Class'
        context['button_text'] = 'Create Class'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ClassAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Classes"""
    model = Class
    form_class = ClassForm
    template_name = 'classes/admin/class_form.html'
    success_url = reverse_lazy('classes:admin_class_list')
    success_message = "Class '%(name)s' updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Class: {self.object.name}'
        context['button_text'] = 'Update Class'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ClassAdminDetailView(DetailView):
    """Admin detail view for Classes"""
    model = Class
    template_name = 'classes/admin/class_detail.html'
    context_object_name = 'class_obj'


@method_decorator([login_required, admin_required], name='dispatch')
class ClassAdminDeleteView(DeleteView):
    """Admin delete view for Classes"""
    model = Class
    template_name = 'classes/admin/class_confirm_delete.html'
    success_url = reverse_lazy('classes:admin_class_list')
    
    def delete(self, request, *args, **kwargs):
        class_obj = self.get_object()
        messages.success(self.request, f"Class {class_obj.name} deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ Subject Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAdminListView(ListView):
    """Admin list view for Subjects"""
    model = Subject
    template_name = 'classes/admin/subject_list.html'
    context_object_name = 'subjects'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Subject.objects.select_related('class_level').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by class level
        class_level = self.request.GET.get('class_level')
        if class_level:
            queryset = queryset.filter(class_level_id=class_level)
        
        # Filter by compulsory status
        is_compulsory = self.request.GET.get('is_compulsory')
        if is_compulsory == 'true':
            queryset = queryset.filter(is_compulsory=True)
        elif is_compulsory == 'false':
            queryset = queryset.filter(is_compulsory=False)
        
        return queryset.order_by('class_level__order', 'display_order', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_levels'] = ClassLevel.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_class_level'] = self.request.GET.get('class_level', '')
        context['selected_is_compulsory'] = self.request.GET.get('is_compulsory', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Subjects"""
    model = Subject
    form_class = SubjectForm
    template_name = 'classes/admin/subject_form.html'
    success_url = reverse_lazy('classes:admin_subject_list')
    success_message = "Subject '%(name)s' created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Subject'
        context['button_text'] = 'Create Subject'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Subjects"""
    model = Subject
    form_class = SubjectForm
    template_name = 'classes/admin/subject_form.html'
    success_url = reverse_lazy('classes:admin_subject_list')
    success_message = "Subject '%(name)s' updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Subject: {self.object.name}'
        context['button_text'] = 'Update Subject'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAdminDetailView(DetailView):
    """Admin detail view for Subjects"""
    model = Subject
    template_name = 'classes/admin/subject_detail.html'
    context_object_name = 'subject'


@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAdminDeleteView(DeleteView):
    """Admin delete view for Subjects"""
    model = Subject
    template_name = 'classes/admin/subject_confirm_delete.html'
    success_url = reverse_lazy('classes:admin_subject_list')
    
    def delete(self, request, *args, **kwargs):
        subject = self.get_object()
        messages.success(self.request, f"Subject {subject.name} deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ SubjectAllocation Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAllocationAdminListView(ListView):
    """Admin list view for Subject Allocations"""
    model = SubjectAllocation
    template_name = 'classes/admin/subject_allocation_list.html'
    context_object_name = 'allocations'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SubjectAllocation.objects.select_related(
            'teacher', 'subject', 'class_assigned', 'academic_year'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(teacher__first_name__icontains=search_query) |
                Q(teacher__last_name__icontains=search_query) |
                Q(subject__name__icontains=search_query) |
                Q(class_assigned__name__icontains=search_query)
            )
        
        # Filter by teacher
        teacher = self.request.GET.get('teacher')
        if teacher:
            queryset = queryset.filter(teacher_id=teacher)
        
        # Filter by subject
        subject = self.request.GET.get('subject')
        if subject:
            queryset = queryset.filter(subject_id=subject)
        
        # Filter by class
        class_assigned = self.request.GET.get('class_assigned')
        if class_assigned:
            queryset = queryset.filter(class_assigned_id=class_assigned)
        
        # Filter by academic year
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        return queryset.order_by('class_assigned__name', 'subject__name', 'teacher__first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teachers'] = User.objects.filter(role='TEACHER')
        context['subjects'] = Subject.objects.all()
        context['classes'] = Class.objects.all()
        context['academic_years'] = AcademicYear.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_teacher'] = self.request.GET.get('teacher', '')
        context['selected_subject'] = self.request.GET.get('subject', '')
        context['selected_class_assigned'] = self.request.GET.get('class_assigned', '')
        context['selected_academic_year'] = self.request.GET.get('academic_year', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAllocationAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Subject Allocations"""
    model = SubjectAllocation
    form_class = SubjectAllocationForm
    template_name = 'classes/admin/subject_allocation_form.html'
    success_url = reverse_lazy('classes:admin_subject_allocation_list')
    success_message = "Subject allocation created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Allocate Subject to Teacher'
        context['button_text'] = 'Create Allocation'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAllocationAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Subject Allocations"""
    model = SubjectAllocation
    form_class = SubjectAllocationForm
    template_name = 'classes/admin/subject_allocation_form.html'
    success_url = reverse_lazy('classes:admin_subject_allocation_list')
    success_message = "Subject allocation updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Subject Allocation'
        context['button_text'] = 'Update Allocation'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAllocationAdminDetailView(DetailView):
    """Admin detail view for Subject Allocations"""
    model = SubjectAllocation
    template_name = 'classes/admin/subject_allocation_detail.html'
    context_object_name = 'allocation'


@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAllocationAdminDeleteView(DeleteView):
    """Admin delete view for Subject Allocations"""
    model = SubjectAllocation
    template_name = 'classes/admin/subject_allocation_confirm_delete.html'
    success_url = reverse_lazy('classes:admin_subject_allocation_list')
    
    def delete(self, request, *args, **kwargs):
        allocation = self.get_object()
        messages.success(self.request, f"Subject allocation deleted successfully.")
        return super().delete(request, *args, **kwargs)
