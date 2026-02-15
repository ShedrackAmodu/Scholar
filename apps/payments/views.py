from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from .models import FeeCategory, FeeStructure, Invoice, InvoiceItem, Payment, Discount, PaymentReceipt
from .forms import (
    FeeCategoryForm, FeeStructureForm, InvoiceForm,
    InvoiceItemForm, PaymentForm, DiscountForm
)
from apps.accounts.decorators import admin_required, accountant_required, principal_required
from apps.students.models import Student
from apps.school.models import SchoolProfile
import csv

# ============ Fee Category CRUD ============
@method_decorator([login_required, admin_required], name='dispatch')
class FeeCategoryListView(ListView):
    """List all fee categories"""
    model = FeeCategory
    template_name = 'payments/admin/fee_category_list.html'
    context_object_name = 'categories'
    paginate_by = 50

@method_decorator([login_required, admin_required], name='dispatch')
class FeeCategoryCreateView(SuccessMessageMixin, CreateView):
    """Create new fee category"""
    model = FeeCategory
    form_class = FeeCategoryForm
    template_name = 'payments/admin/fee_category_form.html'
    success_url = reverse_lazy('payments:fee_category_list')
    success_message = "Fee category %(name)s created successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class FeeCategoryUpdateView(SuccessMessageMixin, UpdateView):
    """Update fee category"""
    model = FeeCategory
    form_class = FeeCategoryForm
    template_name = 'payments/admin/fee_category_form.html'
    success_url = reverse_lazy('payments:fee_category_list')
    success_message = "Fee category %(name)s updated successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class FeeCategoryDeleteView(DeleteView):
    """Delete fee category"""
    model = FeeCategory
    template_name = 'payments/admin/fee_category_confirm_delete.html'
    success_url = reverse_lazy('payments:fee_category_list')

@method_decorator([login_required, admin_required], name='dispatch')
class FeeCategoryDetailView(DetailView):
    """View fee category details"""
    model = FeeCategory
    template_name = 'payments/admin/fee_category_detail.html'
    context_object_name = 'category'

# ============ Fee Structure CRUD ============
@method_decorator([login_required, principal_required], name='dispatch')
class FeeStructureListView(ListView):
    """List all fee structures"""
    model = FeeStructure
    template_name = 'payments/admin/fee_structure_list.html'
    context_object_name = 'structures'
    paginate_by = 50

@method_decorator([login_required, principal_required], name='dispatch')
class FeeStructureCreateView(SuccessMessageMixin, CreateView):
    """Create new fee structure"""
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = 'payments/admin/fee_structure_form.html'
    success_url = reverse_lazy('payments:fee_structure_list')
    success_message = "Fee structure created successfully."

@method_decorator([login_required, principal_required], name='dispatch')
class FeeStructureUpdateView(SuccessMessageMixin, UpdateView):
    """Update fee structure"""
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = 'payments/admin/fee_structure_form.html'
    success_url = reverse_lazy('payments:fee_structure_list')
    success_message = "Fee structure updated successfully."

@method_decorator([login_required, principal_required], name='dispatch')
class FeeStructureDeleteView(DeleteView):
    """Delete fee structure"""
    model = FeeStructure
    template_name = 'payments/admin/fee_structure_confirm_delete.html'
    success_url = reverse_lazy('payments:fee_structure_list')

@method_decorator([login_required, principal_required], name='dispatch')
class FeeStructureDetailView(DetailView):
    """View fee structure details"""
    model = FeeStructure
    template_name = 'payments/admin/fee_structure_detail.html'
    context_object_name = 'structure'

# ============ Discount CRUD ============
@method_decorator([login_required, admin_required], name='dispatch')
class DiscountListView(ListView):
    """List all discounts"""
    model = Discount
    template_name = 'payments/admin/discount_list.html'
    context_object_name = 'discounts'
    paginate_by = 50

@method_decorator([login_required, admin_required], name='dispatch')
class DiscountCreateView(SuccessMessageMixin, CreateView):
    """Create new discount"""
    model = Discount
    form_class = DiscountForm
    template_name = 'payments/admin/discount_form.html'
    success_url = reverse_lazy('payments:discount_list')
    success_message = "Discount created successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class DiscountUpdateView(SuccessMessageMixin, UpdateView):
    """Update discount"""
    model = Discount
    form_class = DiscountForm
    template_name = 'payments/admin/discount_form.html'
    success_url = reverse_lazy('payments:discount_list')
    success_message = "Discount updated successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class DiscountDeleteView(DeleteView):
    """Delete discount"""
    model = Discount
    template_name = 'payments/admin/discount_confirm_delete.html'
    success_url = reverse_lazy('payments:discount_list')

# ============ Payment CRUD ============
@method_decorator([login_required, admin_required], name='dispatch')
class PaymentListView(ListView):
    """List all payments"""
    model = Payment
    template_name = 'payments/admin/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 50
    ordering = ['-payment_date']

@method_decorator([login_required, admin_required], name='dispatch')
class PaymentDetailView(DetailView):
    """View payment details"""
    model = Payment
    template_name = 'payments/admin/payment_detail.html'
    context_object_name = 'payment'

@method_decorator([login_required, admin_required], name='dispatch')
class PaymentUpdateView(SuccessMessageMixin, UpdateView):
    """Update payment"""
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/admin/payment_form.html'
    success_url = reverse_lazy('payments:payment_list')
    success_message = "Payment updated successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class PaymentDeleteView(DeleteView):
    """Delete payment"""
    model = Payment
    template_name = 'payments/admin/payment_confirm_delete.html'
    success_url = reverse_lazy('payments:payment_list')

# ============ Payment Receipt CRUD ============
@method_decorator([login_required, admin_required], name='dispatch')
class PaymentReceiptListView(ListView):
    """List all payment receipts"""
    model = PaymentReceipt
    template_name = 'payments/admin/payment_receipt_list.html'
    context_object_name = 'receipts'
    paginate_by = 50
    ordering = ['-created_at']

@method_decorator([login_required, admin_required], name='dispatch')
class PaymentReceiptDetailView(DetailView):
    """View payment receipt details"""
    model = PaymentReceipt
    template_name = 'payments/admin/payment_receipt_detail.html'
    context_object_name = 'receipt'

@login_required
@admin_required
def fee_categories(request):
    categories = FeeCategory.objects.all()
    return render(request, 'payments/fee_categories.html', {'categories': categories})

@login_required
@admin_required
def create_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            form.save_m2m()
            messages.success(request, 'Invoice created successfully.')
            return redirect('payments:invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm()
    return render(request, 'payments/create_invoice.html', {'form': form})

@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = InvoiceItem.objects.filter(invoice=invoice)
    payments = Payment.objects.filter(invoice=invoice)
    context = {'invoice': invoice, 'items': items, 'payments': payments}
    return render(request, 'payments/invoice_detail.html', context)

@login_required
def make_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.created_by = request.user
            payment.save()
            messages.success(request, 'Payment recorded successfully.')
            return redirect('payments:invoice_detail', invoice_id=invoice.id)
    else:
        form = PaymentForm()
    return render(request, 'payments/make_payment.html', {'form': form, 'invoice': invoice})

@login_required
@accountant_required
def export_invoices_csv(request):
    invoices = Invoice.objects.all().select_related('student')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=invoices.csv'
    writer = csv.writer(response)
    writer.writerow(['Invoice #', 'Student', 'Total', 'Paid', 'Balance', 'Status', 'Created At'])
    for inv in invoices:
        writer.writerow([inv.reference, inv.student.user.get_full_name(), inv.total_amount, inv.amount_paid, inv.balance, inv.status, inv.created_at.isoformat()])
    return response

@login_required
def payment_success(request, payment_id):
    """Display payment success page"""
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'payments/payment_success.html', {'payment': payment})

@login_required
def payment_failed(request, invoice_id):
    """Display payment failed page"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    error_code = request.GET.get('error_code', 'PAY-001')
    error_message = request.GET.get('error_message', 'Your payment could not be processed due to an error with your bank.')
    return render(request, 'payments/payment_failed.html', {
        'invoice': invoice,
        'error_code': error_code,
        'error_message': error_message
    })

@login_required
def parent_payment_dashboard(request):
    """Parent payment dashboard"""
    # Get children for this parent
    children = Student.objects.filter(parents__user=request.user).distinct()
    
    # Get selected child
    selected_child_id = request.GET.get('child')
    selected_child = None
    if selected_child_id:
        try:
            selected_child = children.get(id=selected_child_id)
        except Student.DoesNotExist:
            selected_child = None
    
    # If no specific child selected, use first child
    if not selected_child and children.exists():
        selected_child = children.first()
    
    # Get invoices for selected child
    child_invoices = Invoice.objects.filter(student=selected_child).order_by('-created_at') if selected_child else Invoice.objects.none()
    
    # Calculate statistics
    paid_invoices = child_invoices.filter(status='paid').count()
    pending_invoices = child_invoices.filter(status='pending').count()
    
    # Get recent payments
    recent_payments = Payment.objects.filter(
        invoice__student=selected_child
    ).order_by('-payment_date')[:5] if selected_child else []
    
    # Calculate totals
    total_invoices = child_invoices.count()
    total_paid = sum(payment.amount for payment in recent_payments)
    total_due = sum(invoice.balance for invoice in child_invoices if invoice.balance > 0)
    
    # Calculate due percentage for progress bar
    due_percentage = 0
    if total_due > 0:
        total_amount = sum(invoice.total_amount for invoice in child_invoices)
        due_percentage = (total_due / total_amount) * 100 if total_amount > 0 else 0
    
    context = {
        'children': children,
        'selected_child': selected_child,
        'child_invoices': child_invoices,
        'paid_invoices': paid_invoices,
        'pending_invoices': pending_invoices,
        'recent_payments': recent_payments,
        'total_invoices': total_invoices,
        'total_paid': total_paid,
        'total_due': total_due,
        'due_percentage': due_percentage,
        'children_count': children.count(),
    }
    
    return render(request, 'payments/parent_payment_dashboard.html', context)
