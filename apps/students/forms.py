from django import forms
from django.core.exceptions import ValidationError
from .models import Student, StudentDocument, StudentHistory
from apps.accounts.models import User
from apps.classes.models import Class
from apps.school.models import AcademicYear
import re


class StudentForm(forms.ModelForm):
    """Form for student registration and management"""
    
    class Meta:
        model = Student
        exclude = ('user', 'admission_number', 'created_at', 'updated_at')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
            'religion': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'guardian_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'doctor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'doctor_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'current_class': forms.Select(attrs={'class': 'form-control'}),
            'enrollment_status': forms.Select(attrs={'class': 'form-control'}),
            'previous_school': forms.TextInput(attrs={'class': 'form-control'}),
            'previous_class': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^\+?1?\d{9,15}$', phone):
            raise ValidationError("Enter a valid phone number.")
        return phone
    
    def clean_guardian_phone(self):
        phone = self.cleaned_data.get('guardian_phone')
        if phone and not re.match(r'^\+?1?\d{9,15}$', phone):
            raise ValidationError("Enter a valid guardian phone number.")
        return phone


class StudentEnrollmentForm(forms.Form):
    """Form for enrolling multiple students"""
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.filter(current_class__isnull=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False
    )
    class_assigned = forms.ModelChoiceField(
        queryset=Class.objects.filter(status='ACTIVE'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    academic_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    enrollment_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        students = cleaned_data.get('students')
        class_assigned = cleaned_data.get('class_assigned')
        
        if students and class_assigned:
            # Check if class has capacity
            if students.count() > class_assigned.available_slots:
                raise ValidationError(f"Class only has {class_assigned.available_slots} slots available.")
        
        return cleaned_data


class StudentDocumentForm(forms.ModelForm):
    """Form for student documents"""
    
    class Meta:
        model = StudentDocument
        fields = ('name', 'file')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class StudentSearchForm(forms.Form):
    """Form for searching students"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, admission number...'
        })
    )
    class_filter = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        required=False,
        empty_label="All Classes",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Student.Status.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class BulkStudentUploadForm(forms.Form):
    """Form for bulk uploading students via CSV"""
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )
    class_assigned = forms.ModelChoiceField(
        queryset=Class.objects.filter(status='ACTIVE'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')
        if not file.name.endswith('.csv'):
            raise ValidationError("Please upload a CSV file.")
        return file
