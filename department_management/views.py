"""
Department Management Views
HOD (Head of Department) Interface
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta

from core.models import Department, UserAccount, Section, Subject, AcademicYear
from core.decorators import role_required
from .models import DepartmentAnnouncement, FacultyMeeting, DepartmentResource, DepartmentSettings


@login_required
@role_required(['department_admin'])
def dashboard(request):
    """
    HOD dashboard with department overview
    """
    # Get user's department
    user = request.user
    department = user.department if hasattr(user, 'department') else None
    
    if not department:
        messages.error(request, 'You are not assigned to any department.')
        return redirect('/')
    
    # Faculty count
    faculty_count = UserAccount.objects.filter(
        tenant=user.tenant,
        role__name='teacher',
        is_active=True,
        is_deleted=False
    ).filter(
        Q(teaching_subjects__department=department)
    ).distinct().count()
    
    # Student count
    from core.models import StudentEnrollment
    student_count = StudentEnrollment.objects.filter(
        section__department=department,
        is_deleted=False
    ).values('student').distinct().count()
    
    # Section count
    section_count = Section.objects.filter(
        department=department,
        is_deleted=False
    ).count()
    
    # Subject count
    subject_count = Subject.objects.filter(
        department=department,
        is_deleted=False
    ).count()
    
    # Recent announcements
    recent_announcements = DepartmentAnnouncement.objects.filter(
        department=department,
        is_active=True
    ).order_by('-created_at')[:5]
    
    # Upcoming meetings
    upcoming_meetings = FacultyMeeting.objects.filter(
        department=department,
        meeting_date__gte=timezone.now().date(),
        status='scheduled'
    ).order_by('meeting_date', 'start_time')[:5]
    
    context = {
        'department': department,
        'faculty_count': faculty_count,
        'student_count': student_count,
        'section_count': section_count,
        'subject_count': subject_count,
        'recent_announcements': recent_announcements,
        'upcoming_meetings': upcoming_meetings,
    }
    
    return render(request, 'department_management/dashboard.html', context)


@login_required
@role_required(['department_admin'])
def faculty_list(request):
    """
    List all faculty in the department
    """
    department = request.user.department if hasattr(request.user, 'department') else None
    
    if not department:
        messages.error(request, 'You are not assigned to any department.')
        return redirect('department_management:dashboard')
    
    faculty = UserAccount.objects.filter(
        tenant=request.user.tenant,
        role__name='teacher',
        is_active=True,
        is_deleted=False
    ).filter(
        Q(teaching_subjects__department=department)
    ).distinct().order_by('first_name', 'last_name')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        faculty = faculty.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(faculty, 20)
    page = request.GET.get('page', 1)
    faculty_page = paginator.get_page(page)
    
    context = {
        'department': department,
        'faculty': faculty_page,
        'search': search,
    }
    
    return render(request, 'department_management/faculty_list.html', context)


@login_required
@role_required(['department_admin'])
def students_list(request):
    """
    List all students in the department
    """
    department = request.user.department if hasattr(request.user, 'department') else None
    
    if not department:
        messages.error(request, 'You are not assigned to any department.')
        return redirect('department_management:dashboard')
    
    from core.models import StudentEnrollment
    enrollments = StudentEnrollment.objects.filter(
        section__department=department,
        is_deleted=False
    ).select_related('student', 'section').order_by('section__name', 'roll_number')
    
    # Filters
    section_filter = request.GET.get('section', '')
    if section_filter:
        enrollments = enrollments.filter(section_id=section_filter)
    
    search = request.GET.get('search', '')
    if search:
        enrollments = enrollments.filter(
            Q(student__first_name__icontains=search) |
            Q(student__last_name__icontains=search) |
            Q(student__email__icontains=search) |
            Q(roll_number__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(enrollments, 50)
    page = request.GET.get('page', 1)
    enrollments_page = paginator.get_page(page)
    
    # Sections for filter
    sections = Section.objects.filter(
        department=department,
        is_deleted=False
    ).order_by('name')
    
    context = {
        'department': department,
        'enrollments': enrollments_page,
        'sections': sections,
        'section_filter': section_filter,
        'search': search,
    }
    
    return render(request, 'department_management/students_list.html', context)


@login_required
@role_required(['department_admin'])
def attendance_overview(request):
    """
    Department-wide attendance overview
    """
    department = request.user.department if hasattr(request.user, 'department') else None
    
    if not department:
        messages.error(request, 'You are not assigned to any department.')
        return redirect('department_management:dashboard')
    
    context = {
        'department': department,
    }
    
    return render(request, 'department_management/attendance_overview.html', context)


@login_required
@role_required(['department_admin'])
def exam_results(request):
    """
    Department exam results overview
    """
    department = request.user.department if hasattr(request.user, 'department') else None
    
    if not department:
        messages.error(request, 'You are not assigned to any department.')
        return redirect('department_management:dashboard')
    
    from college_management.models import ExamSchedule
    exams = ExamSchedule.objects.filter(
        department=department,
        is_published=True
    ).order_by('-start_date')[:10]
    
    context = {
        'department': department,
        'exams': exams,
    }
    
    return render(request, 'department_management/exam_results.html', context)


@login_required
@role_required(['department_admin'])
def timetable(request):
    """
    Department timetable view
    """
    department = request.user.department if hasattr(request.user, 'department') else None
    
    if not department:
        messages.error(request, 'You are not assigned to any department.')
        return redirect('department_management:dashboard')
    
    from college_management.models import Timetable
    current_academic_year = AcademicYear.objects.filter(
        tenant=request.user.tenant,
        is_active=True
    ).first()
    
    timetable_entries = []
    if current_academic_year:
        timetable_entries = Timetable.objects.filter(
            section__department=department,
            academic_year=current_academic_year
        ).select_related('section', 'subject', 'teacher').order_by('section__name', 'day_of_week', 'period_number')
    
    context = {
        'department': department,
        'timetable_entries': timetable_entries,
        'current_academic_year': current_academic_year,
    }
    
    return render(request, 'department_management/timetable.html', context)


@login_required
@role_required(['department_admin'])
def subject_management(request):
    """
    Manage department subjects
    """
    department = request.user.department if hasattr(request.user, 'department') else None
    
    if not department:
        messages.error(request, 'You are not assigned to any department.')
        return redirect('department_management:dashboard')
    
    subjects = Subject.objects.filter(
        department=department,
        is_deleted=False
    ).order_by('name')
    
    context = {
        'department': department,
        'subjects': subjects,
    }
    
    return render(request, 'department_management/subject_management.html', context)


@login_required
@role_required(['department_admin'])
def announcements(request):
    """
    Department announcements
    """
    department = request.user.department if hasattr(request.user, 'department') else None
    
    if not department:
        messages.error(request, 'You are not assigned to any department.')
        return redirect('department_management:dashboard')
    
    announcements_list = DepartmentAnnouncement.objects.filter(
        department=department,
        is_active=True
    ).order_by('-is_pinned', '-priority', '-created_at')
    
    # Pagination
    paginator = Paginator(announcements_list, 20)
    page = request.GET.get('page', 1)
    announcements_page = paginator.get_page(page)
    
    context = {
        'department': department,
        'announcements': announcements_page,
    }
    
    return render(request, 'department_management/announcements.html', context)


@login_required
@role_required(['department_admin'])
def announcement_create(request):
    """
    Create department announcement
    """
    department = request.user.department if hasattr(request.user, 'department') else None
    
    if not department:
        messages.error(request, 'You are not assigned to any department.')
        return redirect('department_management:dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        announcement_type = request.POST.get('announcement_type')
        target_audience = request.POST.get('target_audience', 'all')
        is_pinned = request.POST.get('is_pinned') == 'on'
        priority = request.POST.get('priority', 3)
        
        DepartmentAnnouncement.objects.create(
            tenant=request.user.tenant,
            department=department,
            created_by=request.user,
            title=title,
            content=content,
            announcement_type=announcement_type,
            target_audience=target_audience,
            is_pinned=is_pinned,
            priority=int(priority)
        )
        
        messages.success(request, 'Announcement created successfully.')
        return redirect('department_management:announcements')
    
    context = {
        'department': department,
    }
    
    return render(request, 'department_management/announcement_form.html', context)


@login_required
@role_required(['department_admin'])
def reports(request):
    """
    Department reports
    """
    department = request.user.department if hasattr(request.user, 'department') else None
    
    if not department:
        messages.error(request, 'You are not assigned to any department.')
        return redirect('department_management:dashboard')
    
    context = {
        'department': department,
    }
    
    return render(request, 'department_management/reports.html', context)


@login_required
@role_required(['department_admin'])
def settings(request):
    """
    Department settings
    """
    department = request.user.department if hasattr(request.user, 'department') else None
    
    if not department:
        messages.error(request, 'You are not assigned to any department.')
        return redirect('department_management:dashboard')
    
    dept_settings, created = DepartmentSettings.objects.get_or_create(
        tenant=request.user.tenant,
        department=department
    )
    
    if request.method == 'POST':
        dept_settings.minimum_attendance_percentage = request.POST.get('minimum_attendance_percentage')
        dept_settings.passing_marks_percentage = request.POST.get('passing_marks_percentage')
        dept_settings.max_lectures_per_day = request.POST.get('max_lectures_per_day')
        dept_settings.class_duration_minutes = request.POST.get('class_duration_minutes')
        dept_settings.enable_absence_alerts = request.POST.get('enable_absence_alerts') == 'on'
        dept_settings.enable_low_performance_alerts = request.POST.get('enable_low_performance_alerts') == 'on'
        dept_settings.performance_alert_threshold = request.POST.get('performance_alert_threshold')
        dept_settings.save()
        
        messages.success(request, 'Settings updated successfully.')
        return redirect('department_management:settings')
    
    context = {
        'department': department,
        'settings': dept_settings,
    }
    
    return render(request, 'department_management/settings.html', context)
