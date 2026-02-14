from django import forms
from django.core.exceptions import ValidationError
from .models import Application, ApplicationComment, EntranceExam
from apps.classes.models import ClassLevel
import re


class ApplicationForm(forms.ModelForm):
    """Public form for online applications"""
    
    class Meta:
        model = Application
        fields = (
            'first_name', 'last_name', 'middle_name', 'email', 'phone',
            'date_of_birth', 'gender', 'address', 'city', 'state', 'country',
            'applying_for_class', 'previous_school', 'previous_class',
            'father_name', 'father_phone', 'father_email',
            'mother_name', 'mother_phone', 'mother_email',
            'guardian_name', 'guardian_phone', 'guardian_email', 'guardian_relationship'
        )
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter middle name (optional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter home address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter city'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter state'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter country'
            }),
            'applying_for_class': forms.Select(attrs={'class': 'form-control'}),
            'previous_school': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Previous school (optional)'
            }),
            'previous_class': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Previous class (optional)'
            }),
            'father_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Father's full name"
            }),
            'father_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Father's phone"
            }),
            'father_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': "Father's email"
            }),
            'mother_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Mother's full name"
            }),
            'mother_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Mother's phone"
            }),
            'mother_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': "Mother's email"
            }),
            'guardian_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Guardian's full name (if applicable)"
            }),
            'guardian_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Guardian's phone"
            }),
            'guardian_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': "Guardian's email"
            }),
            'guardian_relationship': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Relationship to guardian"
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Application.objects.filter(email=email).exists():
            raise ValidationError("An application with this email already exists.")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^\+?1?\d{9,15}$', phone):
            raise ValidationError("Enter a valid phone number.")
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        # Ensure at least one parent/guardian contact is provided
        father_phone = cleaned_data.get('father_phone')
        mother_phone = cleaned_data.get('mother_phone')
        guardian_phone = cleaned_data.get('guardian_phone')
        
        if not (father_phone or mother_phone or guardian_phone):
            raise ValidationError("Please provide at least one parent/guardian phone number.")
        
        return cleaned_data


class ApplicationReviewForm(forms.ModelForm):
    """Form for admin to review applications"""
    
    class Meta:
        model = Application
        fields = ('status', 'review_notes', 'admission_number', 'enrollment_date')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'review_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'admission_number': forms.TextInput(attrs={'class': 'form-control'}),
            'enrollment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        admission_number = cleaned_data.get('admission_number')
        enrollment_date = cleaned_data.get('enrollment_date')
        
        if status == 'ACC' and not (admission_number and enrollment_date):
            raise ValidationError("Admission number and enrollment date are required for accepted applications.")
        
        return cleaned_data


class ApplicationCommentForm(forms.ModelForm):
    """Form for adding comments to applications"""
    
    class Meta:
        model = ApplicationComment
        fields = ('comment',)
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add your comment...'
            }),
        }


class EntranceExamForm(forms.ModelForm):
    """Form for entrance exam scores"""
    
    class Meta:
        model = EntranceExam
        fields = ('exam_date', 'english_score', 'mathematics_score', 
                 'general_knowledge', 'remarks')
        widgets = {
            'exam_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'english_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'mathematics_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'general_knowledge': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ApplicationSearchForm(forms.Form):
    """Form for searching applications"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, application number...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Application.ApplicationStatus.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    applying_for_class = forms.ModelChoiceField(
        queryset=ClassLevel.objects.all(),
        required=False,
        empty_label="All Classes",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class BulkApplicationStatusForm(forms.Form):
    """Form for bulk updating application status"""
    status = forms.ChoiceField(
        choices=Application.ApplicationStatus.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    applications = forms.ModelMultipleChoiceField(
        queryset=Application.objects.filter(status='PEND'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    review_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
