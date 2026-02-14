from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import FeeCategory, FeeStructure, Invoice, InvoiceItem, Payment, Discount
from .forms import (
    FeeCategoryForm, FeeStructureForm, InvoiceForm,
    InvoiceItemForm, PaymentForm, DiscountForm
)
from apps.accounts.decorators import admin_required, accountant_required
from apps.students.models import Student
from apps.school.models import SchoolProfile
import csv

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
