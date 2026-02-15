from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.decorators import method_decorator

from .models import SchoolProfile, AcademicYear, Term, Holiday
from .forms import SchoolProfileForm, AcademicYearForm, TermForm, HolidayForm
from apps.accounts.decorators import admin_required


# ============ SchoolProfile Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class SchoolProfileAdminListView(ListView):
    """Admin list view for School Profile"""
    model = SchoolProfile
    template_name = 'school/admin/school_profile_list.html'
    context_object_name = 'profiles'
    
    def get_queryset(self):
        return SchoolProfile.objects.all()


@method_decorator([login_required, admin_required], name='dispatch')
class SchoolProfileAdminDetailView(DetailView):
    """Admin detail view for School Profile"""
    model = SchoolProfile
    template_name = 'school/admin/school_profile_detail.html'
    context_object_name = 'profile'


@method_decorator([login_required, admin_required], name='dispatch')
class SchoolProfileAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for School Profile"""
    model = SchoolProfile
    form_class = SchoolProfileForm
    template_name = 'school/admin/school_profile_form.html'
    success_message = "School profile updated successfully."
    
    def get_object(self, queryset=None):
        """Get the first/only school profile"""
        return SchoolProfile.objects.first()
    
    def get_success_url(self):
        return reverse_lazy('school:admin_school_profile_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit School Profile'
        context['button_text'] = 'Update Profile'
        return context


# ============ AcademicYear Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class AcademicYearAdminListView(ListView):
    """Admin list view for Academic Years"""
    model = AcademicYear
    template_name = 'school/admin/academic_year_list.html'
    context_object_name = 'academic_years'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AcademicYear.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
            )
        
        # Filter by current status
        is_current = self.request.GET.get('is_current')
        if is_current == 'true':
            queryset = queryset.filter(is_current=True)
        elif is_current == 'false':
            queryset = queryset.filter(is_current=False)
        
        return queryset.order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_is_current'] = self.request.GET.get('is_current', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class AcademicYearAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Academic Years"""
    model = AcademicYear
    form_class = AcademicYearForm
    template_name = 'school/admin/academic_year_form.html'
    success_url = reverse_lazy('school:admin_academic_year_list')
    success_message = "Academic year '%(name)s' created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Academic Year'
        context['button_text'] = 'Create Academic Year'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class AcademicYearAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Academic Years"""
    model = AcademicYear
    form_class = AcademicYearForm
    template_name = 'school/admin/academic_year_form.html'
    success_url = reverse_lazy('school:admin_academic_year_list')
    success_message = "Academic year '%(name)s' updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Academic Year: {self.object.name}'
        context['button_text'] = 'Update Academic Year'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class AcademicYearAdminDetailView(DetailView):
    """Admin detail view for Academic Years"""
    model = AcademicYear
    template_name = 'school/admin/academic_year_detail.html'
    context_object_name = 'academic_year'


@method_decorator([login_required, admin_required], name='dispatch')
class AcademicYearAdminDeleteView(DeleteView):
    """Admin delete view for Academic Years"""
    model = AcademicYear
    template_name = 'school/admin/academic_year_confirm_delete.html'
    success_url = reverse_lazy('school:admin_academic_year_list')
    
    def delete(self, request, *args, **kwargs):
        academic_year = self.get_object()
        messages.success(self.request, f"Academic year {academic_year.name} deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ Term Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class TermAdminListView(ListView):
    """Admin list view for Terms"""
    model = Term
    template_name = 'school/admin/term_list.html'
    context_object_name = 'terms'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Term.objects.select_related('academic_year').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(academic_year__name__icontains=search_query)
            )
        
        # Filter by academic year
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        # Filter by term
        term = self.request.GET.get('term')
        if term:
            queryset = queryset.filter(term=term)
        
        # Filter by current status
        is_current = self.request.GET.get('is_current')
        if is_current == 'true':
            queryset = queryset.filter(is_current=True)
        elif is_current == 'false':
            queryset = queryset.filter(is_current=False)
        
        return queryset.order_by('-academic_year__start_date', 'start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academic_years'] = AcademicYear.objects.all()
        context['term_choices'] = SchoolProfile.TermChoices.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_academic_year'] = self.request.GET.get('academic_year', '')
        context['selected_term'] = self.request.GET.get('term', '')
        context['selected_is_current'] = self.request.GET.get('is_current', '')
        
        # Import here to avoid circular imports
        from .models import SchoolProfile
        context['term_choices'] = SchoolProfile.TermChoices.choices
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TermAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Terms"""
    model = Term
    form_class = TermForm
    template_name = 'school/admin/term_form.html'
    success_url = reverse_lazy('school:admin_term_list')
    success_message = "Term created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Term'
        context['button_text'] = 'Create Term'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TermAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Terms"""
    model = Term
    form_class = TermForm
    template_name = 'school/admin/term_form.html'
    success_url = reverse_lazy('school:admin_term_list')
    success_message = "Term updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Term: {self.object.get_term_display()}'
        context['button_text'] = 'Update Term'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class TermAdminDetailView(DetailView):
    """Admin detail view for Terms"""
    model = Term
    template_name = 'school/admin/term_detail.html'
    context_object_name = 'term'


@method_decorator([login_required, admin_required], name='dispatch')
class TermAdminDeleteView(DeleteView):
    """Admin delete view for Terms"""
    model = Term
    template_name = 'school/admin/term_confirm_delete.html'
    success_url = reverse_lazy('school:admin_term_list')
    
    def delete(self, request, *args, **kwargs):
        term = self.get_object()
        messages.success(self.request, f"Term deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ Holiday Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class HolidayAdminListView(ListView):
    """Admin list view for Holidays"""
    model = Holiday
    template_name = 'school/admin/holiday_list.html'
    context_object_name = 'holidays'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Holiday.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset.order_by('start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class HolidayAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Holidays"""
    model = Holiday
    form_class = HolidayForm
    template_name = 'school/admin/holiday_form.html'
    success_url = reverse_lazy('school:admin_holiday_list')
    success_message = "Holiday '%(name)s' created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Holiday'
        context['button_text'] = 'Create Holiday'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class HolidayAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Holidays"""
    model = Holiday
    form_class = HolidayForm
    template_name = 'school/admin/holiday_form.html'
    success_url = reverse_lazy('school:admin_holiday_list')
    success_message = "Holiday '%(name)s' updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Holiday: {self.object.name}'
        context['button_text'] = 'Update Holiday'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class HolidayAdminDetailView(DetailView):
    """Admin detail view for Holidays"""
    model = Holiday
    template_name = 'school/admin/holiday_detail.html'
    context_object_name = 'holiday'


@method_decorator([login_required, admin_required], name='dispatch')
class HolidayAdminDeleteView(DeleteView):
    """Admin delete view for Holidays"""
    model = Holiday
    template_name = 'school/admin/holiday_confirm_delete.html'
    success_url = reverse_lazy('school:admin_holiday_list')
    
    def delete(self, request, *args, **kwargs):
        holiday = self.get_object()
        messages.success(self.request, f"Holiday {holiday.name} deleted successfully.")
        return super().delete(request, *args, **kwargs)
