"""
Unit tests for Parent app
"""

import pytest
from django.urls import reverse
from parent.models import ParentCommunication


@pytest.mark.unit
@pytest.mark.django_db
class TestParentCommunicationModel:
    """Test ParentCommunication model"""
    
    def test_create_communication(self, parent_user, student_user, teacher_user):
        """Test creating parent communication"""
        comm = ParentCommunication.objects.create(
            parent=parent_user,
            student=student_user,
            teacher=teacher_user,
            subject='Question about homework',
            message='Can you explain the assignment?',
            message_type='inquiry',
            priority='medium'
        )
        assert comm.subject == 'Question about homework'
        assert comm.status == 'sent'
        assert comm.priority == 'medium'
    
    def test_communication_types(self):
        """Test communication types"""
        types = ['inquiry', 'concern', 'request', 'feedback', 'complaint', 'appreciation']
        from parent.models import ParentCommunication
        type_values = [choice[0] for choice in ParentCommunication.MESSAGE_TYPE_CHOICES]
        for msg_type in types:
            assert msg_type in type_values
    
    def test_reply_to_communication(self, parent_user, student_user, teacher_user):
        """Test replying to communication"""
        comm = ParentCommunication.objects.create(
            parent=parent_user,
            student=student_user,
            teacher=teacher_user,
            subject='Test',
            message='Test message',
            message_type='inquiry'
        )
        comm.reply = 'This is the reply'
        comm.status = 'replied'
        comm.save()
        
        assert comm.reply == 'This is the reply'
        assert comm.status == 'replied'


@pytest.mark.unit
@pytest.mark.django_db
class TestParentViews:
    """Test Parent views"""
    
    def test_parent_dashboard_access(self, client, parent_user):
        """Test parent can access dashboard"""
        client.force_login(parent_user)
        response = client.get(reverse('parent:dashboard'))
        assert response.status_code == 200
    
    def test_parent_view_child_performance(self, client, parent_user, student_user, parent_student_link):
        """Test parent can view child performance"""
        client.force_login(parent_user)
        response = client.get(
            reverse('parent:child_performance', kwargs={'student_id': student_user.id})
        )
        assert response.status_code == 200
    
    def test_parent_view_child_attendance(self, client, parent_user, student_user, parent_student_link):
        """Test parent can view child attendance"""
        client.force_login(parent_user)
        response = client.get(
            reverse('parent:attendance_tracking', kwargs={'student_id': student_user.id})
        )
        assert response.status_code == 200
    
    def test_parent_send_communication(self, client, parent_user, student_user, teacher_user, parent_student_link):
        """Test parent can send communication"""
        client.force_login(parent_user)
        response = client.post(reverse('parent:communication'), {
            'student': student_user.id,
            'teacher': teacher_user.id,
            'subject': 'Test Subject',
            'message': 'Test message',
            'message_type': 'inquiry',
            'priority': 'medium'
        })
        assert response.status_code in [200, 302]
    
    def test_parent_cannot_view_other_children(self, client, parent_user, company, department, section):
        """Test parent cannot view children they're not linked to"""
        # Create another student
        from core.models import UserAccount
        other_student = UserAccount.objects.create_user(
            username='otherstudent',
            email='other@test.com',
            password='test123',
            role='student',
            company=company,
            department=department,
            section=section
        )
        
        client.force_login(parent_user)
        response = client.get(
            reverse('parent:child_performance', kwargs={'student_id': other_student.id})
        )
        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
class TestParentMultipleChildren:
    """Test parent with multiple children"""
    
    def test_parent_dashboard_shows_all_children(self, client, parent_user, student_user, parent_student_link, company, department, section):
        """Test dashboard shows all children"""
        # Create second child
        from core.models import UserAccount, ParentStudentLink
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
            student=student2,
            relationship='mother'
        )
        
        client.force_login(parent_user)
        response = client.get(reverse('parent:dashboard'))
        assert response.status_code == 200
        # Should see both children in context
        assert len(response.context.get('children', [])) == 2
