from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import Event, Notice, Assignment
from .forms import EventForm, NoticeForm
from apps.accounts.decorators import admin_required, teacher_required, principal_required

@login_required
def noticeboard(request):
    notices = Notice.objects.filter(is_active=True).order_by('-publish_date')[:20]
    events = Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')[:10]
    context = {'notices': notices, 'events': events, 'title': 'Noticeboard'}
    return render(request, 'announcements/noticeboard.html', context)

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    context = {'event': event, 'title': event.title}
    return render(request, 'announcements/event_detail.html', context)

@login_required
@admin_required
def create_notice(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notice created successfully.')
            return redirect('announcements:noticeboard')
    else:
        form = NoticeForm()
    return render(request, 'announcements/create_notice.html', {'form': form})

@login_required
@admin_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event created successfully.')
            return redirect('announcements:noticeboard')
    else:
        form = EventForm()
    return render(request, 'announcements/create_event.html', {'form': form})

@login_required
def notice_detail(request, notice_id):
    """Display a single notice."""
    notice = get_object_or_404(Notice, id=notice_id)
    context = {'notice': notice, 'title': notice.title}
    return render(request, 'announcements/notice_detail.html', context)


def announcements_api(request):
    """Return latest announcements and notices as JSON"""
    latest_notices = Notice.objects.filter(is_active=True).order_by('-created_at')[:10]
    data = []
    for notice in latest_notices:
        data.append({
            'title': notice.title,
            'summary': notice.summary,
            'published_at': notice.created_at.isoformat(),
            'url': f'/announcements/notices/{notice.id}/'
        })
    return JsonResponse({'announcements': data})
