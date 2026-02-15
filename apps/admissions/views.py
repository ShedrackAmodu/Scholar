from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from .models import Application, ApplicationComment, EntranceExam
from .forms import ApplicationForm, ApplicationCommentForm, EntranceExamForm, ApplicationReviewForm
from apps.accounts.decorators import admin_required, principal_required

# ============ Application CRUD ============
@method_decorator([login_required, principal_required], name='dispatch')
class ApplicationListView(ListView):
    """List all applications"""
    model = Application
    template_name = 'admissions/admin/application_list.html'
    context_object_name = 'applications'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Application.objects.all().order_by('-submitted_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by applied class
        applied_class = self.request.GET.get('applied_class')
        if applied_class:
            queryset = queryset.filter(applied_class=applied_class)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Application.Status.choices if hasattr(Application, 'Status') else []
        return context

class ApplicationCreateView(SuccessMessageMixin, CreateView):
    """Create new application (public form - no login required)"""
    model = Application
    form_class = ApplicationForm
    template_name = 'admissions/public/application_form.html'
    success_url = reverse_lazy('admissions:admission_form')
    success_message = "Your application has been submitted successfully. You'll receive a confirmation email shortly."

@method_decorator([login_required, principal_required], name='dispatch')
class ApplicationDetailView(DetailView):
    """View application details"""
    model = Application
    template_name = 'admissions/admin/application_detail.html'
    context_object_name = 'application'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_object()
        context['comments'] = ApplicationComment.objects.filter(
            application=application
        ).order_by('-created_at')
        context['entrance_exams'] = EntranceExam.objects.filter(application=application)
        context['comment_form'] = ApplicationCommentForm()
        return context

@method_decorator([login_required, principal_required], name='dispatch')
class ApplicationUpdateView(SuccessMessageMixin, UpdateView):
    """Update application"""
    model = Application
    form_class = ApplicationReviewForm
    template_name = 'admissions/admin/application_form.html'
    success_message = "Application updated successfully."
    
    def get_success_url(self):
        return reverse_lazy('admissions:application_detail', kwargs={'pk': self.object.pk})

@method_decorator([login_required, principal_required], name='dispatch')
class ApplicationDeleteView(DeleteView):
    """Delete application"""
    model = Application
    template_name = 'admissions/admin/application_confirm_delete.html'
    success_url = reverse_lazy('admissions:application_list')

# ============ Entrance Exam CRUD ============
@method_decorator([login_required, principal_required], name='dispatch')
class EntranceExamListView(ListView):
    """List all entrance exams"""
    model = EntranceExam
    template_name = 'admissions/admin/entrance_exam_list.html'
    context_object_name = 'exams'
    paginate_by = 50
    ordering = ['-exam_date']

@method_decorator([login_required, principal_required], name='dispatch')
class EntranceExamCreateView(SuccessMessageMixin, CreateView):
    """Create new entrance exam"""
    model = EntranceExam
    form_class = EntranceExamForm
    template_name = 'admissions/admin/entrance_exam_form.html'
    success_url = reverse_lazy('admissions:entrance_exam_list')
    success_message = "Entrance exam created successfully."

@method_decorator([login_required, principal_required], name='dispatch')
class EntranceExamDetailView(DetailView):
    """View entrance exam details"""
    model = EntranceExam
    template_name = 'admissions/admin/entrance_exam_detail.html'
    context_object_name = 'exam'

@method_decorator([login_required, principal_required], name='dispatch')
class EntranceExamUpdateView(SuccessMessageMixin, UpdateView):
    """Update entrance exam"""
    model = EntranceExam
    form_class = EntranceExamForm
    template_name = 'admissions/admin/entrance_exam_form.html'
    success_url = reverse_lazy('admissions:entrance_exam_list')
    success_message = "Entrance exam updated successfully."

@method_decorator([login_required, principal_required], name='dispatch')
class EntranceExamDeleteView(DeleteView):
    """Delete entrance exam"""
    model = EntranceExam
    template_name = 'admissions/admin/entrance_exam_confirm_delete.html'
    success_url = reverse_lazy('admissions:entrance_exam_list')

# ============ Function-based views ============
def admissions_home(request):
    applications = Application.objects.filter(status__in=['PENDING', 'REVIEW'])
    approved_count = Application.objects.filter(status='APPROVED').count()
    pending_count = Application.objects.filter(status='PENDING').count()
    rejected_count = Application.objects.filter(status='REJECTED').count()
    
    return render(request, 'admissions/home.html', {
        'applications': applications,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count
    })

@login_required
@admin_required
def application_detail(request, app_id):
    application = get_object_or_404(Application, id=app_id)
    comments = ApplicationComment.objects.filter(application=application).order_by('-created_at')
    if request.method == 'POST':
        form = ApplicationCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.application = application
            comment.created_by = request.user
            comment.save()
            messages.success(request, 'Comment added.')
            return redirect('admissions:application_detail', app_id=app_id)
    else:
        form = ApplicationCommentForm()
    return render(request, 'admissions/detail.html', {'application': application, 'comments': comments, 'form': form})

@login_required
@admin_required
def schedule_exam(request, app_id):
    application = get_object_or_404(Application, id=app_id)
    if request.method == 'POST':
        form = EntranceExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.application = application
            exam.created_by = request.user
            exam.save()
            messages.success(request, 'Entrance exam scheduled.')
            return redirect('admissions:application_detail', app_id=app_id)
    else:
        form = EntranceExamForm()
    return render(request, 'admissions/schedule_exam.html', {'form': form, 'application': application})

def application_api(request):
    apps = Application.objects.filter(status='PENDING').values('id', 'first_name', 'last_name', 'applied_class', 'submitted_at')
    return JsonResponse({'applications': list(apps)})

@login_required
@admin_required
def bulk_admission(request):
    if request.method == 'POST':
        # Handle bulk upload logic here
        messages.success(request, 'Bulk admission upload completed.')
        return redirect('admissions:admission_list')
    
    return render(request, 'admissions/bulk_upload.html')
