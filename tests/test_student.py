"""
Unit tests for Student app
"""

import pytest
from django.urls import reverse
from student.models import FeePayment


@pytest.mark.unit
@pytest.mark.django_db
class TestFeePaymentModel:
    """Test FeePayment model"""
    
    def test_create_fee_payment(self, fee_payment):
        """Test creating fee payment"""
        assert fee_payment.fee_type == 'tuition'
        assert fee_payment.amount == 5000.00
        assert fee_payment.status == 'pending'
    
    def test_fee_payment_statuses(self):
        """Test fee payment statuses"""
        statuses = ['pending', 'paid', 'overdue', 'cancelled']
        from student.models import FeePayment
        status_values = [choice[0] for choice in FeePayment.STATUS_CHOICES]
        for status in statuses:
            assert status in status_values
    
    def test_mark_fee_as_paid(self, fee_payment):
        """Test marking fee as paid"""
        fee_payment.status = 'paid'
        fee_payment.save()
        assert fee_payment.status == 'paid'


@pytest.mark.unit
@pytest.mark.django_db
class TestStudentViews:
    """Test Student views"""
    
    def test_student_dashboard_access(self, authenticated_client):
        """Test student can access dashboard"""
        response = authenticated_client.get(reverse('student:dashboard'))
        assert response.status_code == 200
    
    def test_student_view_assignments(self, authenticated_client, assignment):
        """Test student can view assignments"""
        response = authenticated_client.get(reverse('student:assignments'))
        assert response.status_code == 200
    
    def test_student_view_grades(self, authenticated_client):
        """Test student can view grades"""
        response = authenticated_client.get(reverse('student:grades'))
        assert response.status_code == 200
    
    def test_student_view_attendance(self, authenticated_client):
        """Test student can view attendance"""
        response = authenticated_client.get(reverse('student:attendance'))
        assert response.status_code == 200
    
    def test_student_view_fees(self, authenticated_client, fee_payment):
        """Test student can view fee payments"""
        response = authenticated_client.get(reverse('student:fees'))
        assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.django_db
class TestStudentAssignmentSubmission:
    """Test student assignment submission"""
    
    def test_submit_assignment(self, authenticated_client, assignment):
        """Test student can submit assignment"""
        response = authenticated_client.post(
            reverse('student:submit_assignment', kwargs={'pk': assignment.id}),
            {'submission_text': 'My assignment submission'}
        )
        assert response.status_code in [200, 302]
    
    def test_view_submitted_assignments(self, authenticated_client):
        """Test student can view submitted assignments"""
        response = authenticated_client.get(reverse('student:submissions'))
        assert response.status_code == 200
