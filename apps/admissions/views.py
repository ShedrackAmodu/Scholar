from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Application, ApplicationComment, EntranceExam
from .forms import ApplicationForm, ApplicationCommentForm, EntranceExamForm
from apps.accounts.decorators import admin_required

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
