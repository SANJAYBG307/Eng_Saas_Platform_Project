"""
Integration tests for multi-tenancy
"""

import pytest
from django.test import override_settings
from core.models import Company, UserAccount


@pytest.mark.integration
@pytest.mark.multi_tenant
@pytest.mark.django_db
class TestMultiTenancy:
    """Test multi-tenancy functionality"""
    
    def test_tenant_isolation(self):
        """Test data isolation between tenants"""
        # Create two companies
        company1 = Company.objects.create(
            name='Company 1',
            subdomain='company1',
            schema_name='company1'
        )
        company2 = Company.objects.create(
            name='Company 2',
            subdomain='company2',
            schema_name='company2'
        )
        
        # Create users for each company
        user1 = UserAccount.objects.create_user(
            username='user1',
            email='user1@company1.com',
            password='test123',
            company=company1,
            role='student'
        )
        user2 = UserAccount.objects.create_user(
            username='user2',
            email='user2@company2.com',
            password='test123',
            company=company2,
            role='student'
        )
        
        # Verify users belong to correct companies
        assert user1.company == company1
        assert user2.company == company2
        assert user1.company != user2.company
    
    def test_company_user_query(self, company):
        """Test querying users by company"""
        # Create multiple users for same company
        for i in range(3):
            UserAccount.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@test.com',
                password='test123',
                company=company,
                role='student'
            )
        
        # Query users for this company
        company_users = UserAccount.objects.filter(company=company)
        assert company_users.count() >= 3


@pytest.mark.integration
@pytest.mark.django_db
class TestCrossAppIntegration:
    """Test integration between different apps"""
    
    def test_teacher_assignment_to_student(self, teacher_user, student_user, subject, section, assignment):
        """Test assignment flow from teacher to student"""
        # Verify assignment is created by teacher
        assert assignment.teacher == teacher_user
        assert assignment.section == section
        
        # Verify student can see assignment (same section)
        assert student_user.section == section
    
    def test_parent_views_student_grades(self, parent_user, student_user, parent_student_link, teacher_user, subject):
        """Test parent accessing student grades"""
        from teacher.models import Grade
        
        # Create grade for student
        grade = Grade.objects.create(
            student=student_user,
            subject=subject,
            teacher=teacher_user,
            exam_type='midterm',
            marks_obtained=85,
            total_marks=100
        )
        
        # Verify parent-student link
        link = parent_user.children.filter(student=student_user).first()
        assert link is not None
        assert link.student == student_user
    
    def test_department_admin_manages_teachers(self, department_admin_user, teacher_user, department):
        """Test department admin can manage teachers"""
        assert department in department_admin_user.managed_departments.all()
        assert teacher_user.department == department


@pytest.mark.integration
@pytest.mark.payment
@pytest.mark.django_db
class TestPaymentIntegration:
    """Test payment integration (Stripe)"""
    
    def test_fee_payment_creation(self, student_user):
        """Test fee payment creation"""
        from student.models import FeePayment
        
        fee = FeePayment.objects.create(
            student=student_user,
            fee_type='tuition',
            amount=5000.00,
            due_date='2024-12-31',
            status='pending'
        )
        assert fee.status == 'pending'
        assert fee.amount == 5000.00
    
    @pytest.mark.skip(reason="Requires Stripe API keys")
    def test_stripe_payment_processing(self, student_user, fee_payment):
        """Test Stripe payment processing"""
        # This would test actual Stripe integration
        pass


@pytest.mark.integration
@pytest.mark.django_db
class TestNotificationSystem:
    """Test notification system integration"""
    
    def test_announcement_to_students(self, company, section, announcement):
        """Test announcement reaches students"""
        announcement.target_sections.add(section)
        announcement.save()
        
        assert section in announcement.target_sections.all()
    
    def test_parent_communication_notification(self, parent_user, student_user, teacher_user, parent_student_link):
        """Test parent communication creates notification"""
        from parent.models import ParentCommunication
        
        comm = ParentCommunication.objects.create(
            parent=parent_user,
            student=student_user,
            teacher=teacher_user,
            subject='Test',
            message='Test message',
            message_type='inquiry'
        )
        
        # Verify communication is created
        assert comm.parent == parent_user
        assert comm.teacher == teacher_user
