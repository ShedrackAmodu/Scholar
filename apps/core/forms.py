from django import forms
from apps.school.models import SchoolProfile


class SchoolProfileForm(forms.ModelForm):
    """Form for editing school profile settings"""
    
    class Meta:
        model = SchoolProfile
        fields = [
            'name', 'slogan', 'logo', 'favicon',
            'address', 'phone', 'email', 'website',
            'opening_time', 'closing_time',
            'half_day_opening', 'half_day_closing',
            'current_term', 'current_academic_year',
            'next_term_begins',
            'primary_color', 'secondary_color', 'accent_color',
            'facebook', 'twitter', 'instagram', 'youtube'
        ]
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


class SchoolHoursForm(forms.Form):
    """Quick form for updating school hours only"""
    
    opening_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        label='Opening Time'
    )
    closing_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        label='Closing Time'
    )
    half_day_opening = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        label='Half Day Opening Time'
    )
    half_day_closing = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        label='Half Day Closing Time'
    )
