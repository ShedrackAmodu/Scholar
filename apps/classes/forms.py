from django import forms
from django.core.exceptions import ValidationError
from .models import ClassLevel, Class, Subject, SubjectAllocation
from apps.accounts.models import User
from apps.school.models import AcademicYear, SchoolProfile


class ClassLevelForm(forms.ModelForm):
    """Form for class level management"""
    
    class Meta:
        model = ClassLevel
        fields = ('name', 'level_type', 'order', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'level_type': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ClassForm(forms.ModelForm):
    """Form for class management"""
    
    class Meta:
        model = Class
        fields = ('name', 'class_level', 'class_teacher', 'academic_year', 
                 'capacity', 'room_number', 'status')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'class_level': forms.Select(attrs={'class': 'form-control'}),
            'class_teacher': forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show teachers in the dropdown
        self.fields['class_teacher'].queryset = User.objects.filter(role='TEACHER')
        # Only show active academic years
        self.fields['academic_year'].queryset = AcademicYear.objects.all()


class SubjectForm(forms.ModelForm):
    """Form for subject management"""
    
    class Meta:
        model = Subject
        fields = ('name', 'code', 'class_level', 'is_compulsory', 'description', 'display_order')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'class_level': forms.Select(attrs={'class': 'form-control'}),
            'is_compulsory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if Subject.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A subject with this code already exists.")
        return code.upper()


class SubjectAllocationForm(forms.ModelForm):
    """Form for assigning subjects to teachers"""
    
    class Meta:
        model = SubjectAllocation
        fields = ('teacher', 'subject', 'class_assigned', 'academic_year', 'term')
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'class_assigned': forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(role='TEACHER')
    
    def clean(self):
        cleaned_data = super().clean()
        teacher = cleaned_data.get('teacher')
        subject = cleaned_data.get('subject')
        class_assigned = cleaned_data.get('class_assigned')
        academic_year = cleaned_data.get('academic_year')
        term = cleaned_data.get('term')
        
        # Check if allocation already exists
        if SubjectAllocation.objects.filter(
            teacher=teacher,
            subject=subject,
            class_assigned=class_assigned,
            academic_year=academic_year,
            term=term
        ).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This subject allocation already exists.")
        
        return cleaned_data


class BulkClassAssignmentForm(forms.Form):
    """Form for bulk assigning teachers to classes"""
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(role='TEACHER'),
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
    classes = forms.ModelMultipleChoiceField(
        queryset=Class.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
