from django import forms
from django.core.exceptions import ValidationError
from .models import AttendanceSession, Attendance, AttendanceSummary
from apps.students.models import Student
from apps.classes.models import Class
from apps.school.models import AcademicYear, Term, SchoolProfile
from django.utils import timezone


class AttendanceSessionForm(forms.ModelForm):
    """Form for creating attendance sessions"""
    
    class Meta:
        model = AttendanceSession
        fields = ('class_assigned', 'date', 'term', 'academic_year')
        widgets = {
            'class_assigned': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        class_assigned = cleaned_data.get('class_assigned')
        date = cleaned_data.get('date')
        term = cleaned_data.get('term')
        academic_year = cleaned_data.get('academic_year')
        
        # Check if session already exists for this class and date
        if AttendanceSession.objects.filter(
            class_assigned=class_assigned,
            date=date,
            term=term,
            academic_year=academic_year
        ).exists():
            raise ValidationError("An attendance session already exists for this class on this date.")
        
        return cleaned_data


class BulkAttendanceForm(forms.Form):
    """Form for bulk attendance marking"""
    
    def __init__(self, *args, **kwargs):
        students = kwargs.pop('students', [])
        super().__init__(*args, **kwargs)
        
        for student in students:
            self.fields[f'student_{student.id}'] = forms.ChoiceField(
                choices=Attendance.Status.choices,
                initial='P',
                widget=forms.Select(attrs={'class': 'form-control form-control-sm'})
            )
            self.fields[f'note_{student.id}'] = forms.CharField(
                required=False,
                widget=forms.TextInput(attrs={
                    'class': 'form-control form-control-sm',
                    'placeholder': 'Note (optional)'
                })
            )
    
    date = forms.DateField(
        initial=timezone.now,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class IndividualAttendanceForm(forms.ModelForm):
    """Form for individual attendance marking"""
    
    class Meta:
        model = Attendance
        fields = ('student', 'status', 'time_in', 'time_out', 'minutes_late', 
                 'reason_for_absence', 'note')
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'time_in': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'time_out': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'minutes_late': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'reason_for_absence': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        reason = cleaned_data.get('reason_for_absence')
        
        if status in ['A', 'E'] and not reason:
            raise ValidationError("Please provide a reason for absence.")
        
        return cleaned_data


class AttendanceReportForm(forms.Form):
    """Form for generating attendance reports"""
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
    report_type = forms.ChoiceField(
        choices=[
            ('daily', 'Daily Report'),
            ('weekly', 'Weekly Report'),
            ('monthly', 'Monthly Report'),
            ('termly', 'Termly Report'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        report_type = cleaned_data.get('report_type')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if report_type in ['daily', 'weekly', 'monthly'] and not (start_date and end_date):
            raise ValidationError("Please provide start and end dates for custom reports.")
        
        return cleaned_data
