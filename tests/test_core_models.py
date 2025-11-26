"""
Unit tests for Core models
"""

import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from core.models import (
    Company, UserAccount, AcademicYear, Section, 
    Subject, ParentStudentLink
)

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestCompanyModel:
    """Test Company model"""
    
    def test_create_company(self):
        """Test creating a company"""
        company = Company.objects.create(
            name='Test Company',
            subdomain='testco',
            schema_name='testco',
            contact_email='test@company.com'
        )
        assert company.name == 'Test Company'
        assert company.is_active is True
        assert str(company) == 'Test Company'
    
    def test_company_unique_subdomain(self, company):
        """Test subdomain uniqueness"""
        with pytest.raises(Exception):
            Company.objects.create(
                name='Another Company',
                subdomain='testco',  # Duplicate
                schema_name='another'
            )
    
    def test_company_deactivation(self, company):
        """Test company deactivation"""
        company.is_active = False
        company.save()
        assert not company.is_active


@pytest.mark.unit
@pytest.mark.django_db
class TestUserAccountModel:
    """Test UserAccount model"""
    
    def test_create_user(self, company):
        """Test creating a user"""
        user = UserAccount.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            company=company,
            role='student'
        )
        assert user.username == 'testuser'
        assert user.check_password('testpass123')
        assert user.role == 'student'
        assert user.company == company
    
    def test_user_full_name(self, student_user):
        """Test full name property"""
        assert student_user.full_name == 'Jane Student'
    
    def test_user_roles(self):
        """Test all user roles"""
        roles = ['super_admin', 'tenant_admin', 'department_admin', 
                'teacher', 'student', 'parent']
        for role in roles:
            assert role in dict(UserAccount.ROLE_CHOICES)
    
    def test_user_without_company_fails(self):
        """Test user creation requires company"""
        with pytest.raises(Exception):
            UserAccount.objects.create_user(
                username='nocompany',
                email='no@company.com',
                password='test123',
                role='student'
            )


@pytest.mark.unit
@pytest.mark.django_db
class TestAcademicYearModel:
    """Test AcademicYear model"""
    
    def test_create_academic_year(self):
        """Test creating academic year"""
        year = AcademicYear.objects.create(
            name='2024-2025',
            start_date='2024-08-01',
            end_date='2025-07-31'
        )
        assert year.name == '2024-2025'
        assert str(year) == '2024-2025'
    
    def test_only_one_active_year(self, academic_year):
        """Test only one academic year can be active"""
        year2 = AcademicYear.objects.create(
            name='2025-2026',
            start_date='2025-08-01',
            end_date='2026-07-31',
            is_active=True
        )
        academic_year.refresh_from_db()
        # One should be inactive
        active_count = AcademicYear.objects.filter(is_active=True).count()
        assert active_count <= 1


@pytest.mark.unit
@pytest.mark.django_db
class TestSectionModel:
    """Test Section model"""
    
    def test_create_section(self, department, academic_year):
        """Test creating a section"""
        section = Section.objects.create(
            department=department,
            academic_year=academic_year,
            name='A',
            semester=1,
            capacity=60
        )
        assert section.name == 'A'
        assert section.semester == 1
        assert section.capacity == 60
    
    def test_section_str(self, section):
        """Test section string representation"""
        assert 'A' in str(section)


@pytest.mark.unit
@pytest.mark.django_db
class TestSubjectModel:
    """Test Subject model"""
    
    def test_create_subject(self, subject):
        """Test creating a subject"""
        assert subject.name == 'Data Structures'
        assert subject.code == 'CS201'
        assert subject.credits == 4
    
    def test_subject_str(self, subject):
        """Test subject string representation"""
        assert 'Data Structures' in str(subject)


@pytest.mark.unit
@pytest.mark.django_db
class TestParentStudentLink:
    """Test ParentStudentLink model"""
    
    def test_create_parent_student_link(self, parent_user, student_user):
        """Test creating parent-student relationship"""
        link = ParentStudentLink.objects.create(
            parent=parent_user,
            student=student_user,
            relationship='father'
        )
        assert link.parent == parent_user
        assert link.student == student_user
        assert link.relationship == 'father'
    
    def test_parent_can_have_multiple_children(self, parent_user, student_user, company, department, section):
        """Test parent can have multiple children"""
        student2 = UserAccount.objects.create_user(
            username='student2',
            email='student2@test.com',
            password='test123',
            role='student',
            company=company,
            department=department,
            section=section
        )
        
        ParentStudentLink.objects.create(
            parent=parent_user,
            student=student_user,
            relationship='mother'
        )
        ParentStudentLink.objects.create(
            parent=parent_user,
            student=student2,
            relationship='mother'
        )
        
        assert parent_user.children.count() == 2
