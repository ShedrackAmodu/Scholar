from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.decorators import method_decorator

from .models import AttendanceSession, Attendance, AttendanceSummary
from .forms import AttendanceSessionForm
from apps.accounts.decorators import admin_required
from apps.classes.models import Class
from apps.students.models import Student
from apps.school.models import AcademicYear


# ============ AttendanceSession Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class AttendanceSessionAdminListView(ListView):
    """Admin list view for Attendance Sessions"""
    model = AttendanceSession
    template_name = 'attendance/admin/attendance_session_list.html'
    context_object_name = 'sessions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AttendanceSession.objects.select_related(
            'class_assigned', 'academic_year', 'session_taken_by', 'closed_by'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(class_assigned__name__icontains=search_query) |
                Q(session_taken_by__first_name__icontains=search_query) |
                Q(session_taken_by__last_name__icontains=search_query)
            )
        
        # Filter by class
        class_assigned = self.request.GET.get('class')
        if class_assigned:
            queryset = queryset.filter(class_assigned_id=class_assigned)
        
        # Filter by academic year
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        # Filter by term
        term = self.request.GET.get('term')
        if term:
            queryset = queryset.filter(term=term)
        
        # Filter by date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Filter by closed status
        is_closed = self.request.GET.get('is_closed')
        if is_closed:
            queryset = queryset.filter(is_closed=is_closed == 'True')
        
        return queryset.order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.all()
        context['academic_years'] = AcademicYear.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_class'] = self.request.GET.get('class', '')
        context['selected_academic_year'] = self.request.GET.get('academic_year', '')
        context['selected_term'] = self.request.GET.get('term', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['selected_is_closed'] = self.request.GET.get('is_closed', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class AttendanceSessionAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Attendance Sessions"""
    model = AttendanceSession
    form_class = AttendanceSessionForm
    template_name = 'attendance/admin/attendance_session_form.html'
    success_url = reverse_lazy('attendance:admin_attendance_session_list')
    success_message = "Attendance session created successfully."
    
    def form_valid(self, form):
        form.instance.session_taken_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Attendance Session'
        context['button_text'] = 'Create Session'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class AttendanceSessionAdminDetailView(DetailView):
    """Admin detail view for Attendance Sessions"""
    model = AttendanceSession
    template_name = 'attendance/admin/attendance_session_detail.html'
    context_object_name = 'session'
    
    def get_queryset(self):
        return AttendanceSession.objects.select_related(
            'class_assigned', 'academic_year', 'session_taken_by', 'closed_by'
        )


@method_decorator([login_required, admin_required], name='dispatch')
class AttendanceSessionAdminDeleteView(DeleteView):
    """Admin delete view for Attendance Sessions"""
    model = AttendanceSession
    template_name = 'attendance/admin/attendance_session_confirm_delete.html'
    success_url = reverse_lazy('attendance:admin_attendance_session_list')
    
    def delete(self, request, *args, **kwargs):
        session = self.get_object()
        messages.success(
            self.request, 
            f"Attendance session for {session.class_assigned} on {session.date} deleted successfully."
        )
        return super().delete(request, *args, **kwargs)


# ============ Attendance Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class AttendanceAdminListView(ListView):
    """Admin list view for Attendance Records"""
    model = Attendance
    template_name = 'attendance/admin/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = Attendance.objects.select_related(
            'session', 'session__class_assigned', 'student', 'student__user', 'approved_by'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query) |
                Q(student__admission_number__icontains=search_query)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by class
        class_assigned = self.request.GET.get('class')
        if class_assigned:
            queryset = queryset.filter(session__class_assigned_id=class_assigned)
        
        # Filter by academic year
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(session__academic_year_id=academic_year)
        
        # Filter by term
        term = self.request.GET.get('term')
        if term:
            queryset = queryset.filter(session__term=term)
        
        # Filter by date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(session__date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(session__date__lte=date_to)
        
        # Filter by approval status
        is_approved = self.request.GET.get('is_approved')
        if is_approved:
            queryset = queryset.filter(is_approved=is_approved == 'True')
        
        return queryset.order_by('-session__date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Attendance.Status.choices
        context['classes'] = Class.objects.all()
        context['academic_years'] = AcademicYear.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_class'] = self.request.GET.get('class', '')
        context['selected_academic_year'] = self.request.GET.get('academic_year', '')
        context['selected_term'] = self.request.GET.get('term', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['selected_is_approved'] = self.request.GET.get('is_approved', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class AttendanceAdminDetailView(DetailView):
    """Admin detail view for Attendance Records"""
    model = Attendance
    template_name = 'attendance/admin/attendance_detail.html'
    context_object_name = 'attendance'
    
    def get_queryset(self):
        return Attendance.objects.select_related(
            'session', 'session__class_assigned', 'student', 'student__user', 'approved_by'
        )


@method_decorator([login_required, admin_required], name='dispatch')
class AttendanceAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Attendance Records"""
    model = Attendance
    fields = ['status', 'time_in', 'time_out', 'minutes_late', 'reason_for_absence', 'note', 'is_approved']
    template_name = 'attendance/admin/attendance_form.html'
    success_url = reverse_lazy('attendance:admin_attendance_list')
    success_message = "Attendance record updated successfully."
    
    def form_valid(self, form):
        if form.instance.is_approved and not form.instance.approved_by:
            form.instance.approved_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Attendance: {self.object.student}'
        context['button_text'] = 'Update Attendance'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class AttendanceAdminDeleteView(DeleteView):
    """Admin delete view for Attendance Records"""
    model = Attendance
    template_name = 'attendance/admin/attendance_confirm_delete.html'
    success_url = reverse_lazy('attendance:admin_attendance_list')
    
    def delete(self, request, *args, **kwargs):
        attendance = self.get_object()
        messages.success(
            self.request, 
            f"Attendance record for {attendance.student} deleted successfully."
        )
        return super().delete(request, *args, **kwargs)


# ============ AttendanceSummary Admin List View ============

@method_decorator([login_required, admin_required], name='dispatch')
class AttendanceSummaryAdminListView(ListView):
    """Admin list view for Attendance Summaries"""
    model = AttendanceSummary
    template_name = 'attendance/admin/attendance_summary_list.html'
    context_object_name = 'summaries'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AttendanceSummary.objects.select_related(
            'student', 'student__user', 'academic_year'
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
        
        # Filter by term
        term = self.request.GET.get('term')
        if term:
            queryset = queryset.filter(term=term)
        
        # Filter by attendance percentage
        min_percentage = self.request.GET.get('min_percentage')
        if min_percentage:
            try:
                queryset = queryset.filter(attendance_percentage__gte=float(min_percentage))
            except (ValueError, TypeError):
                pass
        
        max_percentage = self.request.GET.get('max_percentage')
        if max_percentage:
            try:
                queryset = queryset.filter(attendance_percentage__lte=float(max_percentage))
            except (ValueError, TypeError):
                pass
        
        return queryset.order_by('-academic_year', '-attendance_percentage')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academic_years'] = AcademicYear.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_academic_year'] = self.request.GET.get('academic_year', '')
        context['selected_term'] = self.request.GET.get('term', '')
        context['min_percentage'] = self.request.GET.get('min_percentage', '')
        context['max_percentage'] = self.request.GET.get('max_percentage', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class AttendanceSummaryAdminDetailView(DetailView):
    """Admin detail view for Attendance Summaries"""
    model = AttendanceSummary
    template_name = 'attendance/admin/attendance_summary_detail.html'
    context_object_name = 'summary'
    
    def get_queryset(self):
        return AttendanceSummary.objects.select_related(
            'student', 'student__user', 'academic_year'
        )
