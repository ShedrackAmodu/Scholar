from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Admin URLs
    path('admin/fee-categories/', views.fee_categories, name='fee_categories'),
    path('admin/create-invoice/', views.create_invoice, name='create_invoice'),
    path('admin/invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('admin/invoice/<int:invoice_id>/payment/', views.make_payment, name='make_payment'),
    path('admin/export-invoices/', views.export_invoices_csv, name='export_invoices_csv'),
]
