from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Fee Category CRUD
    path('admin/fee-categories/', views.FeeCategoryListView.as_view(), name='fee_category_list'),
    path('admin/fee-categories/create/', views.FeeCategoryCreateView.as_view(), name='fee_category_create'),
    path('admin/fee-categories/<int:pk>/', views.FeeCategoryDetailView.as_view(), name='fee_category_detail'),
    path('admin/fee-categories/<int:pk>/edit/', views.FeeCategoryUpdateView.as_view(), name='fee_category_edit'),
    path('admin/fee-categories/<int:pk>/delete/', views.FeeCategoryDeleteView.as_view(), name='fee_category_delete'),
    
    # Fee Structure CRUD
    path('admin/fee-structures/', views.FeeStructureListView.as_view(), name='fee_structure_list'),
    path('admin/fee-structures/create/', views.FeeStructureCreateView.as_view(), name='fee_structure_create'),
    path('admin/fee-structures/<int:pk>/', views.FeeStructureDetailView.as_view(), name='fee_structure_detail'),
    path('admin/fee-structures/<int:pk>/edit/', views.FeeStructureUpdateView.as_view(), name='fee_structure_edit'),
    path('admin/fee-structures/<int:pk>/delete/', views.FeeStructureDeleteView.as_view(), name='fee_structure_delete'),
    
    # Discount CRUD
    path('admin/discounts/', views.DiscountListView.as_view(), name='discount_list'),
    path('admin/discounts/create/', views.DiscountCreateView.as_view(), name='discount_create'),
    path('admin/discounts/<int:pk>/edit/', views.DiscountUpdateView.as_view(), name='discount_edit'),
    path('admin/discounts/<int:pk>/delete/', views.DiscountDeleteView.as_view(), name='discount_delete'),
    
    # Payment CRUD
    path('admin/payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('admin/payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('admin/payments/<int:pk>/edit/', views.PaymentUpdateView.as_view(), name='payment_edit'),
    path('admin/payments/<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='payment_delete'),
    
    # Payment Receipt CRUD
    path('admin/receipts/', views.PaymentReceiptListView.as_view(), name='payment_receipt_list'),
    path('admin/receipts/<int:pk>/', views.PaymentReceiptDetailView.as_view(), name='payment_receipt_detail'),
    
    # Invoice CRUD (existing)
    path('admin/invoices/', views.fee_categories, name='fee_categories'),
    path('admin/create-invoice/', views.create_invoice, name='create_invoice'),
    path('admin/invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('admin/invoice/<int:invoice_id>/payment/', views.make_payment, name='make_payment'),
    path('admin/export-invoices/', views.export_invoices_csv, name='export_invoices_csv'),
    
    # Parent/Student URLs
    path('parent/dashboard/', views.parent_payment_dashboard, name='parent_dashboard'),
    path('payment/success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('payment/failed/<int:invoice_id>/', views.payment_failed, name='payment_failed'),
]
