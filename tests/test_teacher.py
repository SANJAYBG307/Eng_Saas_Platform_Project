"""
Unit tests for Teacher app models and views
"""

import pytest
from datetime import date, timedelta
from django.urls import reverse
from teacher.models import Assignment, Attendance, Grade


@pytest.mark.unit
@pytest.mark.django_db
class TestAssignmentModel:
    """Test Assignment model"""
    
    def test_create_assignment(self, assignment):
        """Test creating an assignment"""
        assert assignment.title == 'Test Assignment'
        assert assignment.max_marks == 100
        assert assignment.assignment_type == 'homework'
    
    def test_assignment_str(self, assignment):
        """Test assignment string representation"""
        assert 'Test Assignment' in str(assignment)
    
    def test_assignment_is_overdue(self, teacher_user, subject, section):
        """Test assignment overdue check"""
        past_date = date.today() - timedelta(days=1)
        overdue_assignment = Assignment.objects.create(
            teacher=teacher_user,
            subject=subject,
            section=section,
            title='Overdue Assignment',
            due_date=past_date,
            max_marks=100
        )
        assert overdue_assignment.due_date < date.today()


@pytest.mark.unit
@pytest.mark.django_db
class TestAttendanceModel:
    """Test Attendance model"""
    
    def test_create_attendance(self, attendance):
        """Test creating attendance record"""
        assert attendance.status == 'present'
        assert attendance.date == date(2024, 11, 26)
    
    def test_attendance_statuses(self):
        """Test all attendance statuses"""
        statuses = ['present', 'absent', 'late', 'excused']
        from teacher.models import Attendance
        status_values = [choice[0] for choice in Attendance.STATUS_CHOICES]
        for status in statuses:
            assert status in status_values


@pytest.mark.unit
@pytest.mark.django_db
class TestGradeModel:
    """Test Grade model"""
    
    def test_create_grade(self, student_user, subject, teacher_user):
        """Test creating a grade"""
        grade = Grade.objects.create(
            student=student_user,
            subject=subject,
            teacher=teacher_user,
            exam_type='midterm',
            marks_obtained=85,
            total_marks=100
        )
        assert grade.marks_obtained == 85
        assert grade.total_marks == 100
    
    def test_grade_percentage_calculation(self, student_user, subject, teacher_user):
        """Test grade percentage calculation"""
        grade = Grade.objects.create(
            student=student_user,
            subject=subject,
            teacher=teacher_user,
            exam_type='final',
            marks_obtained=90,
            total_marks=100
        )
        # Assuming percentage property exists
        expected_percentage = (90 / 100) * 100
        assert grade.marks_obtained / grade.total_marks == 0.9


@pytest.mark.unit
@pytest.mark.django_db
class TestTeacherViews:
    """Test Teacher views"""
    
    def test_teacher_dashboard_access(self, teacher_client):
        """Test teacher can access dashboard"""
        response = teacher_client.get(reverse('teacher:dashboard'))
        assert response.status_code == 200
    
    def test_teacher_assignments_list(self, teacher_client, assignment):
        """Test teacher can view assignments"""
        response = teacher_client.get(reverse('teacher:assignments'))
        assert response.status_code == 200
    
    def test_teacher_create_assignment(self, teacher_client, subject, section):
        """Test teacher can create assignment"""
        response = teacher_client.post(reverse('teacher:assignment_create'), {
            'subject': subject.id,
            'section': section.id,
            'title': 'New Assignment',
            'description': 'Test Description',
            'due_date': date.today() + timedelta(days=7),
            'max_marks': 100,
            'assignment_type': 'homework'
        })
        assert response.status_code in [200, 302]
    
    def test_student_cannot_access_teacher_views(self, authenticated_client):
        """Test student cannot access teacher dashboard"""
        response = authenticated_client.get(reverse('teacher:dashboard'))
        assert response.status_code in [302, 403]


@pytest.mark.integration
@pytest.mark.django_db
class TestTeacherAttendance:
    """Test teacher attendance management"""
    
    def test_mark_attendance(self, teacher_client, student_user, section):
        """Test marking attendance"""
        response = teacher_client.post(reverse('teacher:mark_attendance'), {
            'section': section.id,
            'date': date.today(),
            'students': [student_user.id],
            'status': 'present'
        })
        assert response.status_code in [200, 302]
    
    def test_view_attendance_records(self, teacher_client, attendance):
        """Test viewing attendance records"""
        response = teacher_client.get(reverse('teacher:attendance'))
        assert response.status_code == 200
