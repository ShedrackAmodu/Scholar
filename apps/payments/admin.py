from django.contrib import admin
from .models import (
    FeeCategory,
    FeeStructure,
    Invoice,
    InvoiceItem,
    Payment,
    PaymentReceipt,
    Discount,
)


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'frequency', 'is_compulsory')


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'amount',
        'academic_year',
        'term',
        'is_active')
    search_fields = ('name', 'category__name')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number',
        'student',
        'total_amount',
        'amount_paid',
        'balance',
        'status',
        'issue_date')
    list_filter = ('status', 'academic_year')
    search_fields = ('invoice_number', 'student__admission_number')


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = (
        'invoice',
        'fee_structure',
        'quantity',
        'unit_price',
        'total_price')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'invoice',
        'payer',
        'amount',
        'status',
        'payment_date')
    list_filter = ('status', 'payment_method')


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ('payment', 'receipt_number', 'generated_at')


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'percentage', 'valid_from', 'valid_to')
    search_fields = ('name', 'code')
