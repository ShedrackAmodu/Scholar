from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.decorators import method_decorator

from .models import FeeCategory, FeeStructure, Invoice, InvoiceItem, Payment, PaymentReceipt, Discount
from .forms import FeeCategoryForm, FeeStructureForm
from apps.accounts.decorators import admin_required
from apps.classes.models import Class, ClassLevel
from apps.school.models import AcademicYear


# ============ FeeCategory Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class FeeCategoryAdminListView(ListView):
    """Admin list view for Fee Categories"""
    model = FeeCategory
    template_name = 'payments/admin/fee_category_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FeeCategory.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by frequency
        frequency = self.request.GET.get('frequency')
        if frequency:
            queryset = queryset.filter(frequency=frequency)
        
        # Filter by compulsory status
        is_compulsory = self.request.GET.get('is_compulsory')
        if is_compulsory:
            queryset = queryset.filter(is_compulsory=is_compulsory == 'True')
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['frequencies'] = FeeCategory.Frequency.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_frequency'] = self.request.GET.get('frequency', '')
        context['selected_is_compulsory'] = self.request.GET.get('is_compulsory', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class FeeCategoryAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Fee Categories"""
    model = FeeCategory
    form_class = FeeCategoryForm
    template_name = 'payments/admin/fee_category_form.html'
    success_url = reverse_lazy('payments:admin_fee_category_list')
    success_message = "Fee category '%(name)s' created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Fee Category'
        context['button_text'] = 'Create Category'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class FeeCategoryAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Fee Categories"""
    model = FeeCategory
    form_class = FeeCategoryForm
    template_name = 'payments/admin/fee_category_form.html'
    success_url = reverse_lazy('payments:admin_fee_category_list')
    success_message = "Fee category '%(name)s' updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Fee Category: {self.object.name}'
        context['button_text'] = 'Update Category'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class FeeCategoryAdminDetailView(DetailView):
    """Admin detail view for Fee Categories"""
    model = FeeCategory
    template_name = 'payments/admin/fee_category_detail.html'
    context_object_name = 'category'


@method_decorator([login_required, admin_required], name='dispatch')
class FeeCategoryAdminDeleteView(DeleteView):
    """Admin delete view for Fee Categories"""
    model = FeeCategory
    template_name = 'payments/admin/fee_category_confirm_delete.html'
    success_url = reverse_lazy('payments:admin_fee_category_list')
    
    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        messages.success(self.request, f"Fee category '{category.name}' deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ FeeStructure Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class FeeStructureAdminListView(ListView):
    """Admin list view for Fee Structures"""
    model = FeeStructure
    template_name = 'payments/admin/fee_structure_list.html'
    context_object_name = 'structures'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FeeStructure.objects.select_related(
            'category', 'class_level', 'class_specific', 'academic_year'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Filter by academic year
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        # Filter by class level
        class_level = self.request.GET.get('class_level')
        if class_level:
            queryset = queryset.filter(class_level_id=class_level)
        
        # Filter by term
        term = self.request.GET.get('term')
        if term:
            queryset = queryset.filter(term=term)
        
        # Filter by active status
        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=is_active == 'True')
        
        return queryset.order_by('-academic_year', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academic_years'] = AcademicYear.objects.all()
        context['class_levels'] = ClassLevel.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_academic_year'] = self.request.GET.get('academic_year', '')
        context['selected_class_level'] = self.request.GET.get('class_level', '')
        context['selected_term'] = self.request.GET.get('term', '')
        context['selected_is_active'] = self.request.GET.get('is_active', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class FeeStructureAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Fee Structures"""
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = 'payments/admin/fee_structure_form.html'
    success_url = reverse_lazy('payments:admin_fee_structure_list')
    success_message = "Fee structure '%(name)s' created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Fee Structure'
        context['button_text'] = 'Create Structure'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class FeeStructureAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Fee Structures"""
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = 'payments/admin/fee_structure_form.html'
    success_url = reverse_lazy('payments:admin_fee_structure_list')
    success_message = "Fee structure '%(name)s' updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Fee Structure: {self.object.name}'
        context['button_text'] = 'Update Structure'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class FeeStructureAdminDetailView(DetailView):
    """Admin detail view for Fee Structures"""
    model = FeeStructure
    template_name = 'payments/admin/fee_structure_detail.html'
    context_object_name = 'structure'


@method_decorator([login_required, admin_required], name='dispatch')
class FeeStructureAdminDeleteView(DeleteView):
    """Admin delete view for Fee Structures"""
    model = FeeStructure
    template_name = 'payments/admin/fee_structure_confirm_delete.html'
    success_url = reverse_lazy('payments:admin_fee_structure_list')
    
    def delete(self, request, *args, **kwargs):
        structure = self.get_object()
        messages.success(self.request, f"Fee structure '{structure.name}' deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ Invoice Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class InvoiceAdminListView(ListView):
    """Admin list view for Invoices"""
    model = Invoice
    template_name = 'payments/admin/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Invoice.objects.select_related(
            'student', 'student__user', 'academic_year', 'created_by'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search_query) |
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query) |
                Q(student__admission_number__icontains=search_query)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by academic year
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        # Filter by term
        term = self.request.GET.get('term')
        if term:
            queryset = queryset.filter(term=term)
        
        return queryset.order_by('-issue_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Invoice.Status.choices
        context['academic_years'] = AcademicYear.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_academic_year'] = self.request.GET.get('academic_year', '')
        context['selected_term'] = self.request.GET.get('term', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class InvoiceAdminDetailView(DetailView):
    """Admin detail view for Invoices"""
    model = Invoice
    template_name = 'payments/admin/invoice_detail.html'
    context_object_name = 'invoice'
    
    def get_queryset(self):
        return Invoice.objects.select_related(
            'student', 'student__user', 'academic_year', 'created_by'
        )


@method_decorator([login_required, admin_required], name='dispatch')
class InvoiceAdminDeleteView(DeleteView):
    """Admin delete view for Invoices"""
    model = Invoice
    template_name = 'payments/admin/invoice_confirm_delete.html'
    success_url = reverse_lazy('payments:admin_invoice_list')
    
    def delete(self, request, *args, **kwargs):
        invoice = self.get_object()
        messages.success(self.request, f"Invoice '{invoice.invoice_number}' deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ============ Payment Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class PaymentAdminListView(ListView):
    """Admin list view for Payments"""
    model = Payment
    template_name = 'payments/admin/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Payment.objects.select_related(
            'invoice', 'invoice__student', 'invoice__student__user', 'payer'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(transaction_id__icontains=search_query) |
                Q(reference__icontains=search_query) |
                Q(invoice__invoice_number__icontains=search_query) |
                Q(payer__first_name__icontains=search_query) |
                Q(payer__last_name__icontains=search_query)
            )
        
        # Filter by payment status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by payment method
        payment_method = self.request.GET.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        return queryset.order_by('-payment_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Payment.PaymentStatus.choices
        context['payment_methods'] = Payment.PaymentMethod.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_payment_method'] = self.request.GET.get('payment_method', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class PaymentAdminDetailView(DetailView):
    """Admin detail view for Payments"""
    model = Payment
    template_name = 'payments/admin/payment_detail.html'
    context_object_name = 'payment'
    
    def get_queryset(self):
        return Payment.objects.select_related(
            'invoice', 'invoice__student', 'invoice__student__user', 'payer'
        )


# ============ Discount Admin CRUD Views ============

@method_decorator([login_required, admin_required], name='dispatch')
class DiscountAdminListView(ListView):
    """Admin list view for Discounts"""
    model = Discount
    template_name = 'payments/admin/discount_list.html'
    context_object_name = 'discounts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Discount.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by applicability
        applicable_to_all = self.request.GET.get('applicable_to_all')
        if applicable_to_all:
            queryset = queryset.filter(applicable_to_all=applicable_to_all == 'True')
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_applicable_to_all'] = self.request.GET.get('applicable_to_all', '')
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class DiscountAdminCreateView(SuccessMessageMixin, CreateView):
    """Admin create view for Discounts"""
    model = Discount
    fields = ['name', 'code', 'percentage', 'description', 'applicable_to_all', 
              'applicable_classes', 'valid_from', 'valid_to', 'max_uses']
    template_name = 'payments/admin/discount_form.html'
    success_url = reverse_lazy('payments:admin_discount_list')
    success_message = "Discount '%(name)s' created successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Discount'
        context['button_text'] = 'Create Discount'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class DiscountAdminUpdateView(SuccessMessageMixin, UpdateView):
    """Admin update view for Discounts"""
    model = Discount
    fields = ['name', 'code', 'percentage', 'description', 'applicable_to_all', 
              'applicable_classes', 'valid_from', 'valid_to', 'max_uses']
    template_name = 'payments/admin/discount_form.html'
    success_url = reverse_lazy('payments:admin_discount_list')
    success_message = "Discount '%(name)s' updated successfully."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Discount: {self.object.name}'
        context['button_text'] = 'Update Discount'
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class DiscountAdminDetailView(DetailView):
    """Admin detail view for Discounts"""
    model = Discount
    template_name = 'payments/admin/discount_detail.html'
    context_object_name = 'discount'


@method_decorator([login_required, admin_required], name='dispatch')
class DiscountAdminDeleteView(DeleteView):
    """Admin delete view for Discounts"""
    model = Discount
    template_name = 'payments/admin/discount_confirm_delete.html'
    success_url = reverse_lazy('payments:admin_discount_list')
    
    def delete(self, request, *args, **kwargs):
        discount = self.get_object()
        messages.success(self.request, f"Discount '{discount.name}' deleted successfully.")
        return super().delete(request, *args, **kwargs)
