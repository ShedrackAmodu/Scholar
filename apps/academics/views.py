from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Avg, Sum, Count, Max, Min
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
import json

from .models import (
    Assessment, SubjectAssessment, Score, SubjectScore,
    ReportCard, ClassPerformance
)
from .forms import (
    AssessmentForm, SubjectAssessmentForm, BulkScoreEntryForm,
    IndividualScoreForm, ScoreApprovalForm, ReportCardGenerationForm,
    ReportCardApprovalForm, ClassPerformanceForm
)
from apps.accounts.decorators import teacher_required, admin_required
from apps.classes.models import Class, Subject, SubjectAllocation, ClassLevel
from apps.students.models import Student
from apps.school.models import AcademicYear, Term, SchoolProfile

# Assessment Views
@method_decorator([login_required, admin_required], name='dispatch')
class AssessmentListView(ListView):
    """List all assessments"""
    model = Assessment
    template_name = 'academics/admin/assessment_list.html'
    context_object_name = 'assessments'
    
    def get_queryset(self):
        queryset = Assessment.objects.all()
        
        # Filter by type
        assessment_type = self.request.GET.get('type')
        if assessment_type:
            queryset = queryset.filter(assessment_type=assessment_type)
        
        # Filter by class level
        class_level = self.request.GET.get('class_level')
        if class_level:
            queryset = queryset.filter(class_level_id=class_level)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assessment_types'] = Assessment.AssessmentType.choices
        context['class_levels'] = ClassLevel.objects.all()
        return context

@method_decorator([login_required, admin_required], name='dispatch')
class AssessmentCreateView(SuccessMessageMixin, CreateView):
    """Create new assessment"""
    model = Assessment
    form_class = AssessmentForm
    template_name = 'academics/admin/assessment_form.html'
    success_url = reverse_lazy('academics:assessment_list')
    success_message = "Assessment %(name)s created successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class AssessmentUpdateView(SuccessMessageMixin, UpdateView):
    """Update assessment"""
    model = Assessment
    form_class = AssessmentForm
    template_name = 'academics/admin/assessment_form.html'
    success_url = reverse_lazy('academics:assessment_list')
    success_message = "Assessment %(name)s updated successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class AssessmentDeleteView(DeleteView):
    """Delete assessment"""
    model = Assessment
    template_name = 'academics/admin/assessment_confirm_delete.html'
    success_url = reverse_lazy('academics:assessment_list')
    success_message = "Assessment deleted successfully."

# Subject Assessment Views
@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAssessmentListView(ListView):
    """List all subject assessments"""
    model = SubjectAssessment
    template_name = 'academics/admin/subject_assessment_list.html'
    context_object_name = 'subject_assessments'
    
    def get_queryset(self):
        queryset = SubjectAssessment.objects.select_related(
            'subject', 'assessment', 'academic_year'
        )
        
        # Filter by academic year
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        # Filter by subject
        subject = self.request.GET.get('subject')
        if subject:
            queryset = queryset.filter(subject_id=subject)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academic_years'] = AcademicYear.objects.all()
        context['subjects'] = Subject.objects.all()
        return context

@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAssessmentCreateView(SuccessMessageMixin, CreateView):
    """Create new subject assessment"""
    model = SubjectAssessment
    form_class = SubjectAssessmentForm
    template_name = 'academics/admin/subject_assessment_form.html'
    success_url = reverse_lazy('academics:subject_assessment_list')
    success_message = "Subject assessment created successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAssessmentUpdateView(SuccessMessageMixin, UpdateView):
    """Update subject assessment"""
    model = SubjectAssessment
    form_class = SubjectAssessmentForm
    template_name = 'academics/admin/subject_assessment_form.html'
    success_url = reverse_lazy('academics:subject_assessment_list')
    success_message = "Subject assessment updated successfully."

@method_decorator([login_required, admin_required], name='dispatch')
class SubjectAssessmentDeleteView(DeleteView):
    """Delete subject assessment"""
    model = SubjectAssessment
    template_name = 'academics/admin/subject_assessment_confirm_delete.html'
    success_url = reverse_lazy('academics:subject_assessment_list')
    success_message = "Subject assessment deleted successfully."

# Score Views
@login_required
@teacher_required
def score_entry(request):
    """Entry point for score recording"""
    teacher = request.user
    
    # Get subjects taught by this teacher
    subjects_taught = Subject.objects.filter(
        allocations__teacher=teacher,
        allocations__academic_year__is_current=True
    ).distinct()
    
    # Get classes taught
    classes_taught = Class.objects.filter(
        subject_allocations__teacher=teacher,
        status='ACTIVE'
    ).distinct()
    
    context = {
        'subjects_taught': subjects_taught,
        'classes_taught': classes_taught,
        'title': 'Score Entry'
    }
    return render(request, 'academics/teacher/score_entry.html', context)

@login_required
@teacher_required
def bulk_score_entry(request):
    """Bulk score entry for a class and subject"""
    if request.method == 'POST':
        form = BulkScoreEntryForm(request.POST)
        if form.is_valid():
            subject_assessment = form.cleaned_data['subject_assessment']
            students = form.cleaned_data.get('students', [])
            scores_text = form.cleaned_data.get('scores', '')
            remarks = form.cleaned_data.get('remarks', '')
            
            # Parse scores
            score_list = [s.strip() for s in scores_text.split(',') if s.strip()]
            
            if len(students) != len(score_list):
                messages.error(request, "Number of scores doesn't match number of students.")
                return redirect('academics:bulk_score_entry')
            
            # Create scores
            created_count = 0
            for student, score_value in zip(students, score_list):
                try:
                    score = float(score_value)
                    Score.objects.update_or_create(
                        student=student,
                        subject_assessment=subject_assessment,
                        defaults={
                            'score': score,
                            'remarks': remarks,
                            'recorded_by': request.user
                        }
                    )
                    created_count += 1
                except ValueError:
                    messages.warning(request, f"Invalid score value for {student.user.get_full_name()}")
                except Exception as e:
                    messages.error(request, f"Error saving score for {student.user.get_full_name()}: {str(e)}")
            
            messages.success(request, f"{created_count} scores recorded successfully.")
            return redirect('academics:score_entry')
    else:
        # Get parameters from URL
        class_id = request.GET.get('class_id')
        subject_id = request.GET.get('subject_id')
        assessment_id = request.GET.get('assessment_id')
        
        if class_id and subject_id:
            class_obj = get_object_or_404(Class, id=class_id)
            subject = get_object_or_404(Subject, id=subject_id)
            
            # Get students in this class
            students = Student.objects.filter(
                current_class=class_obj,
                enrollment_status='ACTIVE'
            ).select_related('user')
            
            # Get subject assessments for this subject
            subject_assessments = SubjectAssessment.objects.filter(
                subject=subject,
                academic_year__is_current=True
            ).select_related('assessment')
            
            form = BulkScoreEntryForm(initial={
                'class_assigned': class_obj
            })
            form.fields['students'] = forms.ModelMultipleChoiceField(
                queryset=students,
                widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
            )
        else:
            form = BulkScoreEntryForm()
            students = []
            subject_assessments = []
    
    context = {
        'form': form,
        'students': students if 'students' in locals() else [],
        'subject_assessments': subject_assessments if 'subject_assessments' in locals() else [],
        'title': 'Bulk Score Entry'
    }
    return render(request, 'academics/teacher/bulk_score_entry.html', context)

@login_required
@teacher_required
def individual_score_entry(request):
    """Individual score entry for a student"""
    if request.method == 'POST':
        form = IndividualScoreForm(request.POST)
        if form.is_valid():
            score = form.save(commit=False)
            score.recorded_by = request.user
            score.save()
            
            # Create notification for student and parents
            Notification.objects.create(
                notification_type='SCORE',
                title='New Score Posted',
                message=f"A new score has been posted for {score.student.user.get_full_name()} in {score.subject_assessment.subject.name}",
                recipient=score.student.user
            )
            
            messages.success(request, "Score recorded successfully.")
            return redirect('academics:score_entry')
    else:
        form = IndividualScoreForm()
    
    context = {
        'form': form,
        'title': 'Individual Score Entry'
    }
    return render(request, 'academics/teacher/individual_score_entry.html', context)

@login_required
@teacher_required
def edit_scores(request, class_id, subject_id):
    """Edit scores for a class and subject"""
    class_obj = get_object_or_404(Class, id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Verify teacher is authorized
    if not SubjectAllocation.objects.filter(
        teacher=request.user,
        class_assigned=class_obj,
        subject=subject,
        academic_year__is_current=True
    ).exists():
        messages.error(request, "You are not authorized to edit scores for this class/subject.")
        return redirect('academics:score_entry')
    
    # Get current term
    current_term = Term.objects.filter(is_current=True).first()
    
    # Get subject assessments for current term
    subject_assessments = SubjectAssessment.objects.filter(
        subject=subject,
        term=current_term.term if current_term else None,
        academic_year__is_current=True
    )
    
    # Get students in this class
    students = Student.objects.filter(
        current_class=class_obj,
        enrollment_status='ACTIVE'
    ).select_related('user')
    
    # Get existing scores
    scores = Score.objects.filter(
        student__in=students,
        subject_assessment__in=subject_assessments
    ).select_related('student__user', 'subject_assessment__assessment')
    
    # Organize scores by student and assessment
    score_matrix = {}
    for student in students:
        score_matrix[student.id] = {
            'student': student,
            'scores': {}
        }
    
    for score in scores:
        score_matrix[score.student.id]['scores'][score.subject_assessment_id] = score
    
    context = {
        'class_obj': class_obj,
        'subject': subject,
        'students': students,
        'subject_assessments': subject_assessments,
        'score_matrix': score_matrix,
        'title': f'Edit Scores - {subject.name} - {class_obj.name}'
    }
    return render(request, 'academics/teacher/edit_scores.html', context)

@login_required
@teacher_required
def save_scores_ajax(request):
    """AJAX endpoint to save individual score"""
    if request.method == 'POST':
        score_id = request.POST.get('score_id')
        student_id = request.POST.get('student_id')
        assessment_id = request.POST.get('assessment_id')
        score_value = request.POST.get('score')
        
        try:
            if score_id:
                score = get_object_or_404(Score, id=score_id)
            else:
                score = Score()
                score.student_id = student_id
                score.subject_assessment_id = assessment_id
                score.recorded_by = request.user
            
            score.score = float(score_value)
            score.save()
            
            return JsonResponse({
                'success': True,
                'score_id': score.id,
                'percentage': score.percentage,
                'grade': score.grade
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@teacher_required
def approve_scores(request, class_id, subject_id):
    """Approve scores for a class and subject"""
    class_obj = get_object_or_404(Class, id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        form = ScoreApprovalForm(request.POST)
        if form.is_valid():
            approve_all = form.cleaned_data['approve_all']
            
            # Get current term
            current_term = Term.objects.filter(is_current=True).first()
            
            # Get scores to approve
            scores = Score.objects.filter(
                student__current_class=class_obj,
                subject_assessment__subject=subject,
                subject_assessment__term=current_term.term if current_term else None,
                subject_assessment__academic_year__is_current=True
            )
            
            if approve_all:
                scores.update(
                    is_approved=True,
                    approved_by=request.user,
                    approved_at=timezone.now()
                )
                messages.success(request, f"All scores approved successfully.")
            else:
                # Individual approval would be handled differently
                messages.info(request, "Individual approval not implemented in this view.")
            
            return redirect('academics:edit_scores', class_id=class_obj.id, subject_id=subject.id)
    else:
        form = ScoreApprovalForm()
    
    context = {
        'form': form,
        'class_obj': class_obj,
        'subject': subject,
        'title': 'Approve Scores'
    }
    return render(request, 'academics/teacher/approve_scores.html', context)

# Report Card Views
@login_required
@teacher_required
def generate_report_cards(request):
    """Generate report cards for a class"""
    if request.method == 'POST':
        form = ReportCardGenerationForm(request.POST)
        if form.is_valid():
            class_assigned = form.cleaned_data['class_assigned']
            term = form.cleaned_data['term']
            academic_year = form.cleaned_data['academic_year']
            generate_for_all = form.cleaned_data['generate_for_all']
            
            # Verify teacher is class teacher or admin
            if class_assigned.class_teacher != request.user and request.user.role not in ['SUPER_ADMIN', 'ADMIN', 'PRINCIPAL']:
                messages.error(request, "You are not authorized to generate report cards for this class.")
                return redirect('academics:report_cards')
            
            if generate_for_all:
                students = Student.objects.filter(
                    current_class=class_assigned,
                    enrollment_status='ACTIVE'
                )
            else:
                students = form.cleaned_data.get('students', [])
            
            generated_count = 0
            for student in students:
                try:
                    report_card = generate_student_report_card(
                        student, class_assigned, term, academic_year, request.user
                    )
                    generated_count += 1
                except Exception as e:
                    messages.error(request, f"Error generating report for {student.user.get_full_name()}: {str(e)}")
            
            messages.success(request, f"{generated_count} report cards generated successfully.")
            return redirect('academics:report_card_list', class_id=class_assigned.id)
    else:
        form = ReportCardGenerationForm()
    
    context = {
        'form': form,
        'title': 'Generate Report Cards'
    }
    return render(request, 'academics/teacher/generate_report_cards.html', context)

def generate_student_report_card(student, class_assigned, term, academic_year, generated_by):
    """Helper function to generate a single report card"""
    # Get all subjects for this class
    subjects = Subject.objects.filter(class_level=class_assigned.class_level)
    
    subject_scores = {}
    subject_grades = {}
    total_score = 0
    subject_count = 0
    
    for subject in subjects:
        # Get all scores for this student in this subject for the term
        scores = Score.objects.filter(
            student=student,
            subject_assessment__subject=subject,
            subject_assessment__term=term,
            subject_assessment__academic_year=academic_year
        )
        
        if scores.exists():
            # Calculate weighted total
            subject_total = 0
            for score in scores:
                weighted = (score.score / score.subject_assessment.max_score) * score.subject_assessment.assessment.weight_percentage
                subject_total += weighted
            
            subject_scores[subject.name] = round(subject_total, 2)
            subject_grades[subject.name] = calculate_grade(subject_total)
            total_score += subject_total
            subject_count += 1
    
    # Calculate average
    average_score = total_score / subject_count if subject_count > 0 else 0
    
    # Calculate position (simplified - you'd need to compare with all students in class)
    position = calculate_position(student, class_assigned, term, academic_year)
    
    # Get attendance summary
    attendance_summary = get_attendance_summary(student, term, academic_year)
    
    # Create or update report card
    report_card, created = ReportCard.objects.update_or_create(
        student=student,
        term=term,
        academic_year=academic_year,
        defaults={
            'class_assigned': class_assigned,
            'subject_scores': subject_scores,
            'subject_grades': subject_grades,
            'total_score': total_score,
            'average_score': average_score,
            'position': position,
            'total_students': Student.objects.filter(
                current_class=class_assigned,
                enrollment_status='ACTIVE'
            ).count(),
            'total_school_days': attendance_summary['total_days'],
            'days_present': attendance_summary['present_days'],
            'days_absent': attendance_summary['absent_days'],
            'generated_by': generated_by
        }
    )
    
    return report_card

def calculate_grade(score):
    """Calculate grade based on score"""
    if score >= 70:
        return 'A'
    elif score >= 60:
        return 'B'
    elif score >= 50:
        return 'C'
    elif score >= 45:
        return 'D'
    elif score >= 40:
        return 'E'
    else:
        return 'F'

def calculate_position(student, class_assigned, term, academic_year):
    """Calculate student's position in class"""
    # Get all students in class
    students = Student.objects.filter(
        current_class=class_assigned,
        enrollment_status='ACTIVE'
    )
    
    # Get or calculate averages for all students
    averages = {}
    for s in students:
        # Get all scores for this student
        scores = Score.objects.filter(
            student=s,
            subject_assessment__term=term,
            subject_assessment__academic_year=academic_year
        )
        
        if scores.exists():
            total = 0
            count = 0
            for score in scores:
                weighted = (score.score / score.subject_assessment.max_score) * score.subject_assessment.assessment.weight_percentage
                total += weighted
                count += 1
            avg = total / count if count > 0 else 0
            averages[s.id] = avg
    
    # Sort by average
    sorted_students = sorted(averages.items(), key=lambda x: x[1], reverse=True)
    
    # Find position
    for idx, (student_id, _) in enumerate(sorted_students, 1):
        if student_id == student.id:
            return idx
    
    return None

def get_attendance_summary(student, term, academic_year):
    """Get attendance summary for student"""
    attendance = Attendance.objects.filter(
        student=student,
        session__term=term,
        session__academic_year=academic_year
    )
    
    total_days = attendance.count()
    present_days = attendance.filter(status='P').count()
    absent_days = attendance.filter(status='A').count()
    
    return {
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days
    }

@login_required
def report_card_list(request, class_id=None):
    """List report cards for a class"""
    if not class_id:
        messages.error(request, "Class not specified.")
        return redirect('academics:score_entry')

    class_obj = get_object_or_404(Class, id=class_id)
    
    # Check permission
    if class_obj.class_teacher != request.user and request.user.role not in ['SUPER_ADMIN', 'ADMIN', 'PRINCIPAL']:
        messages.error(request, "You are not authorized to view these report cards.")
        return redirect('dashboard:home')
    
    report_cards = ReportCard.objects.filter(
        class_assigned=class_obj
    ).select_related('student__user').order_by('position')
    
    context = {
        'class_obj': class_obj,
        'report_cards': report_cards,
        'title': f'Report Cards - {class_obj.name}'
    }
    return render(request, 'academics/teacher/report_card_list.html', context)

@login_required
def view_report_card(request, pk):
    """View individual report card"""
    report_card = get_object_or_404(ReportCard, pk=pk)
    
    # Check permission
    user = request.user
    if user.role == 'STUDENT' and report_card.student.user != user:
        messages.error(request, "You don't have permission to view this report card.")
        return redirect('dashboard:home')
    elif user.role == 'PARENT' and report_card.student not in user.parent_profile.children.all():
        messages.error(request, "You don't have permission to view this report card.")
        return redirect('dashboard:home')
    elif user.role == 'TEACHER' and report_card.class_assigned.class_teacher != user:
        if not SubjectAllocation.objects.filter(teacher=user, class_assigned=report_card.class_assigned).exists():
            messages.error(request, "You don't have permission to view this report card.")
            return redirect('dashboard:home')
    
    context = {
        'report_card': report_card,
        'title': f'Report Card - {report_card.student.user.get_full_name()}'
    }
    return render(request, 'academics/report_card_detail.html', context)

@login_required
def download_report_card_pdf(request, pk):
    """Download report card as PDF"""
    report_card = get_object_or_404(ReportCard, pk=pk)
    
    # Check permission (same as view)
    # ... permission checks ...
    
    # Render HTML
    html_string = render_to_string('academics/pdf/report_card_pdf.html', {
        'report_card': report_card,
        'school': SchoolProfile.objects.first()
    })
    
    # Generate PDF
    html = HTML(string=html_string)
    result = html.write_pdf()
    
    # Create response
    response = HttpResponse(result, content_type='application/pdf')
    filename = f"report_card_{report_card.student.admission_number}_{report_card.term}_{report_card.academic_year}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@login_required
@admin_required
def approve_report_cards(request, class_id):
    """Approve report cards for a class"""
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.method == 'POST':
        form = ReportCardApprovalForm(request.POST)
        if form.is_valid():
            class_teacher_comment = form.cleaned_data['class_teacher_comment']
            principal_comment = form.cleaned_data['principal_comment']
            approve = form.cleaned_data['approve']
            
            # Get all report cards for this class
            report_cards = ReportCard.objects.filter(
                class_assigned=class_obj,
                is_approved=False
            )
            
            for report_card in report_cards:
                if class_teacher_comment:
                    report_card.class_teacher_comment = class_teacher_comment
                if principal_comment:
                    report_card.principal_comment = principal_comment
                if approve:
                    report_card.is_approved = True
                    report_card.approved_by = request.user
                    report_card.approved_at = timezone.now()
                report_card.save()
            
            messages.success(request, f"{report_cards.count()} report cards approved successfully.")
            return redirect('academics:report_card_list', class_id=class_obj.id)
    else:
        form = ReportCardApprovalForm()
    
    context = {
        'form': form,
        'class_obj': class_obj,
        'title': 'Approve Report Cards'
    }
    return render(request, 'academics/principal/approve_report_cards.html', context)

# Class Performance Views
@login_required
@admin_required
def class_performance(request):
    """View class performance analytics"""
    if request.method == 'POST':
        form = ClassPerformanceForm(request.POST)
        if form.is_valid():
            class_assigned = form.cleaned_data['class_assigned']
            term = form.cleaned_data['term']
            academic_year = form.cleaned_data['academic_year']
            
            # Calculate class performance
            performance = calculate_class_performance(class_assigned, term, academic_year)
            
            return redirect('academics:class_performance_detail', 
                          class_id=class_assigned.id, 
                          term=term, 
                          year_id=academic_year.id)
    else:
        form = ClassPerformanceForm()
    
    context = {
        'form': form,
        'title': 'Class Performance Analysis'
    }
    return render(request, 'academics/principal/class_performance.html', context)

def calculate_class_performance(class_assigned, term, academic_year):
    """Calculate performance metrics for a class"""
    students = Student.objects.filter(
        current_class=class_assigned,
        enrollment_status='ACTIVE'
    )
    
    subjects = Subject.objects.filter(class_level=class_assigned.class_level)
    
    subject_averages = {}
    all_averages = []
    
    for subject in subjects:
        scores = Score.objects.filter(
            student__in=students,
            subject_assessment__subject=subject,
            subject_assessment__term=term,
            subject_assessment__academic_year=academic_year
        )
        
        if scores.exists():
            # Calculate weighted averages per student
            student_totals = {}
            for score in scores:
                if score.student_id not in student_totals:
                    student_totals[score.student_id] = 0
                weighted = (score.score / score.subject_assessment.max_score) * score.subject_assessment.assessment.weight_percentage
                student_totals[score.student_id] += weighted
            
            avg = sum(student_totals.values()) / len(student_totals) if student_totals else 0
            subject_averages[subject.name] = round(avg, 2)
            
            # Collect all averages for overall class average
            all_averages.extend(student_totals.values())
    
    class_average = sum(all_averages) / len(all_averages) if all_averages else 0
    highest_score = max(all_averages) if all_averages else 0
    lowest_score = min(all_averages) if all_averages else 0
    pass_rate = len([a for a in all_averages if a >= 50]) / len(all_averages) * 100 if all_averages else 0
    
    # Save or update class performance
    performance, created = ClassPerformance.objects.update_or_create(
        class_assigned=class_assigned,
        term=term,
        academic_year=academic_year,
        defaults={
            'total_students': students.count(),
            'subject_averages': subject_averages,
            'class_average': class_average,
            'highest_score': highest_score,
            'lowest_score': lowest_score,
            'pass_rate': pass_rate
        }
    )
    
    return performance

@login_required
@admin_required
def class_performance_detail(request, class_id, term, year_id):
    """View detailed class performance"""
    class_assigned = get_object_or_404(Class, id=class_id)
    academic_year = get_object_or_404(AcademicYear, id=year_id)
    
    performance = get_object_or_404(
        ClassPerformance,
        class_assigned=class_assigned,
        term=term,
        academic_year=academic_year
    )
    
    # Get subject details
    subjects = Subject.objects.filter(class_level=class_assigned.class_level)
    
    # Get student rankings
    students = Student.objects.filter(
        current_class=class_assigned,
        enrollment_status='ACTIVE'
    ).select_related('user')
    
    rankings = []
    for student in students:
        # Calculate student average
        scores = Score.objects.filter(
            student=student,
            subject_assessment__term=term,
            subject_assessment__academic_year=academic_year
        )
        
        if scores.exists():
            total = 0
            count = 0
            for score in scores:
                weighted = (score.score / score.subject_assessment.max_score) * score.subject_assessment.assessment.weight_percentage
                total += weighted
                count += 1
            avg = total / count
            rankings.append({
                'student': student,
                'average': avg
            })
    
    rankings.sort(key=lambda x: x['average'], reverse=True)
    
    context = {
        'performance': performance,
        'class_assigned': class_assigned,
        'term': term,
        'academic_year': academic_year,
        'subjects': subjects,
        'rankings': rankings,
        'title': f'Class Performance - {class_assigned.name}'
    }
    return render(request, 'academics/principal/class_performance_detail.html', context)

# Student Performance Views (for students/parents)
@login_required
def student_performance(request, student_id=None):
    """View student performance (for students and parents)"""
    if request.user.role == 'STUDENT':
        student = request.user.student_profile
    elif request.user.role == 'PARENT' and student_id:
        student = get_object_or_404(Student, id=student_id)
        # Verify parent owns this student
        if not request.user.parent_profile.children.filter(id=student_id).exists():
            messages.error(request, "You don't have permission to view this student.")
            return redirect('dashboard:home')
    else:
        messages.error(request, "Invalid request.")
        return redirect('dashboard:home')
    
    # Get report cards
    report_cards = ReportCard.objects.filter(
        student=student
    ).order_by('-academic_year', '-term')
    
    # Get current term scores
    current_term = Term.objects.filter(is_current=True).first()
    if current_term:
        current_scores = Score.objects.filter(
            student=student,
            subject_assessment__term=current_term.term,
            subject_assessment__academic_year__is_current=True
        ).select_related('subject_assessment__subject', 'subject_assessment__assessment')
    else:
        current_scores = []
    
    context = {
        'student': student,
        'report_cards': report_cards,
        'current_scores': current_scores,
        'current_term': current_term,
        'title': f'Performance - {student.user.get_full_name()}'
    }
    return render(request, 'academics/student/performance.html', context)

# API Views
@login_required
def get_assessments_for_subject(request):
    """API endpoint to get assessments for a subject"""
    subject_id = request.GET.get('subject_id')
    if subject_id:
        assessments = SubjectAssessment.objects.filter(
            subject_id=subject_id,
            academic_year__is_current=True
        ).select_related('assessment').values(
            'id', 'assessment__name', 'assessment__assessment_type', 'max_score'
        )
        return JsonResponse(list(assessments), safe=False)
    return JsonResponse([], safe=False)

@login_required
def get_students_with_scores(request):
    """API endpoint to get students with existing scores for an assessment"""
    assessment_id = request.GET.get('assessment_id')
    class_id = request.GET.get('class_id')
    
    if assessment_id and class_id:
        students = Student.objects.filter(
            current_class_id=class_id,
            enrollment_status='ACTIVE'
        ).select_related('user')
        
        data = []
        for student in students:
            score = Score.objects.filter(
                student=student,
                subject_assessment_id=assessment_id
            ).first()
            
            data.append({
                'student_id': student.id,
                'student_name': student.user.get_full_name(),
                'admission_number': student.admission_number,
                'score_id': score.id if score else None,
                'score': float(score.score) if score else None
            })
        
        return JsonResponse(data, safe=False)
    
    return JsonResponse([], safe=False)

@login_required
def academic_calendar(request):
    """Display the academic calendar for the school"""
    try:
        school_profile = SchoolProfile.objects.first()
    except:
        school_profile = None
    
    # Get current or all academic years
    try:
        academic_years = AcademicYear.objects.all().order_by('-start_year')
    except:
        academic_years = []
    
    context = {
        'school_profile': school_profile,
        'academic_years': academic_years,
        'title': 'Academic Calendar'
    }
    return render(request, 'academics/academic_calendar.html', context)
