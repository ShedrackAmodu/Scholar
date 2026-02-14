from django import forms
from django.core.exceptions import ValidationError
from .models import Assessment, SubjectAssessment, Score, SubjectScore, ReportCard, ClassPerformance
from apps.students.models import Student
from apps.classes.models import Subject, Class
from apps.school.models import AcademicYear, Term, SchoolProfile
from decimal import Decimal


class AssessmentForm(forms.ModelForm):
    """Form for creating assessments (tests, exams, etc.)"""
    
    class Meta:
        model = Assessment
        fields = ('name', 'assessment_type', 'code', 'max_score', 'weight_percentage', 
                 'class_level', 'is_active', 'grade_boundaries')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'assessment_type': forms.Select(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'weight_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'class_level': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'grade_boundaries': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '{"A": 70, "B": 60, "C": 50}'}),
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if Assessment.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
            raise ValidationError("An assessment with this code already exists.")
        return code.upper()
    
    def clean(self):
        cleaned_data = super().clean()
        max_score = cleaned_data.get('max_score')
        weight = cleaned_data.get('weight_percentage')
        
        if max_score and weight and weight > 100:
            raise ValidationError("Weight percentage cannot exceed 100%.")
        
        return cleaned_data


class SubjectAssessmentForm(forms.ModelForm):
    """Form for linking assessments to subjects"""
    
    class Meta:
        model = SubjectAssessment
        fields = ('subject', 'assessment', 'term', 'academic_year', 'max_score')
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'assessment': forms.Select(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        assessment = cleaned_data.get('assessment')
        term = cleaned_data.get('term')
        academic_year = cleaned_data.get('academic_year')
        
        # Check if already exists
        if SubjectAssessment.objects.filter(
            subject=subject,
            assessment=assessment,
            term=term,
            academic_year=academic_year
        ).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This assessment is already linked to this subject for this term.")
        
        return cleaned_data


class BulkScoreEntryForm(forms.Form):
    """Form for bulk score entry"""
    subject_assessment = forms.ModelChoiceField(
        queryset=SubjectAssessment.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        class_assigned = kwargs.pop('class_assigned', None)
        super().__init__(*args, **kwargs)
        
        if class_assigned:
            self.fields['students'] = forms.ModelMultipleChoiceField(
                queryset=Student.objects.filter(current_class=class_assigned),
                widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
            )
            self.fields['scores'] = forms.CharField(
                widget=forms.Textarea(attrs={
                    'class': 'form-control', 
                    'rows': 5,
                    'placeholder': 'Enter scores separated by commas (e.g., 85, 90, 75, 88)'
                })
            )
            self.fields['remarks'] = forms.CharField(
                required=False,
                widget=forms.Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'General remarks for all students'
                })
            )


class IndividualScoreForm(forms.ModelForm):
    """Form for individual score entry"""
    
    class Meta:
        model = Score
        fields = ('student', 'subject_assessment', 'score', 'remarks')
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'subject_assessment': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def clean_score(self):
        score = self.cleaned_data.get('score')
        subject_assessment = self.cleaned_data.get('subject_assessment')
        
        if subject_assessment and score:
            if score > subject_assessment.max_score:
                raise ValidationError(f"Score cannot exceed {subject_assessment.max_score}.")
            if score < 0:
                raise ValidationError("Score cannot be negative.")
        
        return score


class ScoreApprovalForm(forms.Form):
    """Form for approving scores"""
    approve_all = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


class ReportCardGenerationForm(forms.Form):
    """Form for generating report cards"""
    class_assigned = forms.ModelChoiceField(
        queryset=Class.objects.filter(status='ACTIVE'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    term = forms.ChoiceField(
        choices=SchoolProfile.TermChoices.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    academic_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Options
    generate_for_all = forms.BooleanField(
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['students'] = forms.ModelMultipleChoiceField(
            queryset=Student.objects.none(),
            required=False,
            widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
        )
    
    def clean(self):
        cleaned_data = super().clean()
        class_assigned = cleaned_data.get('class_assigned')
        generate_for_all = cleaned_data.get('generate_for_all', True)
        
        if class_assigned and not generate_for_all:
            # Filter students for the selected class
            self.fields['students'].queryset = Student.objects.filter(
                current_class=class_assigned,
                enrollment_status='ACTIVE'
            )
        
        return cleaned_data


class ReportCardApprovalForm(forms.Form):
    """Form for approving report cards"""
    class_teacher_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    principal_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    approve = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class ClassPerformanceForm(forms.ModelForm):
    """Form for class performance analysis"""
    
    class Meta:
        model = ClassPerformance
        fields = ('class_assigned', 'term', 'academic_year')
        widgets = {
            'class_assigned': forms.Select(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
        }
