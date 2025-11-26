"""
Teacher App Views
Teacher portal for managing classes, attendance, assignments, grades
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta

from core.models import UserAccount, Section, Subject, AcademicYear
from core.decorators import role_required
from .models import Attendance, Assignment, AssignmentSubmission, Grade, TeacherResource, TeacherNote
from college_management.models import Timetable, ExamSchedule


@login_required
@role_required(['teacher'])
def dashboard(request):
    """
    Teacher dashboard with overview
    """
    teacher = request.user
    
    # Get teacher's subjects
    teaching_subjects = Subject.objects.filter(
        tenant=teacher.tenant,
        teachers=teacher,
        is_deleted=False
    ).distinct()
    
    # Get teacher's sections
    teaching_sections = Section.objects.filter(
        tenant=teacher.tenant,
        is_deleted=False
    ).filter(
        Q(class_teacher=teacher) | Q(timetable__teacher=teacher)
    ).distinct()
    
    # Today's classes
    today = timezone.now().date()
    current_academic_year = AcademicYear.objects.filter(
        tenant=teacher.tenant,
        is_active=True
    ).first()
    
    todays_classes = []
    if current_academic_year:
        day_of_week = today.weekday() + 1  # Monday=1
        todays_classes = Timetable.objects.filter(
            teacher=teacher,
            academic_year=current_academic_year,
            day_of_week=day_of_week
        ).select_related('section', 'subject').order_by('period_number')[:5]
    
    # Pending assignments to grade
    pending_grading = AssignmentSubmission.objects.filter(
        assignment__teacher=teacher,
        status='submitted'
    ).count()
    
    # Recent assignments
    recent_assignments = Assignment.objects.filter(
        teacher=teacher,
        status='published'
    ).order_by('-created_at')[:5]
    
    context = {
        'teaching_subjects': teaching_subjects,
        'teaching_sections': teaching_sections,
        'todays_classes': todays_classes,
        'pending_grading': pending_grading,
        'recent_assignments': recent_assignments,
    }
    
    return render(request, 'teacher/dashboard.html', context)


@login_required
@role_required(['teacher'])
def my_classes(request):
    """
    List of all classes taught by teacher
    """
    teacher = request.user
    
    sections = Section.objects.filter(
        tenant=teacher.tenant,
        is_deleted=False
    ).filter(
        Q(class_teacher=teacher) | Q(timetable__teacher=teacher)
    ).distinct().annotate(
        student_count=Count('student_enrollments')
    )
    
    context = {
        'sections': sections,
    }
    
    return render(request, 'teacher/my_classes.html', context)


@login_required
@role_required(['teacher'])
def attendance_marking(request):
    """
    Mark attendance for a class
    """
    teacher = request.user
    
    if request.method == 'POST':
        section_id = request.POST.get('section')
        subject_id = request.POST.get('subject')
        date_str = request.POST.get('date')
        
        section = get_object_or_404(Section, id=section_id, tenant=teacher.tenant)
        subject = get_object_or_404(Subject, id=subject_id, tenant=teacher.tenant)
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get all students in section
        from core.models import StudentEnrollment
        enrollments = StudentEnrollment.objects.filter(
            section=section,
            is_deleted=False
        ).select_related('student')
        
        for enrollment in enrollments:
            student_id = str(enrollment.student.id)
            status = request.POST.get(f'status_{student_id}', 'absent')
            remarks = request.POST.get(f'remarks_{student_id}', '')
            
            Attendance.objects.update_or_create(
                tenant=teacher.tenant,
                student=enrollment.student,
                section=section,
                subject=subject,
                date=attendance_date,
                defaults={
                    'teacher': teacher,
                    'status': status,
                    'remarks': remarks
                }
            )
        
        messages.success(request, 'Attendance marked successfully.')
        return redirect('teacher:attendance_marking')
    
    # Get sections and subjects for teacher
    sections = Section.objects.filter(
        tenant=teacher.tenant,
        is_deleted=False
    ).filter(
        Q(class_teacher=teacher) | Q(timetable__teacher=teacher)
    ).distinct()
    
    subjects = Subject.objects.filter(
        tenant=teacher.tenant,
        teachers=teacher,
        is_deleted=False
    )
    
    context = {
        'sections': sections,
        'subjects': subjects,
    }
    
    return render(request, 'teacher/attendance_marking.html', context)


@login_required
@role_required(['teacher'])
def grade_management(request):
    """
    Manage grades for students
    """
    teacher = request.user
    
    grades = Grade.objects.filter(
        teacher=teacher
    ).select_related('student', 'subject').order_by('-exam_date')
    
    # Pagination
    paginator = Paginator(grades, 50)
    page = request.GET.get('page', 1)
    grades_page = paginator.get_page(page)
    
    context = {
        'grades': grades_page,
    }
    
    return render(request, 'teacher/grade_management.html', context)


@login_required
@role_required(['teacher'])
def assignments(request):
    """
    List all assignments created by teacher
    """
    teacher = request.user
    
    assignments_list = Assignment.objects.filter(
        teacher=teacher
    ).select_related('section', 'subject').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(assignments_list, 20)
    page = request.GET.get('page', 1)
    assignments_page = paginator.get_page(page)
    
    context = {
        'assignments': assignments_page,
    }
    
    return render(request, 'teacher/assignments.html', context)


@login_required
@role_required(['teacher'])
def assignment_create(request):
    """
    Create new assignment
    """
    teacher = request.user
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        section_id = request.POST.get('section')
        subject_id = request.POST.get('subject')
        due_date = request.POST.get('due_date')
        max_marks = request.POST.get('max_marks', 100)
        status = request.POST.get('status', 'draft')
        
        current_academic_year = AcademicYear.objects.filter(
            tenant=teacher.tenant,
            is_active=True
        ).first()
        
        Assignment.objects.create(
            tenant=teacher.tenant,
            teacher=teacher,
            section_id=section_id,
            subject_id=subject_id,
            academic_year=current_academic_year,
            title=title,
            description=description,
            due_date=due_date,
            max_marks=max_marks,
            status=status
        )
        
        messages.success(request, 'Assignment created successfully.')
        return redirect('teacher:assignments')
    
    sections = Section.objects.filter(
        tenant=teacher.tenant,
        is_deleted=False
    ).filter(
        Q(class_teacher=teacher) | Q(timetable__teacher=teacher)
    ).distinct()
    
    subjects = Subject.objects.filter(
        tenant=teacher.tenant,
        teachers=teacher,
        is_deleted=False
    )
    
    context = {
        'sections': sections,
        'subjects': subjects,
    }
    
    return render(request, 'teacher/assignment_form.html', context)


@login_required
@role_required(['teacher'])
def assignment_submissions(request, assignment_id):
    """
    View submissions for an assignment
    """
    teacher = request.user
    assignment = get_object_or_404(Assignment, id=assignment_id, teacher=teacher)
    
    submissions = AssignmentSubmission.objects.filter(
        assignment=assignment
    ).select_related('student').order_by('-submission_date')
    
    context = {
        'assignment': assignment,
        'submissions': submissions,
    }
    
    return render(request, 'teacher/assignment_submissions.html', context)


@login_required
@role_required(['teacher'])
def student_performance(request):
    """
    View student performance analytics
    """
    teacher = request.user
    
    context = {}
    
    return render(request, 'teacher/student_performance.html', context)


@login_required
@role_required(['teacher'])
def my_timetable(request):
    """
    Teacher's timetable
    """
    teacher = request.user
    
    current_academic_year = AcademicYear.objects.filter(
        tenant=teacher.tenant,
        is_active=True
    ).first()
    
    timetable_entries = []
    if current_academic_year:
        timetable_entries = Timetable.objects.filter(
            teacher=teacher,
            academic_year=current_academic_year
        ).select_related('section', 'subject').order_by('day_of_week', 'period_number')
    
    context = {
        'timetable_entries': timetable_entries,
    }
    
    return render(request, 'teacher/timetable.html', context)


@login_required
@role_required(['teacher'])
def exam_schedules(request):
    """
    View exam schedules
    """
    teacher = request.user
    
    exams = ExamSchedule.objects.filter(
        tenant=teacher.tenant,
        is_published=True
    ).order_by('-start_date')[:20]
    
    context = {
        'exams': exams,
    }
    
    return render(request, 'teacher/exam_schedules.html', context)


@login_required
@role_required(['teacher'])
def resources(request):
    """
    Teaching resources
    """
    teacher = request.user
    
    resources_list = TeacherResource.objects.filter(
        teacher=teacher
    ).select_related('subject', 'section').order_by('-created_at')
    
    paginator = Paginator(resources_list, 20)
    page = request.GET.get('page', 1)
    resources_page = paginator.get_page(page)
    
    context = {
        'resources': resources_page,
    }
    
    return render(request, 'teacher/resources.html', context)


@login_required
@role_required(['teacher'])
def communication(request):
    """
    Communication with students/parents
    """
    context = {}
    
    return render(request, 'teacher/communication.html', context)


@login_required
@role_required(['teacher'])
def profile(request):
    """
    Teacher profile
    """
    teacher = request.user
    
    context = {
        'teacher': teacher,
    }
    
    return render(request, 'teacher/profile.html', context)


@login_required
@role_required(['teacher'])
def reports(request):
    """
    Generate various reports
    """
    context = {}
    
    return render(request, 'teacher/reports.html', context)
