from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.decorators import method_decorator

from .models import Parent, ParentStudentRelationship
from .forms import ParentForm, ParentStudentRelationshipForm
from apps.accounts.decorators import admin_required
from apps.students.models import Student


# ============ Parent Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class ParentAdminListView(ListView):
    """Admin list view for Parents"""
    model = Parent
    template_name = 'parents/admin/parent_list.html'
    context_object_name = 'parents'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Parent.objects.select_related('user').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(occupation__icontains=search_query)
            )
        
        # Filter by notification preferences
        receive_sms = self.request.GET.get('receive_sms')
        if receive_sms == 'true':
            queryset = queryset.filter(receive_sms=True)
        elif receive_sms == 'false':
            queryset = queryset.filter(receive_sms=False)
        
        receive_email = self.request.GET.get('receive_email')
        if receive_email == 'true':
            queryset = queryset.filter(receive_email=True)
        elif receive_email == 'false':
            queryset = queryset.filter(receive_email=False)
        
        return queryset.order_by('user__first_name', 'user__last_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_receive_sms'] = self.request.GET.get('receive_sms', '')
        context['selected_receive_email'] = self.request.GET.get('receive_email', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ParentAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Parents"""
    model = Parent
    form_class = ParentForm
    template_name = 'parents/admin/parent_form.html'
    success_url = reverse_lazy('parents:admin_parent_list')
    success_message = "Parent profile created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Parent Profile'
        context['button_text'] = 'Create Parent'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ParentAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Parents"""
    model = Parent
    form_class = ParentForm
    template_name = 'parents/admin/parent_form.html'
    success_url = reverse_lazy('parents:admin_parent_list')
    success_message = "Parent profile updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Parent: {self.object.user.get_full_name()}'
        context['button_text'] = 'Update Parent'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ParentAdminDetailView(DetailView):
    """Admin detail view for Parents"""
    model = Parent
    template_name = 'parents/admin/parent_detail.html'
    context_object_name = 'parent'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['children'] = self.object.children.all()
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ParentAdminDeleteView(DeleteView):
    """Admin delete view for Parents"""
    model = Parent
    template_name = 'parents/admin/parent_confirm_delete.html'
    success_url = reverse_lazy('parents:admin_parent_list')
    
    def delete(self, request, *args, **kwargs):
        parent = self.get_object()
        messages.success(self.request, f"Parent {parent.user.get_full_name()} deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ ParentStudentRelationship Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class ParentStudentRelationshipAdminListView(ListView):
    """Admin list view for Parent-Student Relationships"""
    model = ParentStudentRelationship
    template_name = 'parents/admin/parent_student_relationship_list.html'
    context_object_name = 'relationships'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ParentStudentRelationship.objects.select_related(
            'parent', 'parent__user', 'student', 'student__user'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(parent__user__first_name__icontains=search_query) |
                Q(parent__user__last_name__icontains=search_query) |
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query) |
                Q(student__admission_number__icontains=search_query)
            )
        
        # Filter by parent
        parent = self.request.GET.get('parent')
        if parent:
            queryset = queryset.filter(parent_id=parent)
        
        # Filter by student
        student = self.request.GET.get('student')
        if student:
            queryset = queryset.filter(student_id=student)
        
        # Filter by relationship type
        relationship = self.request.GET.get('relationship')
        if relationship:
            queryset = queryset.filter(relationship=relationship)
        
        # Filter by primary contact status
        is_primary_contact = self.request.GET.get('is_primary_contact')
        if is_primary_contact == 'true':
            queryset = queryset.filter(is_primary_contact=True)
        elif is_primary_contact == 'false':
            queryset = queryset.filter(is_primary_contact=False)
        
        # Filter by notification status
        receives_notifications = self.request.GET.get('receives_notifications')
        if receives_notifications == 'true':
            queryset = queryset.filter(receives_notifications=True)
        elif receives_notifications == 'false':
            queryset = queryset.filter(receives_notifications=False)
        
        return queryset.order_by('parent__user__first_name', 'student__user__first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parents'] = Parent.objects.all()
        context['students'] = Student.objects.all()
        context['relationship_choices'] = Parent.Relationship.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_parent'] = self.request.GET.get('parent', '')
        context['selected_student'] = self.request.GET.get('student', '')
        context['selected_relationship'] = self.request.GET.get('relationship', '')
        context['selected_is_primary_contact'] = self.request.GET.get('is_primary_contact', '')
        context['selected_receives_notifications'] = self.request.GET.get('receives_notifications', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ParentStudentRelationshipAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Parent-Student Relationships"""
    model = ParentStudentRelationship
    form_class = ParentStudentRelationshipForm
    template_name = 'parents/admin/parent_student_relationship_form.html'
    success_url = reverse_lazy('parents:admin_parent_student_relationship_list')
    success_message = "Parent-student relationship created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Link Parent to Student'
        context['button_text'] = 'Create Relationship'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ParentStudentRelationshipAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Parent-Student Relationships"""
    model = ParentStudentRelationship
    form_class = ParentStudentRelationshipForm
    template_name = 'parents/admin/parent_student_relationship_form.html'
    success_url = reverse_lazy('parents:admin_parent_student_relationship_list')
    success_message = "Parent-student relationship updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Parent-Student Relationship'
        context['button_text'] = 'Update Relationship'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ParentStudentRelationshipAdminDetailView(DetailView):
    """Admin detail view for Parent-Student Relationships"""
    model = ParentStudentRelationship
    template_name = 'parents/admin/parent_student_relationship_detail.html'
    context_object_name = 'relationship'


@method_decorator([login_required, admin_required], name='dispatch')
class ParentStudentRelationshipAdminDeleteView(DeleteView):
    """Admin delete view for Parent-Student Relationships"""
    model = ParentStudentRelationship
    template_name = 'parents/admin/parent_student_relationship_confirm_delete.html'
    success_url = reverse_lazy('parents:admin_parent_student_relationship_list')
    
    def delete(self, request, *args, **kwargs):
        relationship = self.get_object()
        messages.success(self.request, f"Parent-student relationship deleted successfully.")
        return super().delete(request, *args, **kwargs)
