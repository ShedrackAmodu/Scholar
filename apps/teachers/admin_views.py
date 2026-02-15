from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.decorators import method_decorator

from .models import Teacher, TeacherQualification, TeacherSubjectExpertise, TeacherLeave
from .forms import TeacherForm, TeacherQualificationForm, TeacherSubjectExpertiseForm, TeacherLeaveForm
from apps.accounts.decorators import admin_required


# ============ Teacher Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class TeacherAdminListView(ListView):
    """Admin list view for Teachers"""
    model = Teacher
    template_name = 'teachers/admin/teacher_list.html'
    context_object_name = 'teachers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Teacher.objects.select_related('user').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(staff_id__icontains=search_query)
            )
        
        # Filter by employment type
        employment_type = self.request.GET.get('employment_type')
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)
        
        # Filter by active status
        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=is_active == 'True')
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employment_types'] = Teacher.EmploymentType.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_employment_type'] = self.request.GET.get('employment_type', '')
        context['selected_is_active'] = self.request.GET.get('is_active', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Teachers"""
    model = Teacher
    form_class = TeacherForm
    template_name = 'teachers/admin/teacher_form.html'
    success_url = reverse_lazy('teachers:admin_teacher_list')
    success_message = "Teacher created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Teacher'
        context['button_text'] = 'Create Teacher'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Teachers"""
    model = Teacher
    form_class = TeacherForm
    template_name = 'teachers/admin/teacher_form.html'
    success_url = reverse_lazy('teachers:admin_teacher_list')
    success_message = "Teacher updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Teacher: {self.object.user.get_full_name()}'
        context['button_text'] = 'Update Teacher'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherAdminDetailView(DetailView):
    """Admin detail view for Teachers"""
    model = Teacher
    template_name = 'teachers/admin/teacher_detail.html'
    context_object_name = 'teacher'


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherAdminDeleteView(DeleteView):
    """Admin delete view for Teachers"""
    model = Teacher
    template_name = 'teachers/admin/teacher_confirm_delete.html'
    success_url = reverse_lazy('teachers:admin_teacher_list')
    
    def delete(self, request, *args, **kwargs):
        teacher = self.get_object()
        messages.success(self.request, f"Teacher {teacher.user.get_full_name()} deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ TeacherQualification Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class TeacherQualificationAdminListView(ListView):
    """Admin list view for Teacher Qualifications"""
    model = TeacherQualification
    template_name = 'teachers/admin/teacher_qualification_list.html'
    context_object_name = 'qualifications'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = TeacherQualification.objects.select_related('teacher', 'teacher__user').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(teacher__user__first_name__icontains=search_query) |
                Q(teacher__user__last_name__icontains=search_query) |
                Q(degree__icontains=search_query)
            )
        
        # Filter by teacher
        teacher = self.request.GET.get('teacher')
        if teacher:
            queryset = queryset.filter(teacher_id=teacher)
        
        return queryset.order_by('-year_obtained')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teachers'] = Teacher.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_teacher'] = self.request.GET.get('teacher', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherQualificationAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Teacher Qualifications"""
    model = TeacherQualification
    form_class = TeacherQualificationForm
    template_name = 'teachers/admin/teacher_qualification_form.html'
    success_url = reverse_lazy('teachers:admin_teacher_qualification_list')
    success_message = "Qualification added successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Teacher Qualification'
        context['button_text'] = 'Add Qualification'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherQualificationAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Teacher Qualifications"""
    model = TeacherQualification
    form_class = TeacherQualificationForm
    template_name = 'teachers/admin/teacher_qualification_form.html'
    success_url = reverse_lazy('teachers:admin_teacher_qualification_list')
    success_message = "Qualification updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Qualification: {self.object.degree}'
        context['button_text'] = 'Update Qualification'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherQualificationAdminDetailView(DetailView):
    """Admin detail view for Teacher Qualifications"""
    model = TeacherQualification
    template_name = 'teachers/admin/teacher_qualification_detail.html'
    context_object_name = 'qualification'


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherQualificationAdminDeleteView(DeleteView):
    """Admin delete view for Teacher Qualifications"""
    model = TeacherQualification
    template_name = 'teachers/admin/teacher_qualification_confirm_delete.html'
    success_url = reverse_lazy('teachers:admin_teacher_qualification_list')
    
    def delete(self, request, *args, **kwargs):
        qualification = self.get_object()
        messages.success(self.request, f"Qualification deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ TeacherSubjectExpertise Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class TeacherSubjectExpertiseAdminListView(ListView):
    """Admin list view for Teacher Subject Expertise"""
    model = TeacherSubjectExpertise
    template_name = 'teachers/admin/teacher_subject_expertise_list.html'
    context_object_name = 'expertises'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = TeacherSubjectExpertise.objects.select_related(
            'teacher', 'teacher__user', 'subject'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(teacher__user__first_name__icontains=search_query) |
                Q(teacher__user__last_name__icontains=search_query) |
                Q(subject__name__icontains=search_query)
            )
        
        # Filter by teacher
        teacher = self.request.GET.get('teacher')
        if teacher:
            queryset = queryset.filter(teacher_id=teacher)
        
        return queryset.order_by('teacher')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teachers'] = Teacher.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_teacher'] = self.request.GET.get('teacher', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherSubjectExpertiseAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Teacher Subject Expertise"""
    model = TeacherSubjectExpertise
    form_class = TeacherSubjectExpertiseForm
    template_name = 'teachers/admin/teacher_subject_expertise_form.html'
    success_url = reverse_lazy('teachers:admin_teacher_subject_expertise_list')
    success_message = "Subject expertise added successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Subject Expertise'
        context['button_text'] = 'Add Expertise'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherSubjectExpertiseAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Teacher Subject Expertise"""
    model = TeacherSubjectExpertise
    form_class = TeacherSubjectExpertiseForm
    template_name = 'teachers/admin/teacher_subject_expertise_form.html'
    success_url = reverse_lazy('teachers:admin_teacher_subject_expertise_list')
    success_message = "Subject expertise updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Subject Expertise: {self.object.subject.name}'
        context['button_text'] = 'Update Expertise'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherSubjectExpertiseAdminDetailView(DetailView):
    """Admin detail view for Teacher Subject Expertise"""
    model = TeacherSubjectExpertise
    template_name = 'teachers/admin/teacher_subject_expertise_detail.html'
    context_object_name = 'expertise'


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherSubjectExpertiseAdminDeleteView(DeleteView):
    """Admin delete view for Teacher Subject Expertise"""
    model = TeacherSubjectExpertise
    template_name = 'teachers/admin/teacher_subject_expertise_confirm_delete.html'
    success_url = reverse_lazy('teachers:admin_teacher_subject_expertise_list')
    
    def delete(self, request, *args, **kwargs):
        expertise = self.get_object()
        messages.success(self.request, f"Subject expertise deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ TeacherLeave Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class TeacherLeaveAdminListView(ListView):
    """Admin list view for Teacher Leaves"""
    model = TeacherLeave
    template_name = 'teachers/admin/teacher_leave_list.html'
    context_object_name = 'leaves'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = TeacherLeave.objects.select_related('teacher', 'teacher__user').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(teacher__user__first_name__icontains=search_query) |
                Q(teacher__user__last_name__icontains=search_query) |
                Q(leave_type__icontains=search_query)
            )
        
        # Filter by teacher
        teacher = self.request.GET.get('teacher')
        if teacher:
            queryset = queryset.filter(teacher_id=teacher)
        
        # Filter by approval status
        is_approved = self.request.GET.get('is_approved')
        if is_approved:
            queryset = queryset.filter(is_approved=is_approved == 'True')
        
        return queryset.order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teachers'] = Teacher.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_teacher'] = self.request.GET.get('teacher', '')
        context['selected_is_approved'] = self.request.GET.get('is_approved', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherLeaveAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Teacher Leaves"""
    model = TeacherLeave
    form_class = TeacherLeaveForm
    template_name = 'teachers/admin/teacher_leave_form.html'
    success_url = reverse_lazy('teachers:admin_teacher_leave_list')
    success_message = "Leave record created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Leave Record'
        context['button_text'] = 'Create Leave'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherLeaveAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Teacher Leaves"""
    model = TeacherLeave
    form_class = TeacherLeaveForm
    template_name = 'teachers/admin/teacher_leave_form.html'
    success_url = reverse_lazy('teachers:admin_teacher_leave_list')
    success_message = "Leave record updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Leave Record'
        context['button_text'] = 'Update Leave'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherLeaveAdminDetailView(DetailView):
    """Admin detail view for Teacher Leaves"""
    model = TeacherLeave
    template_name = 'teachers/admin/teacher_leave_detail.html'
    context_object_name = 'leave'


@method_decorator([login_required, admin_required], name='dispatch')
class TeacherLeaveAdminDeleteView(DeleteView):
    """Admin delete view for Teacher Leaves"""
    model = TeacherLeave
    template_name = 'teachers/admin/teacher_leave_confirm_delete.html'
    success_url = reverse_lazy('teachers:admin_teacher_leave_list')
    
    def delete(self, request, *args, **kwargs):
        leave = self.get_object()
        messages.success(self.request, f"Leave record deleted successfully.")
        return super().delete(request, *args, **kwargs)
