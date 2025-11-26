"""
Views for college_management app
Tenant admin interface for college administrators
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta

from core.models import Tenant, UserAccount, Department, Section, AcademicYear, Subject
from core.decorators import role_required
from .models import (
    CollegeSettings,
    Holiday,
    Announcement,
    Timetable,
    ExamSchedule,
    ExamSlot
)


@login_required
@role_required(['tenant_admin'])
def dashboard(request):
    """
    Tenant admin dashboard with college overview
    """
    tenant = request.user.tenant
    
    # Get key metrics
    total_departments = Department.objects.filter(
        tenant=tenant,
        is_deleted=False
    ).count()
    
    total_sections = Section.objects.filter(
        tenant=tenant,
        is_deleted=False
    ).count()
    
    total_teachers = UserAccount.objects.filter(
        tenant=tenant,
        role__name='teacher',
        is_active=True,
        is_deleted=False
    ).count()
    
    total_students = UserAccount.objects.filter(
        tenant=tenant,
        role__name='student',
        is_active=True,
        is_deleted=False
    ).count()
    
    # Recent announcements
    recent_announcements = Announcement.objects.filter(
        tenant=tenant,
        is_active=True
    ).order_by('-created_at')[:5]
    
    # Upcoming holidays
    upcoming_holidays = Holiday.objects.filter(
        tenant=tenant,
        date__gte=timezone.now().date()
    ).order_by('date')[:5]
    
    # Active academic year
    current_academic_year = AcademicYear.objects.filter(
        tenant=tenant,
        is_active=True
    ).first()
    
    context = {
        'total_departments': total_departments,
        'total_sections': total_sections,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'recent_announcements': recent_announcements,
        'upcoming_holidays': upcoming_holidays,
        'current_academic_year': current_academic_year,
    }
    
    return render(request, 'college_management/dashboard.html', context)


@login_required
@role_required(['tenant_admin'])
def department_list(request):
    """
    List all departments
    """
    tenant = request.user.tenant
    
    departments = Department.objects.filter(
        tenant=tenant,
        is_deleted=False
    ).annotate(
        section_count=Count('sections')
    ).order_by('name')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        departments = departments.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(departments, 20)
    page = request.GET.get('page', 1)
    departments_page = paginator.get_page(page)
    
    context = {
        'departments': departments_page,
        'search': search,
    }
    
    return render(request, 'college_management/department_list.html', context)


@login_required
@role_required(['tenant_admin'])
def department_create(request):
    """
    Create new department
    """
    if request.method == 'POST':
        tenant = request.user.tenant
        
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        hod_id = request.POST.get('hod')
        
        # Check if department code already exists
        if Department.objects.filter(tenant=tenant, code=code, is_deleted=False).exists():
            messages.error(request, f'Department with code "{code}" already exists.')
            return redirect('college_management:department_create')
        
        department = Department.objects.create(
            tenant=tenant,
            name=name,
            code=code,
            description=description,
            hod_id=hod_id if hod_id else None
        )
        
        messages.success(request, f'Department "{name}" created successfully.')
        return redirect('college_management:department_detail', dept_id=department.id)
    
    # Get available HODs (teachers)
    teachers = UserAccount.objects.filter(
        tenant=request.user.tenant,
        role__name='teacher',
        is_active=True,
        is_deleted=False
    ).order_by('first_name', 'last_name')
    
    context = {
        'teachers': teachers,
    }
    
    return render(request, 'college_management/department_form.html', context)


@login_required
@role_required(['tenant_admin'])
def department_detail(request, dept_id):
    """
    Department details with sections, teachers, students
    """
    department = get_object_or_404(
        Department,
        id=dept_id,
        tenant=request.user.tenant,
        is_deleted=False
    )
    
    # Get sections
    sections = Section.objects.filter(
        department=department,
        is_deleted=False
    ).annotate(
        student_count=Count('student_enrollments')
    ).order_by('name')
    
    # Get teachers in this department
    teachers = UserAccount.objects.filter(
        tenant=request.user.tenant,
        role__name='teacher',
        is_active=True,
        is_deleted=False
    ).filter(
        Q(teaching_subjects__department=department)
    ).distinct()[:10]
    
    # Get subjects
    subjects = Subject.objects.filter(
        tenant=request.user.tenant,
        department=department,
        is_deleted=False
    ).order_by('name')
    
    context = {
        'department': department,
        'sections': sections,
        'teachers': teachers,
        'subjects': subjects,
    }
    
    return render(request, 'college_management/department_detail.html', context)


@login_required
@role_required(['tenant_admin'])
def department_edit(request, dept_id):
    """
    Edit department
    """
    department = get_object_or_404(
        Department,
        id=dept_id,
        tenant=request.user.tenant,
        is_deleted=False
    )
    
    if request.method == 'POST':
        department.name = request.POST.get('name')
        department.code = request.POST.get('code')
        department.description = request.POST.get('description', '')
        hod_id = request.POST.get('hod')
        department.hod_id = hod_id if hod_id else None
        department.save()
        
        messages.success(request, 'Department updated successfully.')
        return redirect('college_management:department_detail', dept_id=department.id)
    
    teachers = UserAccount.objects.filter(
        tenant=request.user.tenant,
        role__name='teacher',
        is_active=True,
        is_deleted=False
    ).order_by('first_name', 'last_name')
    
    context = {
        'department': department,
        'teachers': teachers,
        'is_edit': True,
    }
    
    return render(request, 'college_management/department_form.html', context)


@login_required
@role_required(['tenant_admin'])
def section_list(request):
    """
    List all sections
    """
    tenant = request.user.tenant
    
    sections = Section.objects.filter(
        tenant=tenant,
        is_deleted=False
    ).select_related('department', 'class_teacher').annotate(
        student_count=Count('student_enrollments')
    ).order_by('department__name', 'name')
    
    # Filters
    dept_filter = request.GET.get('department', '')
    if dept_filter:
        sections = sections.filter(department_id=dept_filter)
    
    # Pagination
    paginator = Paginator(sections, 20)
    page = request.GET.get('page', 1)
    sections_page = paginator.get_page(page)
    
    # For filter dropdown
    departments = Department.objects.filter(
        tenant=tenant,
        is_deleted=False
    ).order_by('name')
    
    context = {
        'sections': sections_page,
        'departments': departments,
        'dept_filter': dept_filter,
    }
    
    return render(request, 'college_management/section_list.html', context)


@login_required
@role_required(['tenant_admin'])
def section_create(request):
    """
    Create new section
    """
    if request.method == 'POST':
        tenant = request.user.tenant
        
        name = request.POST.get('name')
        department_id = request.POST.get('department')
        class_teacher_id = request.POST.get('class_teacher')
        capacity = request.POST.get('capacity', 60)
        
        section = Section.objects.create(
            tenant=tenant,
            name=name,
            department_id=department_id,
            class_teacher_id=class_teacher_id if class_teacher_id else None,
            capacity=int(capacity)
        )
        
        messages.success(request, f'Section "{name}" created successfully.')
        return redirect('college_management:section_detail', section_id=section.id)
    
    departments = Department.objects.filter(
        tenant=request.user.tenant,
        is_deleted=False
    ).order_by('name')
    
    teachers = UserAccount.objects.filter(
        tenant=request.user.tenant,
        role__name='teacher',
        is_active=True,
        is_deleted=False
    ).order_by('first_name', 'last_name')
    
    context = {
        'departments': departments,
        'teachers': teachers,
    }
    
    return render(request, 'college_management/section_form.html', context)


@login_required
@role_required(['tenant_admin'])
def section_detail(request, section_id):
    """
    Section details with students and timetable
    """
    section = get_object_or_404(
        Section,
        id=section_id,
        tenant=request.user.tenant,
        is_deleted=False
    )
    
    # Get students
    from core.models import StudentEnrollment
    enrollments = StudentEnrollment.objects.filter(
        section=section,
        is_deleted=False
    ).select_related('student').order_by('roll_number')[:50]
    
    # Get timetable for current week
    current_academic_year = AcademicYear.objects.filter(
        tenant=request.user.tenant,
        is_active=True
    ).first()
    
    timetable = []
    if current_academic_year:
        timetable = Timetable.objects.filter(
            section=section,
            academic_year=current_academic_year
        ).select_related('subject', 'teacher').order_by('day_of_week', 'period_number')
    
    context = {
        'section': section,
        'enrollments': enrollments,
        'student_count': enrollments.count(),
        'timetable': timetable,
    }
    
    return render(request, 'college_management/section_detail.html', context)


@login_required
@role_required(['tenant_admin'])
def user_list(request):
    """
    List all users (teachers, students, parents)
    """
    tenant = request.user.tenant
    
    users = UserAccount.objects.filter(
        tenant=tenant,
        is_deleted=False
    ).select_related('role').order_by('-created_at')
    
    # Filters
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    if role_filter:
        users = users.filter(role__name=role_filter)
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    users_page = paginator.get_page(page)
    
    context = {
        'users': users_page,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'search': search,
    }
    
    return render(request, 'college_management/user_list.html', context)


@login_required
@role_required(['tenant_admin'])
def user_create(request):
    """
    Create new user
    """
    if request.method == 'POST':
        # This would typically use a form
        # For now, placeholder
        messages.info(request, 'User creation form - To be implemented')
        return redirect('college_management:user_list')
    
    return render(request, 'college_management/user_form.html')


@login_required
@role_required(['tenant_admin'])
def user_detail(request, user_id):
    """
    User detail page
    """
    user = get_object_or_404(
        UserAccount,
        id=user_id,
        tenant=request.user.tenant,
        is_deleted=False
    )
    
    context = {
        'user_obj': user,
    }
    
    return render(request, 'college_management/user_detail.html', context)


@login_required
@role_required(['tenant_admin'])
def timetable_view(request):
    """
    View timetable for all sections
    """
    tenant = request.user.tenant
    
    # Get current academic year
    current_academic_year = AcademicYear.objects.filter(
        tenant=tenant,
        is_active=True
    ).first()
    
    # Get filter parameters
    section_id = request.GET.get('section')
    department_id = request.GET.get('department')
    
    timetable_entries = Timetable.objects.filter(
        tenant=tenant
    ).select_related('section', 'subject', 'teacher')
    
    if current_academic_year:
        timetable_entries = timetable_entries.filter(academic_year=current_academic_year)
    
    if section_id:
        timetable_entries = timetable_entries.filter(section_id=section_id)
    elif department_id:
        timetable_entries = timetable_entries.filter(section__department_id=department_id)
    
    timetable_entries = timetable_entries.order_by('day_of_week', 'period_number')
    
    # For filters
    departments = Department.objects.filter(tenant=tenant, is_deleted=False)
    sections = Section.objects.filter(tenant=tenant, is_deleted=False)
    
    context = {
        'timetable_entries': timetable_entries,
        'departments': departments,
        'sections': sections,
        'section_id': section_id,
        'department_id': department_id,
    }
    
    return render(request, 'college_management/timetable.html', context)


@login_required
@role_required(['tenant_admin'])
def timetable_create(request):
    """
    Create timetable entry
    """
    if request.method == 'POST':
        messages.info(request, 'Timetable creation - To be implemented')
        return redirect('college_management:timetable')
    
    return render(request, 'college_management/timetable_form.html')


@login_required
@role_required(['tenant_admin'])
def exam_list(request):
    """
    List all exam schedules
    """
    tenant = request.user.tenant
    
    exams = ExamSchedule.objects.filter(
        tenant=tenant
    ).select_related('academic_year', 'department').order_by('-start_date')
    
    # Pagination
    paginator = Paginator(exams, 20)
    page = request.GET.get('page', 1)
    exams_page = paginator.get_page(page)
    
    context = {
        'exams': exams_page,
    }
    
    return render(request, 'college_management/exam_list.html', context)


@login_required
@role_required(['tenant_admin'])
def exam_create(request):
    """
    Create exam schedule
    """
    if request.method == 'POST':
        messages.info(request, 'Exam creation - To be implemented')
        return redirect('college_management:exam_list')
    
    return render(request, 'college_management/exam_form.html')


@login_required
@role_required(['tenant_admin'])
def exam_detail(request, exam_id):
    """
    Exam schedule details with slots
    """
    exam = get_object_or_404(
        ExamSchedule,
        id=exam_id,
        tenant=request.user.tenant
    )
    
    # Get exam slots
    exam_slots = ExamSlot.objects.filter(
        exam_schedule=exam
    ).select_related('subject', 'section').order_by('exam_date', 'start_time')
    
    context = {
        'exam': exam,
        'exam_slots': exam_slots,
    }
    
    return render(request, 'college_management/exam_detail.html', context)


@login_required
@role_required(['tenant_admin'])
def announcement_list(request):
    """
    List all announcements
    """
    tenant = request.user.tenant
    
    announcements = Announcement.objects.filter(
        tenant=tenant
    ).select_related('created_by').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(announcements, 20)
    page = request.GET.get('page', 1)
    announcements_page = paginator.get_page(page)
    
    context = {
        'announcements': announcements_page,
    }
    
    return render(request, 'college_management/announcement_list.html', context)


@login_required
@role_required(['tenant_admin'])
def announcement_create(request):
    """
    Create announcement
    """
    if request.method == 'POST':
        tenant = request.user.tenant
        
        title = request.POST.get('title')
        content = request.POST.get('content')
        announcement_type = request.POST.get('announcement_type')
        target_audience = request.POST.get('target_audience', 'all')
        
        announcement = Announcement.objects.create(
            tenant=tenant,
            created_by=request.user,
            title=title,
            content=content,
            announcement_type=announcement_type,
            target_audience=target_audience
        )
        
        messages.success(request, 'Announcement created successfully.')
        return redirect('college_management:announcement_list')
    
    return render(request, 'college_management/announcement_form.html')


@login_required
@role_required(['tenant_admin'])
def announcement_edit(request, announcement_id):
    """
    Edit announcement
    """
    announcement = get_object_or_404(
        Announcement,
        id=announcement_id,
        tenant=request.user.tenant
    )
    
    if request.method == 'POST':
        announcement.title = request.POST.get('title')
        announcement.content = request.POST.get('content')
        announcement.announcement_type = request.POST.get('announcement_type')
        announcement.target_audience = request.POST.get('target_audience', 'all')
        announcement.save()
        
        messages.success(request, 'Announcement updated successfully.')
        return redirect('college_management:announcement_list')
    
    context = {
        'announcement': announcement,
        'is_edit': True,
    }
    
    return render(request, 'college_management/announcement_form.html', context)


@login_required
@role_required(['tenant_admin'])
def reports_dashboard(request):
    """
    Reports dashboard
    """
    return render(request, 'college_management/reports_dashboard.html')


@login_required
@role_required(['tenant_admin'])
def attendance_report(request):
    """
    Attendance report
    """
    return render(request, 'college_management/attendance_report.html')


@login_required
@role_required(['tenant_admin'])
def academic_report(request):
    """
    Academic performance report
    """
    return render(request, 'college_management/academic_report.html')


@login_required
@role_required(['tenant_admin'])
def college_settings(request):
    """
    College settings management
    """
    tenant = request.user.tenant
    
    settings, created = CollegeSettings.objects.get_or_create(tenant=tenant)
    
    if request.method == 'POST':
        settings.semester_system = request.POST.get('semester_system') == 'on'
        settings.grading_system = request.POST.get('grading_system')
        settings.minimum_attendance_percentage = request.POST.get('minimum_attendance_percentage')
        settings.sms_notifications_enabled = request.POST.get('sms_notifications_enabled') == 'on'
        settings.email_notifications_enabled = request.POST.get('email_notifications_enabled') == 'on'
        settings.parent_portal_enabled = request.POST.get('parent_portal_enabled') == 'on'
        settings.save()
        
        messages.success(request, 'Settings updated successfully.')
        return redirect('college_management:settings')
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'college_management/settings.html', context)


@login_required
@role_required(['tenant_admin'])
def holiday_list(request):
    """
    List all holidays
    """
    tenant = request.user.tenant
    
    holidays = Holiday.objects.filter(
        tenant=tenant
    ).order_by('date')
    
    context = {
        'holidays': holidays,
    }
    
    return render(request, 'college_management/holiday_list.html', context)
