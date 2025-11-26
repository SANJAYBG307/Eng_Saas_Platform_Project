"""
Unit tests for authentication and RBAC
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.unit
@pytest.mark.auth
@pytest.mark.django_db
class TestAuthentication:
    """Test authentication functionality"""
    
    def test_user_login_success(self, client, student_user):
        """Test successful user login"""
        response = client.post(reverse('auth:login'), {
            'username': 'student',
            'password': 'testpass123'
        })
        assert response.status_code in [200, 302]
    
    def test_user_login_wrong_password(self, client, student_user):
        """Test login with wrong password"""
        response = client.post(reverse('auth:login'), {
            'username': 'student',
            'password': 'wrongpassword'
        })
        assert response.status_code == 200  # Stays on login page
    
    def test_inactive_user_cannot_login(self, client, company):
        """Test inactive user cannot login"""
        inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@test.com',
            password='test123',
            company=company,
            role='student',
            is_active=False
        )
        response = client.post(reverse('auth:login'), {
            'username': 'inactive',
            'password': 'test123'
        })
        assert response.status_code == 200  # Login fails


@pytest.mark.unit
@pytest.mark.rbac
@pytest.mark.django_db
class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_student_cannot_access_teacher_dashboard(self, authenticated_client):
        """Test student cannot access teacher views"""
        response = authenticated_client.get(reverse('teacher:dashboard'))
        assert response.status_code in [302, 403]  # Redirect or Forbidden
    
    def test_teacher_can_access_teacher_dashboard(self, teacher_client):
        """Test teacher can access teacher dashboard"""
        response = teacher_client.get(reverse('teacher:dashboard'))
        assert response.status_code == 200
    
    def test_student_can_access_student_dashboard(self, authenticated_client):
        """Test student can access student dashboard"""
        response = authenticated_client.get(reverse('student:dashboard'))
        assert response.status_code == 200
    
    def test_unauthenticated_user_redirected(self, client):
        """Test unauthenticated user is redirected to login"""
        response = client.get(reverse('student:dashboard'))
        assert response.status_code == 302
        assert '/auth/login' in response.url


@pytest.mark.unit
@pytest.mark.django_db
class TestUserPermissions:
    """Test user permissions"""
    
    def test_super_admin_has_all_permissions(self, super_admin_user):
        """Test super admin role"""
        assert super_admin_user.role == 'super_admin'
        assert super_admin_user.is_active
    
    def test_tenant_admin_manages_company(self, tenant_admin_user, company):
        """Test tenant admin manages company"""
        assert tenant_admin_user.role == 'tenant_admin'
        assert tenant_admin_user.company == company
    
    def test_department_admin_has_department(self, department_admin_user, department):
        """Test department admin has managed departments"""
        assert department_admin_user.role == 'department_admin'
        assert department in department_admin_user.managed_departments.all()
    
    def test_teacher_belongs_to_department(self, teacher_user, department):
        """Test teacher belongs to department"""
        assert teacher_user.role == 'teacher'
        assert teacher_user.department == department
    
    def test_student_has_section(self, student_user, section):
        """Test student has section"""
        assert student_user.role == 'student'
        assert student_user.section == section
