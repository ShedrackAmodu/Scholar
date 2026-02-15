from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.decorators import method_decorator

from .models import (
    Assessment, SubjectAssessment, Score, SubjectScore,
    ReportCard, ClassPerformance
)
from .forms import (
    AssessmentForm, SubjectAssessmentForm
)
from apps.accounts.decorators import admin_required
from apps.classes.models import Class, Subject, SubjectAllocation, ClassLevel
from apps.students.models import Student
from apps.school.models import AcademicYear, Term

# Admin CRUD Views for Assessment Model

@method_decorator([login_required, admin_required], name='dispatch')
class AssessmentAdminListView(ListView):
    """Admin list view for Assessments"""
    model = Assessment
    template_name = 'academics/admin/assessment_list.html'
    context_object_name = 'assessments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Assessment.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query)
            )
        
        # Filter by type
        assessment_type = self.request.GET.get('type')
        if assessment_type:
            queryset = queryset.filter(assessment_type=assessment_type)
        
        # Filter by class level
        class_level = self.request.GET.get('class_level')
        if class_level:
            queryset = queryset.filter(class_level_id=class_level)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assessment_types'] = Assessment.AssessmentType.choices
        context['class_levels'] = ClassLevel.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_type'] = self.request.GET.get('type', '')
        context['selected_class_level'] = self.request.GET.get('class_level', '')
        return context

@method_decorator([login_required, admin_required], name='dispatch')
class AssessmentAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Assessments"""
    model = Assessment
    form_class = AssessmentForm
    template_name = 'academics/admin/assessment_form.html'
    success_url = reverse_lazy('academics:admin_assessment_list')
    success_message = "Assessment '%(name)s' created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Assessment'
        context['button_text'] = 'Create Assessment'
        return context

@method_decorator([login_required, admin_required], name='dispatch')
class AssessmentAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Assessments"""
    model = Assessment
    form_class = AssessmentForm
    template_name = 'academics/admin/assessment_form.html'
    success_url = reverse_lazy('academics:admin_assessment_list')
    success_message = "Assessment '%(name)s' updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Assessment: {self.object.name}'
        context['button_text'] = 'Update Assessment'
        return context

@method_decorator([login_required, admin_required], name='dispatch')
class AssessmentAdminDetailView(DetailView):
    """Admin detail view for Assessments"""
    model = Assessment
    template_name = 'academics/admin/assessment_detail.html'
    context_object_name = 'assessment'

@method_decorator([login_required, admin_required], name='dispatch')
class AssessmentAdminDeleteView(DeleteView):
    """Admin delete view for Assessments"""
    model = Assessment
    template_name = 'academics/admin/assessment_confirm_delete.html'
    success_url = reverse_lazy('academics:admin_assessment_list')
    success_message = "Assessment deleted successfully."
    
    def delete(self, request, *args, **kwargs):
        assessment = self.get_object()
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Admin CRUD Views for SubjectAssessment Model

@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAssessmentAdminListView(ListView):
    """Admin list view for SubjectAssessments"""
    model = SubjectAssessment
    template_name = 'academics/admin/subject_assessment_list.html'
    context_object_name = 'subject_assessments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SubjectAssessment.objects.select_related(
            'subject', 'assessment', 'academic_year', 'term'
        )
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(subject__name__icontains=search_query) |
                Q(assessment__name__icontains=search_query) |
                Q(academic_year__name__icontains=search_query)
            )
        
        # Filter by academic year
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        # Filter by subject
        subject = self.request.GET.get('subject')
        if subject:
            queryset = queryset.filter(subject_id=subject)
        
        # Filter by term
        term = self.request.GET.get('term')
        if term:
            queryset = queryset.filter(term=term)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academic_years'] = AcademicYear.objects.all()
        context['subjects'] = Subject.objects.all()
        context['terms'] = Term.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_academic_year'] = self.request.GET.get('academic_year', '')
        context['selected_subject'] = self.request.GET.get('subject', '')
        context['selected_term'] = self.request.GET.get('term', '')
        return context

@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAssessmentAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for SubjectAssessments"""
    model = SubjectAssessment
    form_class = SubjectAssessmentForm
    template_name = 'academics/admin/subject_assessment_form.html'
    success_url = reverse_lazy('academics:admin_subject_assessment_list')
    success_message = "Subject assessment created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Subject Assessment'
        context['button_text'] = 'Create Subject Assessment'
        return context

@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAssessmentAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for SubjectAssessments"""
    model = SubjectAssessment
    form_class = SubjectAssessmentForm
    template_name = 'academics/admin/subject_assessment_form.html'
    success_url = reverse_lazy('academics:admin_subject_assessment_list')
    success_message = "Subject assessment updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Subject Assessment'
        context['button_text'] = 'Update Subject Assessment'
        return context

@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAssessmentAdminDetailView(DetailView):
    """Admin detail view for SubjectAssessments"""
    model = SubjectAssessment
    template_name = 'academics/admin/subject_assessment_detail.html'
    context_object_name = 'subject_assessment'

@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAssessmentAdminDeleteView(DeleteView):
    """Admin delete view for SubjectAssessments"""
    model = SubjectAssessment
    template_name = 'academics/admin/subject_assessment_confirm_delete.html'
    success_url = reverse_lazy('academics:admin_subject_assessment_list')
    success_message = "Subject assessment deleted successfully."
    
    def delete(self, request, *args, **kwargs):
        subject_assessment = self.get_object()
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Admin CRUD Views for Score Model

@method_decorator([login_required, admin_required], name='dispatch')
class ScoreAdminListView(ListView):
    """Admin list view for Scores"""
    model = Score
    template_name = 'academics/admin/score_list.html'
    context_object_name = 'scores'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Score.objects.select_related(
            'student__user', 'subject_assessment__subject', 
            'subject_assessment__assessment', 'recorded_by'
        )
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query) |
                Q(student__admission_number__icontains=search_query) |
                Q(subject_assessment__subject__name__icontains=search_query)
            )
        
        # Filter by student
        student = self.request.GET.get('student')
        if student:
            queryset = queryset.filter(student_id=student)
        
        # Filter by subject
        subject = self.request.GET.get('subject')
        if subject:
            queryset = queryset.filter(subject_assessment__subject_id=subject)
        
        # Filter by assessment
        assessment = self.request.GET.get('assessment')
        if assessment:
            queryset = queryset.filter(subject_assessment__assessment_id=assessment)
        
        # Filter by approval status
        approved = self.request.GET.get('approved')
        if approved == 'true':
            queryset = queryset.filter(is_approved=True)
        elif approved == 'false':
            queryset = queryset.filter(is_approved=False)
        
        return queryset.order_by('-recorded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.all()
        context['subjects'] = Subject.objects.all()
        context['assessments'] = Assessment.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_student'] = self.request.GET.get('student', '')
        context['selected_subject'] = self.request.GET.get('subject', '')
        context['selected_assessment'] = self.request.GET.get('assessment', '')
        context['selected_approved'] = self.request.GET.get('approved', '')
        return context

@method_decorator([login_required, admin_required], name='dispatch')
class ScoreAdminDetailView(DetailView):
    """Admin detail view for Scores"""
    model = Score
    template_name = 'academics/admin/score_detail.html'
    context_object_name = 'score'

@method_decorator([login_required, admin_required], name='dispatch')
class ScoreAdminDeleteView(DeleteView):
    """Admin delete view for Scores"""
    model = Score
    template_name = 'academics/admin/score_confirm_delete.html'
    success_url = reverse_lazy('academics:admin_score_list')
    success_message = "Score deleted successfully."
    
    def delete(self, request, *args, **kwargs):
        score = self.get_object()
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Admin CRUD Views for SubjectScore Model

@method_decorator([login_required, admin_required], name='dispatch')
class SubjectScoreAdminListView(ListView):
    """Admin list view for SubjectScores"""
    model = SubjectScore
    template_name = 'academics/admin/subject_score_list.html'
    context_object_name = 'subject_scores'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SubjectScore.objects.select_related(
            'student__user', 'subject'
        )
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query) |
                Q(student__admission_number__icontains=search_query) |
                Q(subject__name__icontains=search_query)
            )
        
        # Filter by student
        student = self.request.GET.get('student')
        if student:
            queryset = queryset.filter(student_id=student)
        
        # Filter by subject
        subject = self.request.GET.get('subject')
        if subject:
            queryset = queryset.filter(subject_id=subject)
        
        return queryset.order_by('-total_score')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.all()
        context['subjects'] = Subject.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_student'] = self.request.GET.get('student', '')
        context['selected_subject'] = self.request.GET.get('subject', '')
        return context

@method_decorator([login_required, admin_required], name='dispatch')
class SubjectScoreAdminDetailView(DetailView):
    """Admin detail view for SubjectScores"""
    model = SubjectScore
    template_name = 'academics/admin/subject_score_detail.html'
    context_object_name = 'subject_score'

# Admin CRUD Views for ReportCard Model

@method_decorator([login_required, admin_required], name='dispatch')
class ReportCardAdminListView(ListView):
    """Admin list view for ReportCards"""
    model = ReportCard
    template_name = 'academics/admin/report_card_list.html'
    context_object_name = 'report_cards'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ReportCard.objects.select_related(
            'student__user', 'class_assigned'
        )
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query) |
                Q(student__admission_number__icontains=search_query) |
                Q(class_assigned__name__icontains=search_query)
            )
        
        # Filter by student
        student = self.request.GET.get('student')
        if student:
            queryset = queryset.filter(student_id=student)
        
        # Filter by class
        class_assigned = self.request.GET.get('class_assigned')
        if class_assigned:
            queryset = queryset.filter(class_assigned_id=class_assigned)
        
        # Filter by term
        term = self.request.GET.get('term')
        if term:
            queryset = queryset.filter(term=term)
        
        # Filter by approval status
        approved = self.request.GET.get('approved')
        if approved == 'true':
            queryset = queryset.filter(is_approved=True)
        elif approved == 'false':
            queryset = queryset.filter(is_approved=False)
        
        return queryset.order_by('-generated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.all()
        context['classes'] = Class.objects.all()
        context['terms'] = Term.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_student'] = self.request.GET.get('student', '')
        context['selected_class'] = self.request.GET.get('class_assigned', '')
        context['selected_term'] = self.request.GET.get('term', '')
        context['selected_approved'] = self.request.GET.get('approved', '')
        return context

@method_decorator([login_required, admin_required], name='dispatch')
class ReportCardAdminDetailView(DetailView):
    """Admin detail view for ReportCards"""
    model = ReportCard
    template_name = 'academics/admin/report_card_detail.html'
    context_object_name = 'report_card'

@method_decorator([login_required, admin_required], name='dispatch')
class ReportCardAdminDeleteView(DeleteView):
    """Admin delete view for ReportCards"""
    model = ReportCard
    template_name = 'academics/admin/report_card_confirm_delete.html'
    success_url = reverse_lazy('academics:admin_report_card_list')
    success_message = "Report card deleted successfully."
    
    def delete(self, request, *args, **kwargs):
        report_card = self.get_object()
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Admin CRUD Views for ClassPerformance Model

@method_decorator([login_required, admin_required], name='dispatch')
class ClassPerformanceAdminListView(ListView):
    """Admin list view for ClassPerformances"""
    model = ClassPerformance
    template_name = 'academics/admin/class_performance_list.html'
    context_object_name = 'class_performances'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ClassPerformance.objects.select_related(
            'class_assigned'
        )
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(class_assigned__name__icontains=search_query)
            )
        
        # Filter by class
        class_assigned = self.request.GET.get('class_assigned')
        if class_assigned:
            queryset = queryset.filter(class_assigned_id=class_assigned)
        
        # Filter by term
        term = self.request.GET.get('term')
        if term:
            queryset = queryset.filter(term=term)
        
        return queryset.order_by('-class_average')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.all()
        context['terms'] = Term.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_class'] = self.request.GET.get('class_assigned', '')
        context['selected_term'] = self.request.GET.get('term', '')
        return context

@method_decorator([login_required, admin_required], name='dispatch')
class ClassPerformanceAdminDetailView(DetailView):
    """Admin detail view for ClassPerformances"""
    model = ClassPerformance
    template_name = 'academics/admin/class_performance_detail.html'
    context_object_name = 'class_performance'

@method_decorator([login_required, admin_required], name='dispatch')
class ClassPerformanceAdminDeleteView(DeleteView):
    """Admin delete view for ClassPerformances"""
    model = ClassPerformance
    template_name = 'academics/admin/class_performance_confirm_delete.html'
    success_url = reverse_lazy('academics:admin_class_performance_list')
    success_message = "Class performance deleted successfully."
    
    def delete(self, request, *args, **kwargs):
        class_performance = self.get_object()
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)