from django import forms
from django.core.exceptions import ValidationError
from .models import Teacher, TeacherQualification, TeacherSubjectExpertise, TeacherLeave
from apps.accounts.models import User
from apps.classes.models import Subject
import re


class TeacherForm(forms.ModelForm):
    """Form for teacher registration and management"""
    
    class Meta:
        model = Teacher
        exclude = ('user', 'staff_id', 'created_at', 'updated_at')
        widgets = {
            'qualification': forms.Select(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'employment_type': forms.Select(attrs={'class': 'form-control'}),
            'date_employed': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'cv': forms.FileInput(attrs={'class': 'form-control'}),
            'certificates': forms.FileInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control'}),
            'pension_number': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'is_class_teacher': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^\+?1?\d{9,15}$', phone):
            raise ValidationError("Enter a valid phone number.")
        return phone


class TeacherQualificationForm(forms.ModelForm):
    """Form for teacher qualifications"""
    
    class Meta:
        model = TeacherQualification
        fields = ('degree', 'institution', 'year_obtained', 'grade')
        widgets = {
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'year_obtained': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2100}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TeacherSubjectExpertiseForm(forms.ModelForm):
    """Form for teacher subject expertise"""
    
    class Meta:
        model = TeacherSubjectExpertise
        fields = ('subject', 'is_primary')
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TeacherLeaveForm(forms.ModelForm):
    """Form for teacher leave requests"""
    
    class Meta:
        model = TeacherLeave
        fields = ('leave_type', 'start_date', 'end_date', 'reason')
        widgets = {
            'leave_type': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError("End date must be after start date.")
        
        return cleaned_data


class TeacherSearchForm(forms.Form):
    """Form for searching teachers"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, staff ID...'
        })
    )
    employment_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Teacher.EmploymentType.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = forms.ChoiceField(
        choices=[('', 'All'), ('True', 'Active'), ('False', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
