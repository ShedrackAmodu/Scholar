from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.decorators import method_decorator

from .models import Event, EventRSVP, Notice, NoticeRead, Assignment, AssignmentSubmission, Notification, ClassMessage
from .forms import EventForm, NoticeForm, AssignmentForm
from apps.accounts.decorators import admin_required
from apps.classes.models import Class, Subject


# ============ Event Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class EventAdminListView(ListView):
    """Admin list view for Events"""
    model = Event
    template_name = 'announcements/admin/event_list.html'
    context_object_name = 'events'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Event.objects.select_related('created_by').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query)
            )
        
        # Filter by event type
        event_type = self.request.GET.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by featured status
        is_featured = self.request.GET.get('is_featured')
        if is_featured:
            queryset = queryset.filter(is_featured=is_featured == 'True')
        
        # Filter by public status
        is_public = self.request.GET.get('is_public')
        if is_public:
            queryset = queryset.filter(is_public=is_public == 'True')
        
        # Filter by date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(start_date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(end_date__lte=date_to)
        
        return queryset.order_by('-is_featured', '-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_types'] = Event.EventType.choices
        context['priorities'] = Event.Priority.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_event_type'] = self.request.GET.get('event_type', '')
        context['selected_priority'] = self.request.GET.get('priority', '')
        context['selected_is_featured'] = self.request.GET.get('is_featured', '')
        context['selected_is_public'] = self.request.GET.get('is_public', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class EventAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Events"""
    model = Event
    form_class = EventForm
    template_name = 'announcements/admin/event_form.html'
    success_url = reverse_lazy('announcements:admin_event_list')
    success_message = "Event '%(title)s' created successfully."
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Event'
        context['button_text'] = 'Create Event'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class EventAdminDetailView(DetailView):
    """Admin detail view for Events"""
    model = Event
    template_name = 'announcements/admin/event_detail.html'
    context_object_name = 'event'
    
    def get_queryset(self):
        return Event.objects.select_related('created_by')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rsvps'] = self.object.rsvps.all()
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class EventAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Events"""
    model = Event
    form_class = EventForm
    template_name = 'announcements/admin/event_form.html'
    success_url = reverse_lazy('announcements:admin_event_list')
    success_message = "Event '%(title)s' updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Event: {self.object.title}'
        context['button_text'] = 'Update Event'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class EventAdminDeleteView(DeleteView):
    """Admin delete view for Events"""
    model = Event
    template_name = 'announcements/admin/event_confirm_delete.html'
    success_url = reverse_lazy('announcements:admin_event_list')
    
    def delete(self, request, *args, **kwargs):
        event = self.get_object()
        messages.success(self.request, f"Event '{event.title}' deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ Notice Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class NoticeAdminListView(ListView):
    """Admin list view for Notices"""
    model = Notice
    template_name = 'announcements/admin/notice_list.html'
    context_object_name = 'notices'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Notice.objects.select_related('created_by').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(summary__icontains=search_query)
            )
        
        # Filter by notice type
        notice_type = self.request.GET.get('notice_type')
        if notice_type:
            queryset = queryset.filter(notice_type=notice_type)
        
        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by pinned status
        is_pinned = self.request.GET.get('is_pinned')
        if is_pinned:
            queryset = queryset.filter(is_pinned=is_pinned == 'True')
        
        # Filter by public status
        is_public = self.request.GET.get('is_public')
        if is_public:
            queryset = queryset.filter(is_public=is_public == 'True')
        
        # Filter by publish date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(publish_date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(publish_date__lte=date_to)
        
        return queryset.order_by('-is_pinned', '-publish_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notice_types'] = Notice.NoticeType.choices
        context['priorities'] = Notice.Priority.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_notice_type'] = self.request.GET.get('notice_type', '')
        context['selected_priority'] = self.request.GET.get('priority', '')
        context['selected_is_pinned'] = self.request.GET.get('is_pinned', '')
        context['selected_is_public'] = self.request.GET.get('is_public', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class NoticeAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Notices"""
    model = Notice
    form_class = NoticeForm
    template_name = 'announcements/admin/notice_form.html'
    success_url = reverse_lazy('announcements:admin_notice_list')
    success_message = "Notice '%(title)s' created successfully."
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Notice'
        context['button_text'] = 'Create Notice'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class NoticeAdminDetailView(DetailView):
    """Admin detail view for Notices"""
    model = Notice
    template_name = 'announcements/admin/notice_detail.html'
    context_object_name = 'notice'
    
    def get_queryset(self):
        return Notice.objects.select_related('created_by')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reads'] = self.object.reads.all()
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class NoticeAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Notices"""
    model = Notice
    form_class = NoticeForm
    template_name = 'announcements/admin/notice_form.html'
    success_url = reverse_lazy('announcements:admin_notice_list')
    success_message = "Notice '%(title)s' updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Notice: {self.object.title}'
        context['button_text'] = 'Update Notice'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class NoticeAdminDeleteView(DeleteView):
    """Admin delete view for Notices"""
    model = Notice
    template_name = 'announcements/admin/notice_confirm_delete.html'
    success_url = reverse_lazy('announcements:admin_notice_list')
    
    def delete(self, request, *args, **kwargs):
        notice = self.get_object()
        messages.success(self.request, f"Notice '{notice.title}' deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ Assignment Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class AssignmentAdminListView(ListView):
    """Admin list view for Assignments"""
    model = Assignment
    template_name = 'announcements/admin/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Assignment.objects.select_related(
            'subject', 'class_assigned', 'created_by'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by class
        class_assigned = self.request.GET.get('class')
        if class_assigned:
            queryset = queryset.filter(class_assigned_id=class_assigned)
        
        # Filter by subject
        subject = self.request.GET.get('subject')
        if subject:
            queryset = queryset.filter(subject_id=subject)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by grading status
        is_graded = self.request.GET.get('is_graded')
        if is_graded:
            queryset = queryset.filter(is_graded=is_graded == 'True')
        
        # Filter by due date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(due_date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(due_date__lte=date_to)
        
        return queryset.order_by('-due_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Assignment.Status.choices
        context['classes'] = Class.objects.all()
        context['subjects'] = Subject.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_class'] = self.request.GET.get('class', '')
        context['selected_subject'] = self.request.GET.get('subject', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_is_graded'] = self.request.GET.get('is_graded', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class AssignmentAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Assignments"""
    model = Assignment
    form_class = AssignmentForm
    template_name = 'announcements/admin/assignment_form.html'
    success_url = reverse_lazy('announcements:admin_assignment_list')
    success_message = "Assignment '%(title)s' created successfully."
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Assignment'
        context['button_text'] = 'Create Assignment'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class AssignmentAdminDetailView(DetailView):
    """Admin detail view for Assignments"""
    model = Assignment
    template_name = 'announcements/admin/assignment_detail.html'
    context_object_name = 'assignment'
    
    def get_queryset(self):
        return Assignment.objects.select_related(
            'subject', 'class_assigned', 'created_by'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submissions'] = self.object.submissions.all()
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class AssignmentAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Assignments"""
    model = Assignment
    form_class = AssignmentForm
    template_name = 'announcements/admin/assignment_form.html'
    success_url = reverse_lazy('announcements:admin_assignment_list')
    success_message = "Assignment '%(title)s' updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Assignment: {self.object.title}'
        context['button_text'] = 'Update Assignment'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class AssignmentAdminDeleteView(DeleteView):
    """Admin delete view for Assignments"""
    model = Assignment
    template_name = 'announcements/admin/assignment_confirm_delete.html'
    success_url = reverse_lazy('announcements:admin_assignment_list')
    
    def delete(self, request, *args, **kwargs):
        assignment = self.get_object()
        messages.success(self.request, f"Assignment '{assignment.title}' deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ AssignmentSubmission Admin List & Detail Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class AssignmentSubmissionAdminListView(ListView):
    """Admin list view for Assignment Submissions"""
    model = AssignmentSubmission
    template_name = 'announcements/admin/assignment_submission_list.html'
    context_object_name = 'submissions'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = AssignmentSubmission.objects.select_related(
            'assignment', 'student', 'student__user', 'graded_by'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(assignment__title__icontains=search_query) |
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query)
            )
        
        # Filter by assignment
        assignment = self.request.GET.get('assignment')
        if assignment:
            queryset = queryset.filter(assignment_id=assignment)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by submission date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(submitted_at__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(submitted_at__lte=date_to)
        
        return queryset.order_by('-submitted_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = AssignmentSubmission.Status.choices
        context['assignments'] = Assignment.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_assignment'] = self.request.GET.get('assignment', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class AssignmentSubmissionAdminDetailView(DetailView):
    """Admin detail view for Assignment Submissions"""
    model = AssignmentSubmission
    template_name = 'announcements/admin/assignment_submission_detail.html'
    context_object_name = 'submission'
    
    def get_queryset(self):
        return AssignmentSubmission.objects.select_related(
            'assignment', 'student', 'student__user', 'graded_by'
        )


# ============ Notification Admin List View ============

@method_decorator([login_required, admin_required], name='dispatch')
class NotificationAdminListView(ListView):
    """Admin list view for Notifications"""
    model = Notification
    template_name = 'announcements/admin/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = Notification.objects.select_related(
            'recipient', 'sender'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(message__icontains=search_query)
            )
        
        # Filter by notification type
        notification_type = self.request.GET.get('notification_type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filter by read status
        is_read = self.request.GET.get('is_read')
        if is_read:
            queryset = queryset.filter(is_read=is_read == 'True')
        
        # Filter by creation date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notification_types'] = Notification.NotificationType.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_notification_type'] = self.request.GET.get('notification_type', '')
        context['selected_is_read'] = self.request.GET.get('is_read', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class NotificationAdminDetailView(DetailView):
    """Admin detail view for Notifications"""
    model = Notification
    template_name = 'announcements/admin/notification_detail.html'
    context_object_name = 'notification'
    
    def get_queryset(self):
        return Notification.objects.select_related(
            'recipient', 'sender'
        )


# ============ ClassMessage Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class ClassMessageAdminListView(ListView):
    """Admin list view for Class Messages"""
    model = ClassMessage
    template_name = 'announcements/admin/class_message_list.html'
    context_object_name = 'messages'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ClassMessage.objects.select_related(
            'class_assigned', 'sender'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(subject__icontains=search_query) |
                Q(message__icontains=search_query) |
                Q(class_assigned__name__icontains=search_query)
            )
        
        # Filter by class
        class_assigned = self.request.GET.get('class')
        if class_assigned:
            queryset = queryset.filter(class_assigned_id=class_assigned)
        
        # Filter by send to students
        send_to_students = self.request.GET.get('send_to_students')
        if send_to_students:
            queryset = queryset.filter(send_to_students=send_to_students == 'True')
        
        # Filter by send to parents
        send_to_parents = self.request.GET.get('send_to_parents')
        if send_to_parents:
            queryset = queryset.filter(send_to_parents=send_to_parents == 'True')
        
        # Filter by sent date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(sent_at__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(sent_at__lte=date_to)
        
        return queryset.order_by('-sent_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_class'] = self.request.GET.get('class', '')
        context['selected_send_to_students'] = self.request.GET.get('send_to_students', '')
        context['selected_send_to_parents'] = self.request.GET.get('send_to_parents', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ClassMessageAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Class Messages"""
    model = ClassMessage
    fields = ['class_assigned', 'subject', 'message', 'attachment', 'send_to_students', 'send_to_parents']
    template_name = 'announcements/admin/class_message_form.html'
    success_url = reverse_lazy('announcements:admin_class_message_list')
    success_message = "Class message sent successfully."
    
    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Send Class Message'
        context['button_text'] = 'Send Message'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ClassMessageAdminDetailView(DetailView):
    """Admin detail view for Class Messages"""
    model = ClassMessage
    template_name = 'announcements/admin/class_message_detail.html'
    context_object_name = 'message'
    
    def get_queryset(self):
        return ClassMessage.objects.select_related(
            'class_assigned', 'sender'
        )


@method_decorator([login_required, admin_required], name='dispatch')
class ClassMessageAdminDeleteView(DeleteView):
    """Admin delete view for Class Messages"""
    model = ClassMessage
    template_name = 'announcements/admin/class_message_confirm_delete.html'
    success_url = reverse_lazy('announcements:admin_class_message_list')
    
    def delete(self, request, *args, **kwargs):
        message = self.get_object()
        messages.success(self.request, f"Class message deleted successfully.")
        return super().delete(request, *args, **kwargs)
