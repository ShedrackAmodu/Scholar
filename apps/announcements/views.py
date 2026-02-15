from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.utils import timezone
from .models import Event, Notice, Assignment, AssignmentSubmission
from .forms import EventForm, NoticeForm, AssignmentForm
from apps.accounts.decorators import admin_required, teacher_required, principal_required

# ============ Event CRUD ============
@method_decorator([login_required, admin_required], name='dispatch')
class EventListView(ListView):
    """List all events"""
    model = Event
    template_name = 'announcements/admin/event_list.html'
    context_object_name = 'events'
    paginate_by = 50
    ordering = ['-start_date']

@method_decorator([login_required, admin_required], name='dispatch')
class EventCreateView(SuccessMessageMixin, CreateView):
    """Create new event"""
    model = Event
    form_class = EventForm
    template_name = 'announcements/admin/event_form.html'
    success_url = reverse_lazy('announcements:event_list')
    success_message = "Event %(title)s created successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class EventDetailView(DetailView):
    """View event details"""
    model = Event
    template_name = 'announcements/admin/event_detail.html'
    context_object_name = 'event'

@method_decorator([login_required, admin_required], name='dispatch')
class EventUpdateView(SuccessMessageMixin, UpdateView):
    """Update event"""
    model = Event
    form_class = EventForm
    template_name = 'announcements/admin/event_form.html'
    success_url = reverse_lazy('announcements:event_list')
    success_message = "Event %(title)s updated successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class EventDeleteView(DeleteView):
    """Delete event"""
    model = Event
    template_name = 'announcements/admin/event_confirm_delete.html'
    success_url = reverse_lazy('announcements:event_list')

# ============ Notice CRUD ============
@method_decorator([login_required, admin_required], name='dispatch')
class NoticeListView(ListView):
    """List all notices"""
    model = Notice
    template_name = 'announcements/admin/notice_list.html'
    context_object_name = 'notices'
    paginate_by = 50
    ordering = ['-publish_date']

@method_decorator([login_required, admin_required], name='dispatch')
class NoticeCreateView(SuccessMessageMixin, CreateView):
    """Create new notice"""
    model = Notice
    form_class = NoticeForm
    template_name = 'announcements/admin/notice_form.html'
    success_url = reverse_lazy('announcements:notice_list')
    success_message = "Notice %(title)s created successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class NoticeDetailView(DetailView):
    """View notice details"""
    model = Notice
    template_name = 'announcements/admin/notice_detail.html'
    context_object_name = 'notice'

@method_decorator([login_required, admin_required], name='dispatch')
class NoticeUpdateView(SuccessMessageMixin, UpdateView):
    """Update notice"""
    model = Notice
    form_class = NoticeForm
    template_name = 'announcements/admin/notice_form.html'
    success_url = reverse_lazy('announcements:notice_list')
    success_message = "Notice %(title)s updated successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class NoticeDeleteView(DeleteView):
    """Delete notice"""
    model = Notice
    template_name = 'announcements/admin/notice_confirm_delete.html'
    success_url = reverse_lazy('announcements:notice_list')

# ============ Assignment CRUD ============
@method_decorator([login_required, teacher_required], name='dispatch')
class AssignmentListView(ListView):
    """List all assignments"""
    model = Assignment
    template_name = 'announcements/admin/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 50
    ordering = ['-created_at']

@method_decorator([login_required, teacher_required], name='dispatch')
class AssignmentCreateView(SuccessMessageMixin, CreateView):
    """Create new assignment"""
    model = Assignment
    form_class = AssignmentForm
    template_name = 'announcements/admin/assignment_form.html'
    success_url = reverse_lazy('announcements:assignment_list')
    success_message = "Assignment %(title)s created successfully."

@method_decorator([login_required], name='dispatch')
class AssignmentDetailView(DetailView):
    """View assignment details"""
    model = Assignment
    template_name = 'announcements/admin/assignment_detail.html'
    context_object_name = 'assignment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment = self.get_object()
        context['submissions'] = AssignmentSubmission.objects.filter(
            assignment=assignment
        ).select_related('student')
        return context

@method_decorator([login_required, teacher_required], name='dispatch')
class AssignmentUpdateView(SuccessMessageMixin, UpdateView):
    """Update assignment"""
    model = Assignment
    form_class = AssignmentForm
    template_name = 'announcements/admin/assignment_form.html'
    success_url = reverse_lazy('announcements:assignment_list')
    success_message = "Assignment %(title)s updated successfully."

@method_decorator([login_required, teacher_required], name='dispatch')
class AssignmentDeleteView(DeleteView):
    """Delete assignment"""
    model = Assignment
    template_name = 'announcements/admin/assignment_confirm_delete.html'
    success_url = reverse_lazy('announcements:assignment_list')

# ============ Function-based views ============
@login_required
def noticeboard(request):
    notices = Notice.objects.filter(is_public=True).order_by('-publish_date')[:20]
    events = Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')[:10]
    context = {'notices': notices, 'events': events, 'title': 'Noticeboard'}
    return render(request, 'announcements/noticeboard.html', context)

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    context = {'event': event, 'title': event.title}
    return render(request, 'announcements/event_detail.html', context)


@login_required
def notice_detail(request, notice_id):
    """Display a single notice."""
    notice = get_object_or_404(Notice, id=notice_id)
    context = {'notice': notice, 'title': notice.title}
    return render(request, 'announcements/notice_detail.html', context)

def announcements_api(request):
    """Return latest announcements and notices as JSON"""
    latest_notices = Notice.objects.filter(is_public=True).order_by('-created_at')[:10]
    data = []
    for notice in latest_notices:
        data.append({
            'title': notice.title,
            'summary': notice.summary,
            'published_at': notice.created_at.isoformat(),
            'url': f'/announcements/notices/{notice.id}/'
        })
    return JsonResponse({'announcements': data})
