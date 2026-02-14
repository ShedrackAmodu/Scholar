from django import forms
from django.core.exceptions import ValidationError
from .models import Event, Notice, Assignment, AssignmentSubmission, Notification, ClassMessage
from apps.classes.models import Class, Subject
from apps.students.models import Student
from django.utils import timezone


class EventForm(forms.ModelForm):
    """Form for creating and editing events"""
    
    class Meta:
        model = Event
        exclude = ('created_by', 'created_at', 'updated_at')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'banner_image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'target_classes': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'target_roles': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'requires_rsvp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_attendees': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise ValidationError("End date must be after start date.")
        
        return cleaned_data


class NoticeForm(forms.ModelForm):
    """Form for creating notices"""
    
    class Meta:
        model = Notice
        exclude = ('created_by', 'created_at', 'updated_at', 'view_count')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'summary': forms.TextInput(attrs={'class': 'form-control'}),
            'notice_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'publish_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'expiry_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'target_classes': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'target_roles': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        publish_date = cleaned_data.get('publish_date')
        expiry_date = cleaned_data.get('expiry_date')
        
        if publish_date and expiry_date and publish_date >= expiry_date:
            raise ValidationError("Expiry date must be after publish date.")
        
        return cleaned_data


class AssignmentForm(forms.ModelForm):
    """Form for creating assignments"""
    
    class Meta:
        model = Assignment
        exclude = ('created_by', 'created_at', 'updated_at')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'class_assigned': forms.Select(attrs={'class': 'form-control'}),
            'date_assigned': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_graded': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'teacher_profile'):
            # Filter subjects to those taught by this teacher
            self.fields['subject'].queryset = Subject.objects.filter(
                allocations__teacher=user
            )
            # Filter classes to those taught by this teacher
            self.fields['class_assigned'].queryset = Class.objects.filter(
                subject_allocations__teacher=user
            ).distinct()


class AssignmentSubmissionForm(forms.ModelForm):
    """Form for submitting assignments"""
    
    class Meta:
        model = AssignmentSubmission
        fields = ('submission_file', 'submission_text')
        widgets = {
            'submission_file': forms.FileInput(attrs={'class': 'form-control'}),
            'submission_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class GradeAssignmentForm(forms.ModelForm):
    """Form for grading assignments"""
    
    class Meta:
        model = AssignmentSubmission
        fields = ('score', 'feedback')
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_score(self):
        score = self.cleaned_data.get('score')
        assignment = self.instance.assignment
        
        if score and assignment.total_marks and score > assignment.total_marks:
            raise ValidationError(f"Score cannot exceed {assignment.total_marks}.")
        
        return score


class ClassMessageForm(forms.ModelForm):
    """Form for sending messages to classes"""
    
    class Meta:
        model = ClassMessage
        fields = ('class_assigned', 'subject', 'message', 'attachment', 
                 'send_to_students', 'send_to_parents')
        widgets = {
            'class_assigned': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'send_to_students': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_to_parents': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.role == 'TEACHER':
            # Filter classes to those taught by this teacher
            self.fields['class_assigned'].queryset = Class.objects.filter(
                subject_allocations__teacher=user
            ).distinct()


class NotificationFilterForm(forms.Form):
    """Form for filtering notifications"""
    notification_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Notification.NotificationType.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_read = forms.ChoiceField(
        choices=[('', 'All'), ('True', 'Read'), ('False', 'Unread')],
        required=False,
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
