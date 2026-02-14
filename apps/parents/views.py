from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django import forms

from .models import Parent, ParentStudentRelationship
from .forms import (
    ParentForm, ParentStudentRelationshipForm, LinkParentToStudentForm,
    BulkParentLinkForm
)
from apps.accounts.models import User
from apps.accounts.decorators import admin_required, parent_required
from apps.students.models import Student
from apps.academics.models import Score, ReportCard
from apps.attendance.models import Attendance
from apps.announcements.models import Notification, Event

# Parent List Views
@method_decorator([login_required, admin_required], name='dispatch')
class ParentListView(ListView):
    """List all parents"""
    model = Parent
    template_name = 'parents/admin/parent_list.html'
    context_object_name = 'parents'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Parent.objects.select_related('user').prefetch_related('children')
        
        # Search
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(phone__icontains=query)
            )
        
        return queryset

@method_decorator([login_required, admin_required], name='dispatch')
class ParentDetailView(DetailView):
    """View parent details"""
    model = Parent
    template_name = 'parents/admin/parent_detail.html'
    context_object_name = 'parent'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent = self.get_object()
        
        # Get relationships
        context['relationships'] = ParentStudentRelationship.objects.filter(
            parent=parent
        ).select_related('student__user')
        
        # Get recent notifications
        context['notifications'] = Notification.objects.filter(
            recipient=parent.user
        ).order_by('-created_at')[:20]
        
        return context

# Parent CRUD Views
@method_decorator([login_required, admin_required], name='dispatch')
class ParentCreateView(SuccessMessageMixin, CreateView):
    """Create new parent"""
    model = Parent
    form_class = ParentForm
    template_name = 'parents/admin/parent_form.html'
    success_url = reverse_lazy('parents:parent_list')
    success_message = "Parent %(user)s created successfully."
    
    def form_valid(self, form):
        # Create user account
        user = User.objects.create_user(
            username=form.cleaned_data.get('email').split('@')[0],
            email=form.cleaned_data.get('email'),
            password='Parent@123',  # Default password
            first_name=form.cleaned_data.get('first_name'),
            last_name=form.cleaned_data.get('last_name'),
            role='PARENT'
        )
        form.instance.user = user
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add user fields to form
        form.fields['first_name'] = forms.CharField(max_length=100)
        form.fields['last_name'] = forms.CharField(max_length=100)
        form.fields['email'] = forms.EmailField()
        return form

@method_decorator([login_required, admin_required], name='dispatch')
class ParentUpdateView(SuccessMessageMixin, UpdateView):
    """Update parent"""
    model = Parent
    form_class = ParentForm
    template_name = 'parents/admin/parent_form.html'
    success_url = reverse_lazy('parents:parent_list')
    success_message = "Parent %(user)s updated successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class ParentDeleteView(DeleteView):
    """Delete parent"""
    model = Parent
    template_name = 'parents/admin/parent_confirm_delete.html'
    success_url = reverse_lazy('parents:parent_list')
    success_message = "Parent deleted successfully."
    
    def delete(self, request, *args, **kwargs):
        parent = self.get_object()
        # Also delete user account
        parent.user.delete()
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Parent-Student Relationship Views
@login_required
@admin_required
def link_parent_to_student(request):
    """Link existing parent to student"""
    if request.method == 'POST':
        form = LinkParentToStudentForm(request.POST)
        if form.is_valid():
            parent = form.cleaned_data['parent']
            student_id = request.POST.get('student_id')
            student = get_object_or_404(Student, id=student_id)
            
            ParentStudentRelationship.objects.create(
                parent=parent,
                student=student,
                relationship=form.cleaned_data['relationship'],
                is_primary_contact=form.cleaned_data['is_primary_contact']
            )
            
            messages.success(request, f"{parent.user.get_full_name()} linked to {student.user.get_full_name()} successfully.")
            return redirect('parents:parent_detail', pk=parent.id)
    else:
        form = LinkParentToStudentForm()
        student_id = request.GET.get('student_id')
    
    context = {
        'form': form,
        'student_id': student_id,
        'title': 'Link Parent to Student'
    }
    return render(request, 'parents/admin/link_parent_form.html', context)

@login_required
@admin_required
def unlink_parent_from_student(request, pk):
    """Remove parent-student relationship"""
    relationship = get_object_or_404(ParentStudentRelationship, pk=pk)
    parent_id = relationship.parent.id
    
    if request.method == 'POST':
        relationship.delete()
        messages.success(request, "Parent unlinked from student successfully.")
        return redirect('parents:parent_detail', pk=parent_id)
    
    context = {
        'relationship': relationship,
        'title': 'Confirm Unlink'
    }
    return render(request, 'parents/admin/unlink_confirm.html', context)

@login_required
@admin_required
def bulk_link_parents(request):
    """Bulk link parents to students"""
    if request.method == 'POST':
        form = BulkParentLinkForm(request.POST)
        if form.is_valid():
            parent = form.cleaned_data['parent']
            students = form.cleaned_data['students']
            relationship = form.cleaned_data['relationship']
            
            for student in students:
                ParentStudentRelationship.objects.get_or_create(
                    parent=parent,
                    student=student,
                    defaults={'relationship': relationship}
                )
            
            messages.success(request, f"Parent linked to {students.count()} students successfully.")
            return redirect('parents:parent_detail', pk=parent.id)
    else:
        form = BulkParentLinkForm()
    
    context = {
        'form': form,
        'title': 'Bulk Link Parents'
    }
    return render(request, 'parents/admin/bulk_link.html', context)

# Parent Dashboard Views
@login_required
@parent_required
def parent_dashboard(request):
    """Parent dashboard"""
    parent = request.user.parent_profile
    
    # Get children
    children = parent.children.filter(enrollment_status='ACTIVE')
    
    # Get notifications
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:10]
    
    # Get upcoming events
    upcoming_events = Event.objects.filter(
        start_date__gte=timezone.now(),
        is_public=True
    ).order_by('start_date')[:5]
    
    context = {
        'parent': parent,
        'children': children,
        'notifications': notifications,
        'upcoming_events': upcoming_events,
        'title': 'Parent Dashboard'
    }
    return render(request, 'parents/dashboard/dashboard.html', context)

@login_required
@parent_required
def child_dashboard(request, child_id):
    """View specific child's information"""
    parent = request.user.parent_profile
    child = get_object_or_404(Student, id=child_id)
    
    # Verify parent owns this child
    if not parent.children.filter(id=child_id).exists():
        messages.error(request, "You don't have permission to view this child.")
        return redirect('parents:dashboard')
    
    # Get recent scores
    recent_scores = Score.objects.filter(
        student=child
    ).select_related('subject_assessment__subject').order_by('-recorded_at')[:10]
    
    # Get attendance
    attendance = Attendance.objects.filter(
        student=child
    ).select_related('session').order_by('-session__date')[:20]
    
    # Get report cards
    report_cards = ReportCard.objects.filter(
        student=child
    ).order_by('-academic_year', '-term')
    
    context = {
        'child': child,
        'recent_scores': recent_scores,
        'attendance': attendance,
        'report_cards': report_cards,
        'title': f"{child.user.get_full_name()}'s Dashboard"
    }
    return render(request, 'parents/dashboard/child_dashboard.html', context)

@login_required
@parent_required
def child_scores(request, child_id):
    """View all scores for a child"""
    parent = request.user.parent_profile
    child = get_object_or_404(Student, id=child_id)
    
    if not parent.children.filter(id=child_id).exists():
        messages.error(request, "You don't have permission to view this child.")
        return redirect('parents:dashboard')
    
    scores = Score.objects.filter(
        student=child
    ).select_related(
        'subject_assessment__subject',
        'subject_assessment__assessment'
    ).order_by('-subject_assessment__academic_year', '-subject_assessment__term')
    
    # Group by term
    terms = {}
    for score in scores:
        key = f"{score.subject_assessment.academic_year}_{score.subject_assessment.term}"
        if key not in terms:
            terms[key] = {
                'academic_year': score.subject_assessment.academic_year,
                'term': score.subject_assessment.term,
                'scores': []
            }
        terms[key]['scores'].append(score)
    
    context = {
        'child': child,
        'terms': terms.values(),
        'title': f"{child.user.get_full_name()}'s Scores"
    }
    return render(request, 'parents/dashboard/child_scores.html', context)

@login_required
@parent_required
def child_attendance(request, child_id):
    """View attendance for a child"""
    parent = request.user.parent_profile
    child = get_object_or_404(Student, id=child_id)
    
    if not parent.children.filter(id=child_id).exists():
        messages.error(request, "You don't have permission to view this child.")
        return redirect('parents:dashboard')
    
    attendance = Attendance.objects.filter(
        student=child
    ).select_related('session').order_by('-session__date')
    
    # Calculate statistics
    total_days = attendance.count()
    present_days = attendance.filter(status='P').count()
    absent_days = attendance.filter(status='A').count()
    late_days = attendance.filter(status='L').count()
    
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    context = {
        'child': child,
        'attendance': attendance,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
        'attendance_percentage': attendance_percentage,
        'title': f"{child.user.get_full_name()}'s Attendance"
    }
    return render(request, 'parents/dashboard/child_attendance.html', context)

@login_required
@parent_required
def child_report_cards(request, child_id):
    """View report cards for a child"""
    parent = request.user.parent_profile
    child = get_object_or_404(Student, id=child_id)
    
    if not parent.children.filter(id=child_id).exists():
        messages.error(request, "You don't have permission to view this child.")
        return redirect('parents:dashboard')
    
    report_cards = ReportCard.objects.filter(
        student=child
    ).order_by('-academic_year', '-term')
    
    context = {
        'child': child,
        'report_cards': report_cards,
        'title': f"{child.user.get_full_name()}'s Report Cards"
    }
    return render(request, 'parents/dashboard/child_report_cards.html', context)

# API Views
@login_required
def get_parent_children(request):
    """API endpoint to get children of current parent"""
    if request.user.role != 'PARENT':
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    parent = request.user.parent_profile
    children = parent.children.filter(
        enrollment_status='ACTIVE'
    ).select_related('user').values(
        'id', 'user__first_name', 'user__last_name', 'admission_number', 'current_class__name'
    )
    
    return JsonResponse(list(children), safe=False)

@login_required
@admin_required
def search_parents(request):
    """API endpoint to search parents"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    parents = Parent.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(user__email__icontains=query)
    ).select_related('user')[:10].values(
        'id', 'user__first_name', 'user__last_name', 'user__email', 'phone'
    )
    
    return JsonResponse(list(parents), safe=False)
