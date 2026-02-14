from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
import csv

from .models import AttendanceSession, Attendance, AttendanceSummary
from .forms import (
    AttendanceSessionForm, BulkAttendanceForm,
    IndividualAttendanceForm, AttendanceReportForm
)
from apps.accounts.decorators import teacher_required, principal_required, admin_required
from apps.classes.models import Class, SubjectAllocation
from apps.students.models import Student
from apps.school.models import Term, AcademicYear

# Attendance Session Views
@login_required
@teacher_required
def take_attendance(request):
    """Take attendance for a class"""
    teacher = request.user
    
    # Get classes taught by this teacher
    classes_taught = Class.objects.filter(
        Q(subject_allocations__teacher=teacher) |
        Q(class_teacher=teacher),
        status='ACTIVE'
    ).distinct()
    
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        date = request.POST.get('date')
        
        class_obj = get_object_or_404(Class, id=class_id)
        
        # Check if session already exists
        session, created = AttendanceSession.objects.get_or_create(
            class_assigned=class_obj,
            date=date,
            defaults={
                'term': Term.objects.filter(is_current=True).first().term if Term.objects.filter(is_current=True).exists() else None,
                'academic_year': AcademicYear.objects.filter(is_current=True).first(),
                'session_taken_by': teacher
            }
        )
        
        if created:
            # Create attendance records for all students
            students = Student.objects.filter(
                current_class=class_obj,
                enrollment_status='ACTIVE'
            )
            
            for student in students:
                Attendance.objects.create(
                    session=session,
                    student=student,
                    status='P'  # Default to present
                )
            
            messages.success(request, f"Attendance session created for {class_obj.name} on {date}")
        else:
            messages.info(request, f"Attendance session already exists for {class_obj.name} on {date}")
        
        return redirect('attendance:mark_attendance', session_id=session.id)
    
    context = {
        'classes_taught': classes_taught,
        'today': timezone.now().date(),
        'title': 'Take Attendance'
    }
    return render(request, 'attendance/teacher/select_class.html', context)

@login_required
@teacher_required
def mark_attendance(request, session_id):
    """Mark attendance for a specific session"""
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    # Check permission
    if session.session_taken_by != request.user and not SubjectAllocation.objects.filter(
        teacher=request.user,
        class_assigned=session.class_assigned
    ).exists() and session.class_assigned.class_teacher != request.user:
        messages.error(request, "You are not authorized to mark attendance for this class.")
        return redirect('attendance:take_attendance')
    
    if session.is_closed:
        messages.warning(request, "This attendance session is closed and cannot be edited.")
        return redirect('attendance:view_attendance', session_id=session.id)
    
    # Get attendance records
    attendances = Attendance.objects.filter(session=session).select_related('student__user')
    
    if request.method == 'POST':
        # Process attendance updates
        for attendance in attendances:
            status = request.POST.get(f'status_{attendance.id}')
            note = request.POST.get(f'note_{attendance.id}', '')
            
            if status:
                attendance.status = status
                attendance.note = note
                
                # Calculate minutes late if status is late
                if status == 'L':
                    time_in = request.POST.get(f'time_in_{attendance.id}')
                    if time_in:
                        # Parse time and calculate minutes late compared to school opening
                        # This is simplified - you'd need proper time comparison
                        attendance.minutes_late = 15  # Placeholder
                
                attendance.save()
        
        messages.success(request, "Attendance marked successfully.")
        
        # Check if this was the last action
        if 'save_and_close' in request.POST:
            session.is_closed = True
            session.save()
            messages.success(request, "Attendance session closed.")
            return redirect('attendance:attendance_history')
        
        return redirect('attendance:mark_attendance', session_id=session.id)
    
    context = {
        'session': session,
        'attendances': attendances,
        'title': f'Mark Attendance - {session.class_assigned.name} - {session.date}'
    }
    return render(request, 'attendance/teacher/mark_attendance.html', context)

@login_required
def view_attendance(request, session_id):
    """View attendance for a session"""
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    # Check permission
    user = request.user
    if user.role == 'STUDENT':
        # Students can only see their own attendance
        attendance = get_object_or_404(Attendance, session=session, student__user=user)
        return redirect('attendance:student_attendance')
    elif user.role == 'PARENT':
        # Parents can see their children's attendance
        children = user.parent_profile.children.all()
        attendances = Attendance.objects.filter(
            session=session,
            student__in=children
        ).select_related('student__user')
    else:
        # Teachers and admins can see all
        attendances = Attendance.objects.filter(session=session).select_related('student__user')
    
    context = {
        'session': session,
        'attendances': attendances if 'attendances' in locals() else [],
        'title': f'Attendance - {session.class_assigned.name} - {session.date}'
    }
    return render(request, 'attendance/view_attendance.html', context)

@login_required
def attendance_history(request):
    """View attendance history"""
    user = request.user
    
    if user.role == 'STUDENT':
        student = user.student_profile
        attendances = Attendance.objects.filter(
            student=student
        ).select_related('session__class_assigned').order_by('-session__date')
        
        context = {
            'attendances': attendances,
            'title': 'My Attendance History'
        }
        return render(request, 'attendance/student/history.html', context)
    
    elif user.role == 'PARENT':
        parent = user.parent_profile
        children = parent.children.all()
        
        # Get attendance for all children
        attendances = Attendance.objects.filter(
            student__in=children
        ).select_related('student__user', 'session__class_assigned').order_by('-session__date')
        
        # Group by child
        children_data = []
        for child in children:
            child_attendance = attendances.filter(student=child)
            total_days = child_attendance.count()
            present_days = child_attendance.filter(status='P').count()
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            children_data.append({
                'child': child,
                'attendance': child_attendance[:20],  # Last 20 records
                'total_days': total_days,
                'present_days': present_days,
                'attendance_percentage': attendance_percentage
            })
        
        context = {
            'children_data': children_data,
            'title': 'Children Attendance History'
        }
        return render(request, 'attendance/parent/history.html', context)
    
    else:
        # Teachers and admins
        # Get classes taught by this teacher
        if user.role == 'TEACHER':
            classes = Class.objects.filter(
                Q(subject_allocations__teacher=user) |
                Q(class_teacher=user),
                status='ACTIVE'
            ).distinct()
        else:
            classes = Class.objects.filter(status='ACTIVE')
        
        # Get recent sessions
        recent_sessions = AttendanceSession.objects.filter(
            class_assigned__in=classes
        ).select_related('class_assigned', 'session_taken_by').order_by('-date')[:50]
        
        context = {
            'recent_sessions': recent_sessions,
            'classes': classes,
            'title': 'Attendance History'
        }
        return render(request, 'attendance/teacher/history.html', context)

# Attendance Reports
@login_required
@principal_required
def attendance_report(request):
    """Generate attendance reports"""
    if request.method == 'POST':
        form = AttendanceReportForm(request.POST)
        if form.is_valid():
            class_assigned = form.cleaned_data['class_assigned']
            term = form.cleaned_data['term']
            academic_year = form.cleaned_data['academic_year']
            report_type = form.cleaned_data['report_type']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Get sessions within date range
            sessions = AttendanceSession.objects.filter(
                class_assigned=class_assigned,
                date__range=[start_date, end_date] if start_date and end_date else None
            )
            
            # Get all students in class
            students = Student.objects.filter(
                current_class=class_assigned,
                enrollment_status='ACTIVE'
            ).select_related('user')
            
            # Calculate attendance statistics
            report_data = []
            for student in students:
                attendances = Attendance.objects.filter(
                    student=student,
                    session__in=sessions
                )
                
                total_days = attendances.count()
                present_days = attendances.filter(status='P').count()
                absent_days = attendances.filter(status='A').count()
                late_days = attendances.filter(status='L').count()
                
                attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
                
                report_data.append({
                    'student': student,
                    'total_days': total_days,
                    'present_days': present_days,
                    'absent_days': absent_days,
                    'late_days': late_days,
                    'attendance_percentage': attendance_percentage
                })
            
            # Generate CSV if requested
            if 'export_csv' in request.POST:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="attendance_report_{class_assigned.name}_{term}.csv"'
                
                writer = csv.writer(response)
                writer.writerow(['Student Name', 'Admission Number', 'Total Days', 'Present', 'Absent', 'Late', 'Percentage'])
                
                for data in report_data:
                    writer.writerow([
                        data['student'].user.get_full_name(),
                        data['student'].admission_number,
                        data['total_days'],
                        data['present_days'],
                        data['absent_days'],
                        data['late_days'],
                        f"{data['attendance_percentage']:.2f}%"
                    ])
                
                return response
            
            context = {
                'form': form,
                'class_assigned': class_assigned,
                'term': term,
                'academic_year': academic_year,
                'report_data': report_data,
                'sessions': sessions,
                'title': 'Attendance Report'
            }
            return render(request, 'attendance/report_results.html', context)
    else:
        form = AttendanceReportForm()
    
    context = {
        'form': form,
        'title': 'Generate Attendance Report'
    }
    return render(request, 'attendance/report_form.html', context)

# API Views
@login_required
def get_attendance_summary(request, student_id):
    """API endpoint to get attendance summary for a student"""
    student = get_object_or_404(Student, id=student_id)
    
    # Check permission
    user = request.user
    if user.role == 'STUDENT' and student.user != user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    elif user.role == 'PARENT' and student not in user.parent_profile.children.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Get current term
    current_term = Term.objects.filter(is_current=True).first()
    
    if current_term:
        attendance = Attendance.objects.filter(
            student=student,
            session__term=current_term.term,
            session__academic_year__is_current=True
        )
        
        total_days = attendance.count()
        present_days = attendance.filter(status='P').count()
        absent_days = attendance.filter(status='A').count()
        late_days = attendance.filter(status='L').count()
        
        return JsonResponse({
            'student_name': student.user.get_full_name(),
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'attendance_percentage': (present_days / total_days * 100) if total_days > 0 else 0
        })
    
    return JsonResponse({'error': 'No current term found'}, status=404)

@login_required
def close_attendance_session(request, session_id):
    """API endpoint to close an attendance session"""
    if request.method == 'POST':
        session = get_object_or_404(AttendanceSession, id=session_id)
        
        # Check permission
        if session.session_taken_by != request.user and request.user.role not in ['SUPER_ADMIN', 'ADMIN', 'PRINCIPAL']:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        session.is_closed = True
        session.closed_by = request.user
        session.closed_at = timezone.now()
        session.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
