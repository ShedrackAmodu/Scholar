from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.decorators import method_decorator

from .models import Student, StudentDocument, StudentHistory
from .forms import StudentForm, StudentDocumentForm, StudentHistoryForm
from apps.accounts.decorators import admin_required


# ============ Student Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class StudentAdminListView(ListView):
    """Admin list view for Students"""
    model = Student
    template_name = 'students/admin/student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Student.objects.select_related('user', 'current_class').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(admission_number__icontains=search_query)
            )
        
        # Filter by class
        current_class = self.request.GET.get('class')
        if current_class:
            queryset = queryset.filter(current_class_id=current_class)
        
        # Filter by enrollment status
        enrollment_status = self.request.GET.get('enrollment_status')
        if enrollment_status:
            queryset = queryset.filter(enrollment_status=enrollment_status)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.classes.models import Class
        context['classes'] = Class.objects.all()
        context['enrollment_statuses'] = Student.EnrollmentStatus.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_class'] = self.request.GET.get('class', '')
        context['selected_enrollment_status'] = self.request.GET.get('enrollment_status', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class StudentAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Students"""
    model = Student
    form_class = StudentForm
    template_name = 'students/admin/student_form.html'
    success_url = reverse_lazy('students:admin_student_list')
    success_message = "Student created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Student'
        context['button_text'] = 'Create Student'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class StudentAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Students"""
    model = Student
    form_class = StudentForm
    template_name = 'students/admin/student_form.html'
    success_url = reverse_lazy('students:admin_student_list')
    success_message = "Student updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Student: {self.object.user.get_full_name()}'
        context['button_text'] = 'Update Student'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class StudentAdminDetailView(DetailView):
    """Admin detail view for Students"""
    model = Student
    template_name = 'students/admin/student_detail.html'
    context_object_name = 'student'


@method_decorator([login_required, admin_required], name='dispatch')
class StudentAdminDeleteView(DeleteView):
    """Admin delete view for Students"""
    model = Student
    template_name = 'students/admin/student_confirm_delete.html'
    success_url = reverse_lazy('students:admin_student_list')
    
    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        messages.success(self.request, f"Student {student.user.get_full_name()} deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ StudentDocument Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class StudentDocumentAdminListView(ListView):
    """Admin list view for Student Documents"""
    model = StudentDocument
    template_name = 'students/admin/student_document_list.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = StudentDocument.objects.select_related('student', 'student__user').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query) |
                Q(name__icontains=search_query)
            )
        
        # Filter by student
        student = self.request.GET.get('student')
        if student:
            queryset = queryset.filter(student_id=student)
        
        return queryset.order_by('-uploaded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_student'] = self.request.GET.get('student', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class StudentDocumentAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Student Documents"""
    model = StudentDocument
    form_class = StudentDocumentForm
    template_name = 'students/admin/student_document_form.html'
    success_url = reverse_lazy('students:admin_student_document_list')
    success_message = "Document uploaded successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Upload Student Document'
        context['button_text'] = 'Upload Document'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class StudentDocumentAdminDetailView(DetailView):
    """Admin detail view for Student Documents"""
    model = StudentDocument
    template_name = 'students/admin/student_document_detail.html'
    context_object_name = 'document'


@method_decorator([login_required, admin_required], name='dispatch')
class StudentDocumentAdminDeleteView(DeleteView):
    """Admin delete view for Student Documents"""
    model = StudentDocument
    template_name = 'students/admin/student_document_confirm_delete.html'
    success_url = reverse_lazy('students:admin_student_document_list')
    
    def delete(self, request, *args, **kwargs):
        document = self.get_object()
        messages.success(self.request, f"Document {document.name} deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ StudentHistory Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class StudentHistoryAdminListView(ListView):
    """Admin list view for Student History"""
    model = StudentHistory
    template_name = 'students/admin/student_history_list.html'
    context_object_name = 'histories'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = StudentHistory.objects.select_related(
            'student', 'student__user', 'class_assigned', 'academic_year'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query) |
                Q(student__admission_number__icontains=search_query)
            )
        
        # Filter by academic year
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        return queryset.order_by('-date_from')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.school.models import AcademicYear
        context['academic_years'] = AcademicYear.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_academic_year'] = self.request.GET.get('academic_year', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class StudentHistoryAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Student History"""
    model = StudentHistory
    form_class = StudentHistoryForm
    template_name = 'students/admin/student_history_form.html'
    success_url = reverse_lazy('students:admin_student_history_list')
    success_message = "Student history record created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Student History Record'
        context['button_text'] = 'Create Record'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class StudentHistoryAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Student History"""
    model = StudentHistory
    form_class = StudentHistoryForm
    template_name = 'students/admin/student_history_form.html'
    success_url = reverse_lazy('students:admin_student_history_list')
    success_message = "Student history record updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit History Record: {self.object.student.user.get_full_name()}'
        context['button_text'] = 'Update Record'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class StudentHistoryAdminDetailView(DetailView):
    """Admin detail view for Student History"""
    model = StudentHistory
    template_name = 'students/admin/student_history_detail.html'
    context_object_name = 'history'


@method_decorator([login_required, admin_required], name='dispatch')
class StudentHistoryAdminDeleteView(DeleteView):
    """Admin delete view for Student History"""
    model = StudentHistory
    template_name = 'students/admin/student_history_confirm_delete.html'
    success_url = reverse_lazy('students:admin_student_history_list')
    
    def delete(self, request, *args, **kwargs):
        history = self.get_object()
        messages.success(self.request, f"Student history record deleted successfully.")
        return super().delete(request, *args, **kwargs)
