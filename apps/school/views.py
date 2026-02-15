from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.http import JsonResponse
from django.utils.decorators import method_decorator

from .models import SchoolProfile, AcademicYear, Term, Holiday
from apps.announcements.models import Event, Notice
from .forms import (
    SchoolProfileForm, SchoolHoursForm, AcademicYearForm,
    TermForm, HolidayForm
)
from apps.accounts.decorators import admin_required

# Public Views
def home(request):
    """Public home page"""
    school = SchoolProfile.objects.first()
    
    # Get featured events for hero section
    featured_events = Event.objects.filter(
        is_featured=True,
        is_public=True,
        start_date__gte=timezone.now()
    ).order_by('start_date')[:5]
    
    # Get recent notices
    recent_notices = Notice.objects.filter(
        is_public=True,
        publish_date__lte=timezone.now()
    ).order_by('-is_pinned', '-publish_date')[:10]
    
    context = {
        'school': school,
        'featured_events': featured_events,
        'recent_notices': recent_notices,
        'title': 'Welcome'
    }
    return render(request, 'home.html', context)

def about_us(request):
    """About us page"""
    school = SchoolProfile.objects.first()
    context = {
        'school': school,
        'title': 'About Us'
    }
    return render(request, 'school/public/about.html', context)

def contact_us(request):
    """Contact us page"""
    school = SchoolProfile.objects.first()
    context = {
        'school': school,
        'title': 'Contact Us'
    }
    return render(request, 'school/public/contact.html', context)

def noticeboard(request):
    """Public noticeboard"""
    notices = Notice.objects.filter(
        is_public=True,
        publish_date__lte=timezone.now()
    ).order_by('-is_pinned', '-publish_date')
    
    context = {
        'notices': notices,
        'title': 'Noticeboard'
    }
    return render(request, 'school/public/noticeboard.html', context)

def events(request):
    """Public events page"""
    upcoming_events = Event.objects.filter(
        is_public=True,
        start_date__gte=timezone.now()
    ).order_by('start_date')
    
    past_events = Event.objects.filter(
        is_public=True,
        end_date__lt=timezone.now()
    ).order_by('-end_date')[:20]
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'title': 'Events'
    }
    return render(request, 'school/public/events.html', context)

# Admin Views
@login_required
@admin_required
def school_settings(request):
    """School settings management"""
    school = SchoolProfile.objects.first()
    
    if not school:
        school = SchoolProfile.objects.create(
            name="My School",
            email="info@myschool.com",
            phone="+234800000000",
            address="Your School Address"
        )
    
    if request.method == 'POST':
        form = SchoolProfileForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, "School settings updated successfully.")
            return redirect('school:settings')
    else:
        form = SchoolProfileForm(instance=school)
    
    context = {
        'form': form,
        'school': school,
        'title': 'School Settings'
    }
    return render(request, 'school/admin/settings.html', context)

@login_required
@admin_required
def school_hours(request):
    """Edit school hours"""
    school = SchoolProfile.objects.first()
    
    if request.method == 'POST':
        form = SchoolHoursForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, "School hours updated successfully.")
            return redirect('school:settings')
    else:
        form = SchoolHoursForm(instance=school)
    
    context = {
        'form': form,
        'title': 'School Hours'
    }
    return render(request, 'school/admin/hours_form.html', context)

# Academic Year Views
@method_decorator([login_required, admin_required], name='dispatch')
class AcademicYearListView(LoginRequiredMixin, ListView):
    """List all academic years"""
    model = AcademicYear
    template_name = 'school/admin/academic_year_list.html'
    context_object_name = 'academic_years'
    ordering = ['-start_date']

@method_decorator([login_required, admin_required], name='dispatch')
class AcademicYearCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create new academic year"""
    model = AcademicYear
    form_class = AcademicYearForm
    template_name = 'school/admin/academic_year_form.html'
    success_url = reverse_lazy('school:academic_year_list')
    success_message = "Academic year %(name)s created successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class AcademicYearUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update academic year"""
    model = AcademicYear
    form_class = AcademicYearForm
    template_name = 'school/admin/academic_year_form.html'
    success_url = reverse_lazy('school:academic_year_list')
    success_message = "Academic year %(name)s updated successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class AcademicYearDeleteView(LoginRequiredMixin, DeleteView):
    """Delete academic year"""
    model = AcademicYear
    template_name = 'school/admin/academic_year_confirm_delete.html'
    success_url = reverse_lazy('school:academic_year_list')
    success_message = "Academic year deleted successfully."

class AcademicYearDetailView(LoginRequiredMixin, DetailView):
    """View academic year details"""
    model = AcademicYear
    template_name = 'school/admin/academic_year_detail.html'
    context_object_name = 'academic_year'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        academic_year = self.get_object()
        context['terms'] = Term.objects.filter(academic_year=academic_year)
        context['holidays'] = Holiday.objects.filter(academic_year=academic_year)
        return context

# Term Views
@method_decorator([login_required, admin_required], name='dispatch')
class TermListView(LoginRequiredMixin, ListView):
    """List all terms"""
    model = Term
    template_name = 'school/admin/term_list.html'
    context_object_name = 'terms'
    ordering = ['-academic_year__start_date', 'start_date']

@method_decorator([login_required, admin_required], name='dispatch')
class TermCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create new term"""
    model = Term
    form_class = TermForm
    template_name = 'school/admin/term_form.html'
    success_url = reverse_lazy('school:term_list')
    success_message = "Term created successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class TermUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update term"""
    model = Term
    form_class = TermForm
    template_name = 'school/admin/term_form.html'
    success_url = reverse_lazy('school:term_list')
    success_message = "Term updated successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class TermDeleteView(LoginRequiredMixin, DeleteView):
    """Delete term"""
    model = Term
    template_name = 'school/admin/term_confirm_delete.html'
    success_url = reverse_lazy('school:term_list')
    success_message = "Term deleted successfully."

class TermDetailView(LoginRequiredMixin, DetailView):
    """View term details"""
    model = Term
    template_name = 'school/admin/term_detail.html'
    context_object_name = 'term'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        term = self.get_object()
        context['classes'] = term.academic_year.classes.all() if hasattr(term.academic_year, 'classes') else []
        return context

# Holiday Views
@method_decorator([login_required, admin_required], name='dispatch')
class HolidayListView(LoginRequiredMixin, ListView):
    """List all holidays"""
    model = Holiday
    template_name = 'school/admin/holiday_list.html'
    context_object_name = 'holidays'
    ordering = ['-start_date']

@method_decorator([login_required, admin_required], name='dispatch')
class HolidayCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create new holiday"""
    model = Holiday
    form_class = HolidayForm
    template_name = 'school/admin/holiday_form.html'
    success_url = reverse_lazy('school:holiday_list')
    success_message = "Holiday %(name)s created successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class HolidayUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update holiday"""
    model = Holiday
    form_class = HolidayForm
    template_name = 'school/admin/holiday_form.html'
    success_url = reverse_lazy('school:holiday_list')
    success_message = "Holiday %(name)s updated successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class HolidayDeleteView(LoginRequiredMixin, DeleteView):
    """Delete holiday"""
    model = Holiday
    template_name = 'school/admin/holiday_confirm_delete.html'
    success_url = reverse_lazy('school:holiday_list')
    success_message = "Holiday deleted successfully."

class HolidayDetailView(LoginRequiredMixin, DetailView):
    """View holiday details"""
    model = Holiday
    template_name = 'school/admin/holiday_detail.html'
    context_object_name = 'holiday'

# API Views (for AJAX requests)
@login_required
def get_terms_for_academic_year(request):
    """API endpoint to get terms for selected academic year"""
    academic_year_id = request.GET.get('academic_year')
    if academic_year_id:
        terms = Term.objects.filter(academic_year_id=academic_year_id).values('id', 'term')
        return JsonResponse(list(terms), safe=False)
    return JsonResponse([], safe=False)

@login_required
def set_current_academic_year(request):
    """Set current academic year"""
    if request.method == 'POST':
        year_id = request.POST.get('year_id')
        try:
            year = AcademicYear.objects.get(id=year_id)
            year.is_current = True
            year.save()
            messages.success(request, f"{year.name} set as current academic year.")
        except AcademicYear.DoesNotExist:
            messages.error(request, "Academic year not found.")
    return redirect('school:academic_year_list')

@login_required
def set_current_term(request):
    """Set current term"""
    if request.method == 'POST':
        term_id = request.POST.get('term_id')
        try:
            term = Term.objects.get(id=term_id)
            term.is_current = True
            term.save()
            
            # Update school profile
            school = SchoolProfile.objects.first()
            if school:
                school.current_term = term.term
                school.current_academic_year = term.academic_year.name
                school.save()
            
            messages.success(request, f"{term.get_term_display()} set as current term.")
        except Term.DoesNotExist:
            messages.error(request, "Term not found.")
    return redirect('school:term_list')
