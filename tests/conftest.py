"""
Pytest configuration and fixtures for SaaS Platform tests
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from core.models import (
    Company, UserAccount, Section, Subject, 
    AcademicYear, ParentStudentLink
)
from college_management.models import Department, Announcement
from teacher.models import Assignment, Attendance
from student.models import FeePayment

User = get_user_model()


@pytest.fixture
def client():
    """Django test client"""
    return Client()


@pytest.fixture
def api_client():
    """DRF API test client"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def company(db):
    """Create a test company (tenant)"""
    return Company.objects.create(
        name='Test Company',
        subdomain='testco',
        schema_name='testco',
        is_active=True,
        contact_email='test@company.com',
        contact_phone='+1234567890'
    )


@pytest.fixture
def academic_year(db):
    """Create an academic year"""
    return AcademicYear.objects.create(
        name='2024-2025',
        start_date='2024-08-01',
        end_date='2025-07-31',
        is_active=True
    )


@pytest.fixture
def department(db, company):
    """Create a test department"""
    from college_management.models import Department
    return Department.objects.create(
        company=company,
        name='Computer Science',
        code='CS',
        is_active=True
    )


@pytest.fixture
def subject(db, department):
    """Create a test subject"""
    return Subject.objects.create(
        department=department,
        name='Data Structures',
        code='CS201',
        credits=4
    )


@pytest.fixture
def section(db, department, academic_year):
    """Create a test section"""
    return Section.objects.create(
        department=department,
        academic_year=academic_year,
        name='A',
        semester=1,
        capacity=60
    )


@pytest.fixture
def super_admin_user(db, company):
    """Create a super admin user"""
    return UserAccount.objects.create_user(
        username='superadmin',
        email='superadmin@test.com',
        password='testpass123',
        first_name='Super',
        last_name='Admin',
        role='super_admin',
        company=company,
        is_active=True
    )


@pytest.fixture
def tenant_admin_user(db, company):
    """Create a tenant admin user"""
    return UserAccount.objects.create_user(
        username='tenantadmin',
        email='tenantadmin@test.com',
        password='testpass123',
        first_name='Tenant',
        last_name='Admin',
        role='tenant_admin',
        company=company,
        is_active=True
    )


@pytest.fixture
def department_admin_user(db, company, department):
    """Create a department admin user"""
    user = UserAccount.objects.create_user(
        username='deptadmin',
        email='deptadmin@test.com',
        password='testpass123',
        first_name='Department',
        last_name='Admin',
        role='department_admin',
        company=company,
        is_active=True
    )
    user.managed_departments.add(department)
    return user


@pytest.fixture
def teacher_user(db, company, department):
    """Create a teacher user"""
    user = UserAccount.objects.create_user(
        username='teacher',
        email='teacher@test.com',
        password='testpass123',
        first_name='John',
        last_name='Teacher',
        role='teacher',
        company=company,
        department=department,
        is_active=True
    )
    return user


@pytest.fixture
def student_user(db, company, department, section):
    """Create a student user"""
    user = UserAccount.objects.create_user(
        username='student',
        email='student@test.com',
        password='testpass123',
        first_name='Jane',
        last_name='Student',
        role='student',
        company=company,
        department=department,
        section=section,
        is_active=True
    )
    return user


@pytest.fixture
def parent_user(db, company):
    """Create a parent user"""
    return UserAccount.objects.create_user(
        username='parent',
        email='parent@test.com',
        password='testpass123',
        first_name='Mary',
        last_name='Parent',
        role='parent',
        company=company,
        is_active=True
    )


@pytest.fixture
def parent_student_link(db, parent_user, student_user):
    """Create parent-student relationship"""
    return ParentStudentLink.objects.create(
        parent=parent_user,
        student=student_user,
        relationship='mother'
    )


@pytest.fixture
def assignment(db, teacher_user, subject, section):
    """Create a test assignment"""
    return Assignment.objects.create(
        teacher=teacher_user,
        subject=subject,
        section=section,
        title='Test Assignment',
        description='Test Description',
        due_date='2024-12-31',
        max_marks=100,
        assignment_type='homework'
    )


@pytest.fixture
def attendance(db, student_user, section):
    """Create attendance record"""
    return Attendance.objects.create(
        student=student_user,
        section=section,
        date='2024-11-26',
        status='present'
    )


@pytest.fixture
def fee_payment(db, student_user):
    """Create fee payment record"""
    return FeePayment.objects.create(
        student=student_user,
        fee_type='tuition',
        amount=5000.00,
        due_date='2024-12-31',
        status='pending'
    )


@pytest.fixture
def announcement(db, company, section):
    """Create announcement"""
    return Announcement.objects.create(
        company=company,
        title='Test Announcement',
        content='Test Content',
        priority='medium',
        announcement_type='general',
        is_published=True
    )


# Authentication helpers
@pytest.fixture
def authenticated_client(client, student_user):
    """Client authenticated as student"""
    client.force_login(student_user)
    return client


@pytest.fixture
def teacher_client(client, teacher_user):
    """Client authenticated as teacher"""
    client.force_login(teacher_user)
    return client


@pytest.fixture
def admin_client(client, tenant_admin_user):
    """Client authenticated as admin"""
    client.force_login(tenant_admin_user)
    return client
