"""
Student App Views - Multi-Tenant SaaS Platform
Views for student portal (12 pages)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count, Avg, Q, Sum
from core.decorators import role_required
from core.models import Section, Subject, AcademicYear, Announcement
from teacher.models import Attendance, Assignment, AssignmentSubmission, Grade, TeacherResource
from college_management.models import Timetable, ExamSchedule, Holiday
from .models import StudentNote, StudentResource, LibraryTransaction, FeePayment


@login_required
@role_required(['student'])
def dashboard(request):
    """Student dashboard with overview"""
    student = request.user
    
    # Get student's section
    try:
        section = Section.objects.get(students=student, academic_year__is_active=True)
    except Section.DoesNotExist:
        section = None
    
    # Today's classes
    today = timezone.now().date()
    day_of_week = today.strftime('%A').lower()
    todays_classes = []
    if section:
        todays_classes = Timetable.objects.filter(
            section=section,
            day_of_week=day_of_week,
            academic_year__is_active=True
        ).order_by('period_number')
    
    # Pending assignments
    pending_assignments = Assignment.objects.filter(
        section=section,
        status='published',
        due_date__gte=today
    ).exclude(
        assignmentsubmission__student=student
    ).order_by('due_date')[:5]
    
    # Recent grades
    recent_grades = Grade.objects.filter(
        student=student,
        is_published=True
    ).order_by('-exam_date')[:5]
    
    # Attendance stats
    attendance_stats = Attendance.objects.filter(
        student=student,
        section=section
    ).aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent'))
    )
    
    attendance_percentage = 0
    if attendance_stats['total'] > 0:
        attendance_percentage = (attendance_stats['present'] / attendance_stats['total']) * 100
    
    # Pending fees
    pending_fees = FeePayment.objects.filter(
        student=student,
        status__in=['pending', 'overdue']
    ).order_by('due_date')[:3]
    
    context = {
        'section': section,
        'todays_classes': todays_classes,
        'pending_assignments': pending_assignments,
        'recent_grades': recent_grades,
        'attendance_percentage': round(attendance_percentage, 2),
        'pending_fees': pending_fees,
    }
    return render(request, 'student/dashboard.html', context)


@login_required
@role_required(['student'])
def attendance_view(request):
    """View attendance records"""
    student = request.user
    
    # Get section
    section = Section.objects.filter(students=student, academic_year__is_active=True).first()
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(
        student=student,
        section=section
    ).order_by('-date')
    
    # Paginate
    paginator = Paginator(attendance_records, 50)
    page_number = request.GET.get('page')
    attendances = paginator.get_page(page_number)
    
    context = {
        'attendances': attendances,
        'section': section,
    }
    return render(request, 'student/attendance.html', context)


@login_required
@role_required(['student'])
def grades(request):
    """View grades and marks"""
    student = request.user
    
    # Get published grades
    grade_list = Grade.objects.filter(
        student=student,
        is_published=True
    ).order_by('-exam_date')
    
    # Paginate
    paginator = Paginator(grade_list, 50)
    page_number = request.GET.get('page')
    grades = paginator.get_page(page_number)
    
    # Calculate average
    avg_percentage = Grade.objects.filter(
        student=student,
        is_published=True
    ).aggregate(avg=Avg('percentage'))['avg'] or 0
    
    context = {
        'grades': grades,
        'avg_percentage': round(avg_percentage, 2),
    }
    return render(request, 'student/grades.html', context)


@login_required
@role_required(['student'])
def assignments(request):
    """View all assignments"""
    student = request.user
    section = Section.objects.filter(students=student, academic_year__is_active=True).first()
    
    # Get assignments for student's section
    assignment_list = Assignment.objects.filter(
        section=section,
        status='published'
    ).order_by('-due_date')
    
    # Paginate
    paginator = Paginator(assignment_list, 20)
    page_number = request.GET.get('page')
    assignments = paginator.get_page(page_number)
    
    context = {
        'assignments': assignments,
        'section': section,
    }
    return render(request, 'student/assignments.html', context)


@login_required
@role_required(['student'])
def assignment_detail(request, assignment_id):
    """View assignment details and submit"""
    student = request.user
    assignment = get_object_or_404(Assignment, id=assignment_id, status='published')
    
    # Check if already submitted
    submission = AssignmentSubmission.objects.filter(
        assignment=assignment,
        student=student
    ).first()
    
    if request.method == 'POST' and not submission:
        # Handle submission
        file = request.FILES.get('file')
        remarks = request.POST.get('remarks', '')
        
        AssignmentSubmission.objects.create(
            assignment=assignment,
            student=student,
            attachment=file,
            submission_date=timezone.now(),
            is_late=timezone.now().date() > assignment.due_date,
            status='submitted'
        )
        return redirect('student:assignments')
    
    context = {
        'assignment': assignment,
        'submission': submission,
    }
    return render(request, 'student/assignment_detail.html', context)


@login_required
@role_required(['student'])
def exam_schedule(request):
    """View exam schedules"""
    student = request.user
    section = Section.objects.filter(students=student, academic_year__is_active=True).first()
    
    # Get published exams
    exams = ExamSchedule.objects.filter(
        section=section,
        is_published=True
    ).order_by('-start_date')
    
    context = {
        'exams': exams,
        'section': section,
    }
    return render(request, 'student/exam_schedule.html', context)


@login_required
@role_required(['student'])
def timetable(request):
    """View weekly timetable"""
    student = request.user
    section = Section.objects.filter(students=student, academic_year__is_active=True).first()
    
    # Get timetable
    timetable_entries = Timetable.objects.filter(
        section=section,
        academic_year__is_active=True
    ).order_by('day_of_week', 'period_number')
    
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    periods = range(1, 9)  # 8 periods
    
    context = {
        'timetable': timetable_entries,
        'section': section,
        'days': days,
        'periods': periods,
    }
    return render(request, 'student/timetable.html', context)


@login_required
@role_required(['student'])
def announcements(request):
    """View announcements"""
    student = request.user
    section = Section.objects.filter(students=student, academic_year__is_active=True).first()
    
    # Get announcements for section/college
    announcement_list = Announcement.objects.filter(
        Q(target_sections=section) | Q(target_sections__isnull=True),
        is_active=True
    ).order_by('-created_at')
    
    # Paginate
    paginator = Paginator(announcement_list, 20)
    page_number = request.GET.get('page')
    announcements = paginator.get_page(page_number)
    
    context = {
        'announcements': announcements,
    }
    return render(request, 'student/announcements.html', context)


@login_required
@role_required(['student'])
def resources(request):
    """View and download resources"""
    student = request.user
    section = Section.objects.filter(students=student, academic_year__is_active=True).first()
    
    # Get teacher resources (public or for student's section)
    resource_list = TeacherResource.objects.filter(
        Q(section=section) | Q(section__isnull=True),
        is_public=True
    ).order_by('-created_at')
    
    # Paginate
    paginator = Paginator(resource_list, 20)
    page_number = request.GET.get('page')
    resources = paginator.get_page(page_number)
    
    context = {
        'resources': resources,
    }
    return render(request, 'student/resources.html', context)


@login_required
@role_required(['student'])
def communication(request):
    """Communication portal (placeholder)"""
    return render(request, 'student/communication.html')


@login_required
@role_required(['student'])
def profile(request):
    """Student profile"""
    student = request.user
    section = Section.objects.filter(students=student, academic_year__is_active=True).first()
    
    context = {
        'section': section,
    }
    return render(request, 'student/profile.html', context)


@login_required
@role_required(['student'])
def fees(request):
    """View fee payments and dues"""
    student = request.user
    
    # Get fee records
    fee_list = FeePayment.objects.filter(
        student=student
    ).order_by('-due_date')
    
    # Paginate
    paginator = Paginator(fee_list, 20)
    page_number = request.GET.get('page')
    fees = paginator.get_page(page_number)
    
    # Calculate totals
    total_paid = FeePayment.objects.filter(student=student, status='paid').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    total_pending = FeePayment.objects.filter(
        student=student, 
        status__in=['pending', 'overdue']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'fees': fees,
        'total_paid': total_paid,
        'total_pending': total_pending,
    }
    return render(request, 'student/fees.html', context)
