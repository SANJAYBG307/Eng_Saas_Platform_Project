# Testing Guide for SaaS Platform

## Overview

This project uses **pytest** and **pytest-django** for testing. Tests are organized by type:
- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test interactions between components
- **E2E tests**: Test complete user workflows

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_core_models.py      # Core app model tests
├── test_authentication.py   # Auth and RBAC tests
├── test_teacher.py          # Teacher app tests
├── test_student.py          # Student app tests
├── test_parent.py           # Parent app tests
├── test_integration.py      # Integration tests
└── README.md                # This file
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_core_models.py
```

### Run Specific Test Class
```bash
pytest tests/test_core_models.py::TestCompanyModel
```

### Run Specific Test Method
```bash
pytest tests/test_core_models.py::TestCompanyModel::test_create_company
```

### Run Tests by Marker
```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# Authentication tests
pytest -m auth

# RBAC tests
pytest -m rbac

# Multi-tenancy tests
pytest -m multi_tenant
```

### Run with Coverage
```bash
# Generate coverage report
pytest --cov=. --cov-report=html

# View coverage
# Open htmlcov/index.html in browser
```

### Run in Verbose Mode
```bash
pytest -v
```

### Run with Output
```bash
pytest -s
```

## Test Markers

Tests are organized with markers for easy filtering:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.rbac` - Role-based access control tests
- `@pytest.mark.multi_tenant` - Multi-tenancy tests
- `@pytest.mark.payment` - Payment integration tests
- `@pytest.mark.slow` - Slow running tests

## Available Fixtures

### Database Fixtures
- `company` - Test company (tenant)
- `academic_year` - Academic year
- `department` - Department
- `subject` - Subject
- `section` - Section

### User Fixtures
- `super_admin_user` - Super admin user
- `tenant_admin_user` - Tenant admin user
- `department_admin_user` - Department admin user
- `teacher_user` - Teacher user
- `student_user` - Student user
- `parent_user` - Parent user

### Relationship Fixtures
- `parent_student_link` - Parent-student relationship

### App Model Fixtures
- `assignment` - Teacher assignment
- `attendance` - Attendance record
- `fee_payment` - Fee payment
- `announcement` - Announcement

### Client Fixtures
- `client` - Django test client
- `api_client` - DRF API client
- `authenticated_client` - Client logged in as student
- `teacher_client` - Client logged in as teacher
- `admin_client` - Client logged in as admin

## Writing New Tests

### Unit Test Example
```python
import pytest

@pytest.mark.unit
@pytest.mark.django_db
class TestMyModel:
    def test_create_instance(self):
        """Test creating model instance"""
        obj = MyModel.objects.create(name='Test')
        assert obj.name == 'Test'
```

### Integration Test Example
```python
import pytest
from django.urls import reverse

@pytest.mark.integration
@pytest.mark.django_db
class TestMyView:
    def test_view_integration(self, authenticated_client):
        """Test view with authentication"""
        response = authenticated_client.get(reverse('my_view'))
        assert response.status_code == 200
```

### Using Fixtures
```python
@pytest.mark.django_db
def test_with_fixtures(student_user, assignment):
    """Test using pre-created fixtures"""
    assert student_user.role == 'student'
    assert assignment.max_marks == 100
```

## Best Practices

### 1. Test Naming
- Use descriptive names: `test_user_can_submit_assignment`
- Follow pattern: `test_<what>_<condition>`

### 2. Test Organization
- Group related tests in classes
- Use markers to categorize tests
- Keep tests focused and isolated

### 3. Fixtures
- Use fixtures for common setup
- Keep fixtures simple and reusable
- Document fixture purpose

### 4. Assertions
- Use clear assertions with messages
- Test one thing per test method
- Verify both positive and negative cases

### 5. Database Tests
- Always use `@pytest.mark.django_db` decorator
- Use transactions for speed
- Clean up test data

## Common Patterns

### Testing Views
```python
def test_view_access(self, authenticated_client):
    """Test authenticated user can access view"""
    response = authenticated_client.get(reverse('view_name'))
    assert response.status_code == 200
    assert 'expected_key' in response.context
```

### Testing Models
```python
def test_model_creation(self, company):
    """Test model can be created"""
    obj = MyModel.objects.create(
        name='Test',
        company=company
    )
    assert obj.pk is not None
    assert str(obj) == 'Test'
```

### Testing Permissions
```python
def test_permission_denied(self, client, student_user):
    """Test user without permission is denied"""
    client.force_login(student_user)
    response = client.get(reverse('admin_view'))
    assert response.status_code in [302, 403]
```

### Testing Forms
```python
def test_form_valid(self):
    """Test form with valid data"""
    form = MyForm(data={'field': 'value'})
    assert form.is_valid()
```

## Continuous Integration

Tests should be run in CI/CD pipeline:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    pytest --cov=. --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

## Coverage Goals

Target coverage levels:
- **Overall**: 80%+
- **Models**: 90%+
- **Views**: 75%+
- **Utilities**: 85%+

## Troubleshooting

### Tests Failing Due to Database
```bash
# Reset test database
pytest --create-db

# Use --reuse-db for speed
pytest --reuse-db
```

### Import Errors
```bash
# Ensure virtual environment is activated
# Check PYTHONPATH includes project root
```

### Slow Tests
```bash
# Run only fast tests
pytest -m "not slow"

# Run in parallel (requires pytest-xdist)
pytest -n auto
```

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-django documentation](https://pytest-django.readthedocs.io/)
- [Django testing documentation](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
