from django import forms
from django.core.exceptions import ValidationError
from .models import Parent, ParentStudentRelationship
from apps.students.models import Student
from apps.accounts.models import User
import re


class ParentForm(forms.ModelForm):
    """Form for parent registration and management"""
    
    class Meta:
        model = Parent
        exclude = ('user', 'created_at', 'updated_at')
        widgets = {
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'employer': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'receive_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receive_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^\+?1?\d{9,15}$', phone):
            raise ValidationError("Enter a valid phone number.")
        return phone


class ParentStudentRelationshipForm(forms.ModelForm):
    """Form for linking parents to students"""
    
    class Meta:
        model = ParentStudentRelationship
        fields = ('parent', 'student', 'relationship', 'is_primary_contact', 
                 'can_pickup', 'receives_notifications')
        widgets = {
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'relationship': forms.Select(attrs={'class': 'form-control'}),
            'is_primary_contact': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_pickup': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receives_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        parent = cleaned_data.get('parent')
        student = cleaned_data.get('student')
        
        if parent and student:
            # Check if relationship already exists
            if ParentStudentRelationship.objects.filter(
                parent=parent, 
                student=student
            ).exclude(pk=self.instance.pk).exists():
                raise ValidationError("This parent-student relationship already exists.")
        
        return cleaned_data


class LinkParentToStudentForm(forms.Form):
    """Form for linking an existing parent to a student"""
    parent = forms.ModelChoiceField(
        queryset=Parent.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    relationship = forms.ChoiceField(
        choices=Parent.Relationship.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_primary_contact = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class BulkParentLinkForm(forms.Form):
    """Form for bulk linking parents to students"""
    parent = forms.ModelChoiceField(
        queryset=Parent.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    relationship = forms.ChoiceField(
        choices=Parent.Relationship.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
