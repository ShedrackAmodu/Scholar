from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.utils import timezone
import csv
import io

from .models import Student, StudentDocument, StudentHistory
from .forms import (
    StudentForm, StudentEnrollmentForm, StudentDocumentForm,
    StudentSearchForm, BulkStudentUploadForm
)
from apps.accounts.models import User
from apps.accounts.decorators import admin_required, teacher_required, principal_required
from apps.classes.models import Class
from apps.school.models import AcademicYear
from apps.academics.models import Score, ReportCard
from apps.attendance.models import Attendance

# Student List Views
@method_decorator([login_required, principal_required], name='dispatch')
class StudentListView(ListView):
    """List all students"""
    model = Student
    template_name = 'students/admin/student_list.html'
    context_object_name = 'students'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Student.objects.select_related(
            'user', 'current_class'
        ).prefetch_related('parentstudentrelationship_set__parent')
        
        # Search
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(admission_number__icontains=query) |
                Q(user__email__icontains=query)
            )
        
        # Filter by class
        class_id = self.request.GET.get('class')
        if class_id:
            queryset = queryset.filter(current_class_id=class_id)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(enrollment_status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.filter(status='ACTIVE')
        context['status_choices'] = Student.Status.choices
        context['search_form'] = StudentSearchForm(self.request.GET)
        return context

@method_decorator([login_required, principal_required], name='dispatch')
class StudentDetailView(DetailView):
    """View student details"""
    model = Student
    template_name = 'students/admin/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Get academic records
        context['scores'] = Score.objects.filter(
            student=student
        ).select_related('subject_assessment__subject')[:20]
        
        # Get report cards
        context['report_cards'] = ReportCard.objects.filter(
            student=student
        ).order_by('-academic_year', '-term')
        
        # Get attendance
        context['attendance'] = Attendance.objects.filter(
            student=student
        ).select_related('session')[:30]
        
        # Get documents
        context['documents'] = StudentDocument.objects.filter(student=student)
        
        # Get parents
        context['parents'] = student.parentstudentrelationship_set.all()
        
        # Get history
        context['history'] = StudentHistory.objects.filter(
            student=student
        ).select_related('class_assigned', 'academic_year')
        
        return context

# Student CRUD Views
@method_decorator([login_required, principal_required], name='dispatch')
class StudentCreateView(SuccessMessageMixin, CreateView):
    """Create new student"""
    model = Student
    form_class = StudentForm
    template_name = 'students/admin/student_form.html'
    success_url = reverse_lazy('students:student_list')
    success_message = "Student %(user)s created successfully."
    
    def form_valid(self, form):
        # Create user account first
        user = User.objects.create_user(
            username=form.cleaned_data.get('email').split('@')[0],
            email=form.cleaned_data.get('guardian_email'),
            password='Student@123',  # Default password
            first_name=form.cleaned_data.get('user_first_name', ''),
            last_name=form.cleaned_data.get('user_last_name', ''),
            role='STUDENT'
        )
        form.instance.user = user
        return super().form_valid(form)

@method_decorator([login_required, principal_required], name='dispatch')
class StudentUpdateView(SuccessMessageMixin, UpdateView):
    """Update student"""
    model = Student
    form_class = StudentForm
    template_name = 'students/admin/student_form.html'
    success_url = reverse_lazy('students:student_list')
    success_message = "Student %(user)s updated successfully."

@method_decorator([login_required, principal_required], name='dispatch')
class StudentDeleteView(DeleteView):
    """Delete student"""
    model = Student
    template_name = 'students/admin/student_confirm_delete.html'
    success_url = reverse_lazy('students:student_list')
    success_message = "Student deleted successfully."
    
    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        # Also delete user account
        student.user.delete()
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Student Enrollment
@login_required
@principal_required
def student_enrollment(request):
    """Enroll students in classes"""
    if request.method == 'POST':
        form = StudentEnrollmentForm(request.POST)
        if form.is_valid():
            students = form.cleaned_data['students']
            class_assigned = form.cleaned_data['class_assigned']
            academic_year = form.cleaned_data['academic_year']
            enrollment_date = form.cleaned_data['enrollment_date']
            
            for student in students:
                # Create history record
                StudentHistory.objects.create(
                    student=student,
                    class_assigned=class_assigned,
                    academic_year=academic_year,
                    date_from=enrollment_date
                )
                
                # Update student's current class
                student.current_class = class_assigned
                student.save()
                
                # Update class enrollment count
                class_assigned.current_enrollment += 1
                class_assigned.save()
            
            messages.success(request, f"{students.count()} students enrolled successfully.")
            return redirect('students:student_list')
    else:
        form = StudentEnrollmentForm()
    
    context = {
        'form': form,
        'title': 'Bulk Student Enrollment'
    }
    return render(request, 'students/admin/enrollment_form.html', context)

# Student Documents
@login_required
def student_documents(request, student_id):
    """View student documents"""
    student = get_object_or_404(Student, id=student_id)
    
    # Check permission
    if request.user.role not in ['SUPER_ADMIN', 'ADMIN', 'PRINCIPAL'] and \
       request.user != student.user:
        messages.error(request, "You don't have permission to view these documents.")
        return redirect('home')
    
    documents = StudentDocument.objects.filter(student=student)
    
    context = {
        'student': student,
        'documents': documents,
        'title': f'Documents - {student.user.get_full_name()}'
    }
    return render(request, 'students/documents.html', context)

@login_required
def upload_document(request, student_id):
    """Upload document for student"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = StudentDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.student = student
            document.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect('students:student_documents', student_id=student.id)
    else:
        form = StudentDocumentForm()
    
    context = {
        'form': form,
        'student': student,
        'title': 'Upload Document'
    }
    return render(request, 'students/upload_document.html', context)

# Bulk Operations
@login_required
@principal_required
def bulk_student_upload(request):
    """Bulk upload students from CSV"""
    if request.method == 'POST':
        form = BulkStudentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            class_assigned = form.cleaned_data['class_assigned']
            
            # Read CSV file
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string, delimiter=',')
            
            # Skip header row
            next(reader, None)
            
            created_count = 0
            error_count = 0
            
            for row in reader:
                try:
                    # Create user
                    user = User.objects.create_user(
                        username=row[2].split('@')[0],  # email
                        email=row[2],
                        password='Student@123',
                        first_name=row[0],
                        last_name=row[1],
                        role='STUDENT'
                    )
                    
                    # Create student
                    student = Student.objects.create(
                        user=user,
                        admission_number=row[3],
                        date_of_birth=row[4],
                        gender=row[5],
                        address=row[6],
                        guardian_name=row[7],
                        guardian_phone=row[8],
                        guardian_email=row[9],
                        current_class=class_assigned
                    )
                    
                    created_count += 1
                    
                except Exception as e:
                    error_count += 1
            
            messages.success(request, f"{created_count} students created successfully. {error_count} errors.")
            return redirect('students:student_list')
    else:
        form = BulkStudentUploadForm()
    
    context = {
        'form': form,
        'title': 'Bulk Student Upload'
    }
    return render(request, 'students/admin/bulk_upload.html', context)

# Student Dashboard Views
@login_required
def student_dashboard(request):
    """Student dashboard"""
    student = request.user.student_profile
    
    # Get current class info
    current_class = student.current_class
    
    # Get recent scores
    recent_scores = Score.objects.filter(
        student=student
    ).select_related('subject_assessment__subject').order_by('-recorded_at')[:10]
    
    # Get attendance summary
    attendance_summary = Attendance.objects.filter(
        student=student
    ).values('status').annotate(count=Count('status'))
    
    # Get latest report card
    latest_report = ReportCard.objects.filter(
        student=student
    ).order_by('-academic_year', '-term').first()
    
    # Get upcoming events
    upcoming_events = Event.objects.filter(
        start_date__gte=timezone.now(),
        is_public=True
    ).order_by('start_date')[:5]
    
    context = {
        'student': student,
        'current_class': current_class,
        'recent_scores': recent_scores,
        'attendance_summary': attendance_summary,
        'latest_report': latest_report,
        'upcoming_events': upcoming_events,
        'title': 'Student Dashboard'
    }
    return render(request, 'students/dashboard/student_dashboard.html', context)

@login_required
def student_scores(request):
    """View all scores for student"""
    student = request.user.student_profile
    
    scores = Score.objects.filter(
        student=student
    ).select_related(
        'subject_assessment__subject',
        'subject_assessment__assessment'
    ).order_by('-subject_assessment__academic_year', '-subject_assessment__term')
    
    # Group by term
    terms = {}
    for score in scores:
        key = f"{score.subject_assessment.academic_year}_{score.subject_assessment.term}"
        if key not in terms:
            terms[key] = {
                'academic_year': score.subject_assessment.academic_year,
                'term': score.subject_assessment.term,
                'scores': []
            }
        terms[key]['scores'].append(score)
    
    context = {
        'terms': terms.values(),
        'title': 'My Scores'
    }
    return render(request, 'students/dashboard/scores.html', context)

@login_required
def student_attendance(request):
    """View attendance records for student"""
    student = request.user.student_profile
    
    attendance = Attendance.objects.filter(
        student=student
    ).select_related('session').order_by('-session__date')
    
    # Calculate statistics
    total_days = attendance.count()
    present_days = attendance.filter(status='P').count()
    absent_days = attendance.filter(status='A').count()
    late_days = attendance.filter(status='L').count()
    
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    context = {
        'attendance': attendance,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
        'attendance_percentage': attendance_percentage,
        'title': 'My Attendance'
    }
    return render(request, 'students/dashboard/attendance.html', context)

@login_required
def student_report_cards(request):
    """View report cards for student"""
    student = request.user.student_profile
    
    report_cards = ReportCard.objects.filter(
        student=student
    ).order_by('-academic_year', '-term')
    
    context = {
        'report_cards': report_cards,
        'title': 'My Report Cards'
    }
    return render(request, 'students/dashboard/report_cards.html', context)

# API Views
@login_required
def get_students_for_class(request):
    """API endpoint to get students for a class"""
    class_id = request.GET.get('class_id')
    if class_id:
        students = Student.objects.filter(
            current_class_id=class_id,
            enrollment_status='ACTIVE'
        ).select_related('user').values(
            'id', 'user__first_name', 'user__last_name', 'admission_number'
        )
        return JsonResponse(list(students), safe=False)
    return JsonResponse([], safe=False)

@login_required
def promote_students(request):
    """Promote students to next class"""
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        next_class_id = request.POST.get('next_class_id')
        academic_year_id = request.POST.get('academic_year_id')
        
        class_obj = get_object_or_404(Class, id=class_id)
        next_class = get_object_or_404(Class, id=next_class_id)
        academic_year = get_object_or_404(AcademicYear, id=academic_year_id)
        
        students = Student.objects.filter(
            current_class=class_obj,
            enrollment_status='ACTIVE'
        )
        
        for student in students:
            # Create history
            StudentHistory.objects.create(
                student=student,
                class_assigned=next_class,
                academic_year=academic_year,
                date_from=timezone.now().date(),
                reason='Promotion'
            )
            
            # Update student
            student.current_class = next_class
            student.save()
        
        messages.success(request, f"{students.count()} students promoted successfully.")
        return redirect('students:student_list')
    
    return redirect('students:student_list')
