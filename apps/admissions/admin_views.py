from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.decorators import method_decorator

from .models import Application, ApplicationComment, EntranceExam
from .forms import ApplicationForm
from apps.accounts.decorators import admin_required
from apps.classes.models import ClassLevel


# ============ Application Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class ApplicationAdminListView(ListView):
    """Admin list view for Admission Applications"""
    model = Application
    template_name = 'admissions/admin/application_list.html'
    context_object_name = 'applications'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Application.objects.select_related(
            'applying_for_class', 'reviewed_by'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(application_number__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        
        # Filter by application status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by class level applying for
        class_level = self.request.GET.get('class_level')
        if class_level:
            queryset = queryset.filter(applying_for_class_id=class_level)
        
        # Filter by gender
        gender = self.request.GET.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # Filter by application date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(application_date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(application_date__lte=date_to)
        
        return queryset.order_by('-application_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Application.ApplicationStatus.choices
        context['genders'] = Application.Gender.choices
        context['class_levels'] = ClassLevel.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_class_level'] = self.request.GET.get('class_level', '')
        context['selected_gender'] = self.request.GET.get('gender', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ApplicationAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Applications"""
    model = Application
    form_class = ApplicationForm
    template_name = 'admissions/admin/application_form.html'
    success_url = reverse_lazy('admissions:admin_application_list')
    success_message = "Application for %(first_name)s %(last_name)s created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Application'
        context['button_text'] = 'Create Application'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ApplicationAdminDetailView(DetailView):
    """Admin detail view for Applications"""
    model = Application
    template_name = 'admissions/admin/application_detail.html'
    context_object_name = 'application'
    
    def get_queryset(self):
        return Application.objects.select_related(
            'applying_for_class', 'reviewed_by'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['entrance_exams'] = self.object.entrance_exams.all()
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ApplicationAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Applications"""
    model = Application
    form_class = ApplicationForm
    template_name = 'admissions/admin/application_form.html'
    success_url = reverse_lazy('admissions:admin_application_list')
    success_message = "Application for %(first_name)s %(last_name)s updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Application: {self.object.first_name} {self.object.last_name}'
        context['button_text'] = 'Update Application'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ApplicationAdminDeleteView(DeleteView):
    """Admin delete view for Applications"""
    model = Application
    template_name = 'admissions/admin/application_confirm_delete.html'
    success_url = reverse_lazy('admissions:admin_application_list')
    
    def delete(self, request, *args, **kwargs):
        application = self.get_object()
        messages.success(
            self.request, 
            f"Application '{application.application_number}' for {application.first_name} {application.last_name} deleted successfully."
        )
        return super().delete(request, *args, **kwargs)


# ============ ApplicationComment Admin Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class ApplicationCommentAdminListView(ListView):
    """Admin list view for Application Comments"""
    model = ApplicationComment
    template_name = 'admissions/admin/application_comment_list.html'
    context_object_name = 'comments'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = ApplicationComment.objects.select_related(
            'application', 'user'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(application__application_number__icontains=search_query) |
                Q(application__first_name__icontains=search_query) |
                Q(application__last_name__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(comment__icontains=search_query)
            )
        
        # Filter by application
        application = self.request.GET.get('application')
        if application:
            queryset = queryset.filter(application_id=application)
        
        # Filter by date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = Application.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_application'] = self.request.GET.get('application', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ApplicationCommentAdminDetailView(DetailView):
    """Admin detail view for Application Comments"""
    model = ApplicationComment
    template_name = 'admissions/admin/application_comment_detail.html'
    context_object_name = 'comment'
    
    def get_queryset(self):
        return ApplicationComment.objects.select_related(
            'application', 'user'
        )


@method_decorator([login_required, admin_required], name='dispatch')
class ApplicationCommentAdminDeleteView(DeleteView):
    """Admin delete view for Application Comments"""
    model = ApplicationComment
    template_name = 'admissions/admin/application_comment_confirm_delete.html'
    success_url = reverse_lazy('admissions:admin_application_comment_list')
    
    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        messages.success(self.request, f"Comment deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ EntranceExam Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class EntranceExamAdminListView(ListView):
    """Admin list view for Entrance Exams"""
    model = EntranceExam
    template_name = 'admissions/admin/entrance_exam_list.html'
    context_object_name = 'exams'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = EntranceExam.objects.select_related(
            'application', 'conducted_by'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(application__application_number__icontains=search_query) |
                Q(application__first_name__icontains=search_query) |
                Q(application__last_name__icontains=search_query) |
                Q(conducted_by__first_name__icontains=search_query) |
                Q(conducted_by__last_name__icontains=search_query)
            )
        
        # Filter by application
        application = self.request.GET.get('application')
        if application:
            queryset = queryset.filter(application_id=application)
        
        # Filter by exam result
        is_passed = self.request.GET.get('is_passed')
        if is_passed:
            queryset = queryset.filter(is_passed=is_passed == 'True')
        
        # Filter by date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(exam_date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(exam_date__lte=date_to)
        
        # Filter by minimum score
        min_score = self.request.GET.get('min_score')
        if min_score:
            try:
                queryset = queryset.filter(total_score__gte=float(min_score))
            except (ValueError, TypeError):
                pass
        
        return queryset.order_by('-exam_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = Application.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_application'] = self.request.GET.get('application', '')
        context['selected_is_passed'] = self.request.GET.get('is_passed', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['min_score'] = self.request.GET.get('min_score', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class EntranceExamAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Entrance Exams"""
    model = EntranceExam
    fields = ['application', 'exam_date', 'english_score', 'mathematics_score', 
              'general_knowledge', 'is_passed', 'remarks']
    template_name = 'admissions/admin/entrance_exam_form.html'
    success_url = reverse_lazy('admissions:admin_entrance_exam_list')
    success_message = "Entrance exam created successfully."
    
    def form_valid(self, form):
        form.instance.conducted_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Entrance Exam'
        context['button_text'] = 'Create Exam'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class EntranceExamAdminDetailView(DetailView):
    """Admin detail view for Entrance Exams"""
    model = EntranceExam
    template_name = 'admissions/admin/entrance_exam_detail.html'
    context_object_name = 'exam'
    
    def get_queryset(self):
        return EntranceExam.objects.select_related(
            'application', 'conducted_by'
        )


@method_decorator([login_required, admin_required], name='dispatch')
class EntranceExamAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Entrance Exams"""
    model = EntranceExam
    fields = ['application', 'exam_date', 'english_score', 'mathematics_score', 
              'general_knowledge', 'is_passed', 'remarks']
    template_name = 'admissions/admin/entrance_exam_form.html'
    success_url = reverse_lazy('admissions:admin_entrance_exam_list')
    success_message = "Entrance exam updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Entrance Exam'
        context['button_text'] = 'Update Exam'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class EntranceExamAdminDeleteView(DeleteView):
    """Admin delete view for Entrance Exams"""
    model = EntranceExam
    template_name = 'admissions/admin/entrance_exam_confirm_delete.html'
    success_url = reverse_lazy('admissions:admin_entrance_exam_list')
    
    def delete(self, request, *args, **kwargs):
        exam = self.get_object()
        messages.success(
            self.request, 
            f"Entrance exam for {exam.application.first_name} {exam.application.last_name} deleted successfully."
        )
        return super().delete(request, *args, **kwargs)
