from django import forms
from django.core.exceptions import ValidationError
from .models import FeeCategory, FeeStructure, Invoice, InvoiceItem, Payment, Discount
from apps.students.models import Student
from apps.classes.models import Class, ClassLevel
from apps.school.models import AcademicYear, Term, SchoolProfile
import decimal


class FeeCategoryForm(forms.ModelForm):
    """Form for fee categories"""
    
    class Meta:
        model = FeeCategory
        fields = ('name', 'code', 'description', 'frequency', 'is_compulsory')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'is_compulsory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if FeeCategory.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A category with this code already exists.")
        return code.upper()


class FeeStructureForm(forms.ModelForm):
    """Form for fee structures"""
    
    class Meta:
        model = FeeStructure
        fields = ('category', 'name', 'class_level', 'class_specific', 'amount',
                 'academic_year', 'term', 'due_date', 'is_active')
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'class_level': forms.Select(attrs={'class': 'form-control'}),
            'class_specific': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        class_level = cleaned_data.get('class_level')
        class_specific = cleaned_data.get('class_specific')
        
        if class_specific and class_level and class_specific.class_level != class_level:
            raise ValidationError("Selected class must belong to the selected class level.")
        
        return cleaned_data


class BulkInvoiceGenerationForm(forms.Form):
    """Form for generating invoices in bulk"""
    class_assigned = forms.ModelChoiceField(
        queryset=Class.objects.filter(status='ACTIVE'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    academic_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    term = forms.ChoiceField(
        choices=SchoolProfile.TermChoices.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fee_items = forms.ModelMultipleChoiceField(
        queryset=FeeStructure.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        fee_items = cleaned_data.get('fee_items')
        
        if not fee_items:
            raise ValidationError("Please select at least one fee item.")
        
        return cleaned_data


class InvoiceForm(forms.ModelForm):
    """Form for creating/editing invoices"""
    
    class Meta:
        model = Invoice
        fields = ('student', 'due_date', 'academic_year', 'term', 'discount', 'notes')
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class InvoiceItemForm(forms.ModelForm):
    """Form for adding items to invoice"""
    
    class Meta:
        model = InvoiceItem
        fields = ('fee_structure', 'quantity', 'description')
        widgets = {
            'fee_structure': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_price'] = forms.DecimalField(
            max_digits=10,
            decimal_places=2,
            widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            required=False
        )


class PaymentForm(forms.ModelForm):
    """Form for recording payments"""
    
    class Meta:
        model = Payment
        fields = ('invoice', 'amount', 'payment_method', 'notes')
        widgets = {
            'invoice': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        invoice = self.cleaned_data.get('invoice')
        
        if invoice and amount:
            if amount > invoice.balance:
                raise ValidationError(f"Amount cannot exceed the balance of {invoice.balance}.")
        
        return amount


class PaystackPaymentForm(forms.Form):
    """Form for Paystack payment initialization"""
    invoice_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'readonly': True
        })
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01',
            'readonly': True
        })
    )


class DiscountForm(forms.ModelForm):
    """Form for discounts"""
    
    class Meta:
        model = Discount
        fields = ('name', 'code', 'percentage', 'description', 'applicable_to_all',
                 'applicable_classes', 'valid_from', 'valid_to', 'max_uses')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'applicable_to_all': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'applicable_classes': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'valid_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'max_uses': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if Discount.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A discount with this code already exists.")
        return code.upper()
    
    def clean(self):
        cleaned_data = super().clean()
        valid_from = cleaned_data.get('valid_from')
        valid_to = cleaned_data.get('valid_to')
        
        if valid_from and valid_to and valid_from >= valid_to:
            raise ValidationError("Valid to date must be after valid from date.")
        
        return cleaned_data


class PaymentReportForm(forms.Form):
    """Form for payment reports"""
    academic_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    term = forms.ChoiceField(
        choices=[('', 'All Terms')] + list(SchoolProfile.TermChoices.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class_assigned = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        required=False,
        empty_label="All Classes",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    report_type = forms.ChoiceField(
        choices=[
            ('summary', 'Summary Report'),
            ('detailed', 'Detailed Report'),
            ('defaulters', 'Defaulters List'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
