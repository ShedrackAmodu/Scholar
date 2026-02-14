from django import forms
from .models import SchoolProfile, AcademicYear, Term, Holiday
from django.core.exceptions import ValidationError


class SchoolProfileForm(forms.ModelForm):
    """Form for school profile configuration"""
    
    class Meta:
        model = SchoolProfile
        exclude = ('created_at', 'updated_at')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slogan': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'favicon': forms.FileInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'half_day_opening': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'half_day_closing': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'current_term': forms.Select(attrs={'class': 'form-control'}),
            'current_academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'next_term_begins': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'primary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'accent_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'youtube': forms.URLInput(attrs={'class': 'form-control'}),
        }


class SchoolHoursForm(forms.ModelForm):
    """Form specifically for editing school hours"""
    
    class Meta:
        model = SchoolProfile
        fields = ('opening_time', 'closing_time', 'half_day_opening', 'half_day_closing')
        widgets = {
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'half_day_opening': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'half_day_closing': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }


class AcademicYearForm(forms.ModelForm):
    """Form for academic year management"""
    
    class Meta:
        model = AcademicYear
        fields = ('name', 'start_date', 'end_date', 'is_current')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise ValidationError("End date must be after start date.")
        
        return cleaned_data


class TermForm(forms.ModelForm):
    """Form for term management"""
    
    class Meta:
        model = Term
        fields = ('academic_year', 'term', 'start_date', 'end_date', 'is_current')
        widgets = {
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        academic_year = cleaned_data.get('academic_year')
        
        if start_date and end_date and start_date >= end_date:
            raise ValidationError("End date must be after start date.")
        
        # Check if dates are within academic year
        if academic_year and start_date and end_date:
            if start_date < academic_year.start_date or end_date > academic_year.end_date:
                raise ValidationError("Term dates must be within the academic year.")
        
        return cleaned_data


class HolidayForm(forms.ModelForm):
    """Form for holiday management"""
    
    class Meta:
        model = Holiday
        fields = ('name', 'start_date', 'end_date', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise ValidationError("End date must be after start date.")
        
        return cleaned_data
