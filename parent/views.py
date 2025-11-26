"""
Parent App Views - Multi-Tenant SaaS Platform
Views for parent portal (10 pages)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count, Avg, Q, Sum
from core.decorators import role_required
from core.models import Section, Subject, AcademicYear, ParentStudentLink
from teacher.models import Attendance, Assignment, Grade
from college_management.models import Timetable, ExamSchedule, Announcement
from student.models import FeePayment
from .models import ParentCommunication


@login_required
@role_required(['parent'])
def dashboard(request):
    """Parent dashboard with overview of all children"""
    parent = request.user
    
    # Get all children
    children_links = ParentStudentLink.objects.filter(parent=parent).select_related('student')
    children = [link.student for link in children_links]
    
    # Aggregate stats for all children
    total_pending_fees = 0
    total_pending_assignments = 0
    children_data = []
    
    for child in children:
        # Get section
        section = Section.objects.filter(students=child, academic_year__is_active=True).first()
        
        # Attendance
        attendance_stats = Attendance.objects.filter(student=child, section=section).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present'))
        )
        attendance_percentage = 0
        if attendance_stats['total'] > 0:
            attendance_percentage = (attendance_stats['present'] / attendance_stats['total']) * 100
        
        # Grades average
        avg_percentage = Grade.objects.filter(
            student=child,
            is_published=True
        ).aggregate(avg=Avg('percentage'))['avg'] or 0
        
        # Pending assignments
        pending_assignments = Assignment.objects.filter(
            section=section,
            status='published',
            due_date__gte=timezone.now().date()
        ).exclude(
            assignmentsubmission__student=child
        ).count()
        total_pending_assignments += pending_assignments
        
        # Pending fees
        pending_fees = FeePayment.objects.filter(
            student=child,
            status__in=['pending', 'overdue']
        ).aggregate(total=Sum('amount'))['total'] or 0
        total_pending_fees += pending_fees
        
        children_data.append({
            'student': child,
            'section': section,
            'attendance_percentage': round(attendance_percentage, 2),
            'avg_percentage': round(avg_percentage, 2),
            'pending_assignments': pending_assignments,
            'pending_fees': pending_fees,
        })
    
    # Recent communications
    recent_communications = ParentCommunication.objects.filter(
        parent=parent
    ).order_by('-created_at')[:5]
    
    context = {
        'children_data': children_data,
        'total_children': len(children),
        'total_pending_fees': total_pending_fees,
        'total_pending_assignments': total_pending_assignments,
        'recent_communications': recent_communications,
    }
    return render(request, 'parent/dashboard.html', context)


@login_required
@role_required(['parent'])
def child_performance(request, student_id):
    """Detailed performance view for a specific child"""
    parent = request.user
    
    # Verify parent-child relationship
    link = get_object_or_404(ParentStudentLink, parent=parent, student_id=student_id)
    child = link.student
    
    # Get section
    section = Section.objects.filter(students=child, academic_year__is_active=True).first()
    
    # Recent grades
    recent_grades = Grade.objects.filter(
        student=child,
        is_published=True
    ).order_by('-exam_date')[:10]
    
    # Average performance
    avg_percentage = Grade.objects.filter(
        student=child,
        is_published=True
    ).aggregate(avg=Avg('percentage'))['avg'] or 0
    
    # Assignment completion rate
    total_assignments = Assignment.objects.filter(
        section=section,
        status='published'
    ).count()
    
    completed_assignments = Assignment.objects.filter(
        section=section,
        status='published',
        assignmentsubmission__student=child
    ).count()
    
    completion_rate = 0
    if total_assignments > 0:
        completion_rate = (completed_assignments / total_assignments) * 100
    
    context = {
        'child': child,
        'section': section,
        'recent_grades': recent_grades,
        'avg_percentage': round(avg_percentage, 2),
        'completion_rate': round(completion_rate, 2),
        'total_assignments': total_assignments,
        'completed_assignments': completed_assignments,
    }
    return render(request, 'parent/child_performance.html', context)


@login_required
@role_required(['parent'])
def attendance_tracking(request, student_id):
    """View attendance records for a child"""
    parent = request.user
    
    # Verify parent-child relationship
    link = get_object_or_404(ParentStudentLink, parent=parent, student_id=student_id)
    child = link.student
    
    # Get section
    section = Section.objects.filter(students=child, academic_year__is_active=True).first()
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(
        student=child,
        section=section
    ).order_by('-date')
    
    # Paginate
    paginator = Paginator(attendance_records, 50)
    page_number = request.GET.get('page')
    attendances = paginator.get_page(page_number)
    
    # Calculate stats
    attendance_stats = Attendance.objects.filter(student=child, section=section).aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late'))
    )
    
    attendance_percentage = 0
    if attendance_stats['total'] > 0:
        attendance_percentage = (attendance_stats['present'] / attendance_stats['total']) * 100
    
    context = {
        'child': child,
        'section': section,
        'attendances': attendances,
        'attendance_stats': attendance_stats,
        'attendance_percentage': round(attendance_percentage, 2),
    }
    return render(request, 'parent/attendance_tracking.html', context)


@login_required
@role_required(['parent'])
def grades_view(request, student_id):
    """View grades for a child"""
    parent = request.user
    
    # Verify parent-child relationship
    link = get_object_or_404(ParentStudentLink, parent=parent, student_id=student_id)
    child = link.student
    
    # Get published grades
    grade_list = Grade.objects.filter(
        student=child,
        is_published=True
    ).order_by('-exam_date')
    
    # Paginate
    paginator = Paginator(grade_list, 50)
    page_number = request.GET.get('page')
    grades = paginator.get_page(page_number)
    
    # Calculate average
    avg_percentage = Grade.objects.filter(
        student=child,
        is_published=True
    ).aggregate(avg=Avg('percentage'))['avg'] or 0
    
    context = {
        'child': child,
        'grades': grades,
        'avg_percentage': round(avg_percentage, 2),
    }
    return render(request, 'parent/grades_view.html', context)


@login_required
@role_required(['parent'])
def fee_payments(request, student_id):
    """View fee payments for a child"""
    parent = request.user
    
    # Verify parent-child relationship
    link = get_object_or_404(ParentStudentLink, parent=parent, student_id=student_id)
    child = link.student
    
    # Get fee records
    fee_list = FeePayment.objects.filter(
        student=child
    ).order_by('-due_date')
    
    # Paginate
    paginator = Paginator(fee_list, 20)
    page_number = request.GET.get('page')
    fees = paginator.get_page(page_number)
    
    # Calculate totals
    total_paid = FeePayment.objects.filter(student=child, status='paid').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    total_pending = FeePayment.objects.filter(
        student=child, 
        status__in=['pending', 'overdue']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'child': child,
        'fees': fees,
        'total_paid': total_paid,
        'total_pending': total_pending,
    }
    return render(request, 'parent/fee_payments.html', context)


@login_required
@role_required(['parent'])
def announcements(request):
    """View announcements for children's sections"""
    parent = request.user
    
    # Get all children's sections
    children_links = ParentStudentLink.objects.filter(parent=parent).select_related('student')
    sections = []
    for link in children_links:
        section = Section.objects.filter(students=link.student, academic_year__is_active=True).first()
        if section:
            sections.append(section)
    
    # Get announcements for these sections
    announcement_list = Announcement.objects.filter(
        Q(target_sections__in=sections) | Q(target_sections__isnull=True),
        is_active=True
    ).distinct().order_by('-created_at')
    
    # Paginate
    paginator = Paginator(announcement_list, 20)
    page_number = request.GET.get('page')
    announcements = paginator.get_page(page_number)
    
    context = {
        'announcements': announcements,
    }
    return render(request, 'parent/announcements.html', context)


@login_required
@role_required(['parent'])
def communication(request):
    """Communication with teachers"""
    parent = request.user
    
    if request.method == 'POST':
        # Create new communication
        student_id = request.POST.get('student')
        teacher_id = request.POST.get('teacher')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        message_type = request.POST.get('message_type', 'inquiry')
        priority = request.POST.get('priority', 'medium')
        
        # Verify parent-child relationship
        if ParentStudentLink.objects.filter(parent=parent, student_id=student_id).exists():
            ParentCommunication.objects.create(
                parent=parent,
                student_id=student_id,
                teacher_id=teacher_id if teacher_id else None,
                subject=subject,
                message=message,
                message_type=message_type,
                priority=priority,
                status='sent'
            )
            return redirect('parent:communication')
    
    # Get communications
    communication_list = ParentCommunication.objects.filter(
        parent=parent
    ).order_by('-created_at')
    
    # Paginate
    paginator = Paginator(communication_list, 20)
    page_number = request.GET.get('page')
    communications = paginator.get_page(page_number)
    
    # Get children for form
    children_links = ParentStudentLink.objects.filter(parent=parent).select_related('student')
    children = [link.student for link in children_links]
    
    context = {
        'communications': communications,
        'children': children,
    }
    return render(request, 'parent/communication.html', context)


@login_required
@role_required(['parent'])
def exam_schedules(request, student_id):
    """View exam schedules for a child"""
    parent = request.user
    
    # Verify parent-child relationship
    link = get_object_or_404(ParentStudentLink, parent=parent, student_id=student_id)
    child = link.student
    
    # Get section
    section = Section.objects.filter(students=child, academic_year__is_active=True).first()
    
    # Get published exams
    exams = ExamSchedule.objects.filter(
        section=section,
        is_published=True
    ).order_by('-start_date')
    
    context = {
        'child': child,
        'section': section,
        'exams': exams,
    }
    return render(request, 'parent/exam_schedules.html', context)


@login_required
@role_required(['parent'])
def timetable(request, student_id):
    """View timetable for a child"""
    parent = request.user
    
    # Verify parent-child relationship
    link = get_object_or_404(ParentStudentLink, parent=parent, student_id=student_id)
    child = link.student
    
    # Get section
    section = Section.objects.filter(students=child, academic_year__is_active=True).first()
    
    # Get timetable
    timetable_entries = Timetable.objects.filter(
        section=section,
        academic_year__is_active=True
    ).order_by('day_of_week', 'period_number')
    
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    periods = range(1, 9)  # 8 periods
    
    context = {
        'child': child,
        'section': section,
        'timetable': timetable_entries,
        'days': days,
        'periods': periods,
    }
    return render(request, 'parent/timetable.html', context)


@login_required
@role_required(['parent'])
def reports(request):
    """Generate reports for children (placeholder)"""
    parent = request.user
    
    # Get all children
    children_links = ParentStudentLink.objects.filter(parent=parent).select_related('student')
    children = [link.student for link in children_links]
    
    context = {
        'children': children,
    }
    return render(request, 'parent/reports.html', context)
