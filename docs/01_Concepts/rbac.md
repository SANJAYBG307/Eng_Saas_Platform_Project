# Role-Based Access Control (RBAC)

## Overview

The platform implements a comprehensive Role-Based Access Control (RBAC) system with 6 distinct user roles, each with specific permissions and access levels.

## User Roles

### 1. Super Admin
**Scope**: Entire platform

**Responsibilities**:
- Manage all companies/tenants
- View system-wide analytics
- Configure global settings
- Manage subscriptions
- Access all tenant data (support purposes)

**Access**:
- `/company/` - Company management
- All administrative functions
- System health monitoring
- Billing and subscriptions

### 2. Tenant Admin
**Scope**: Single organization/college

**Responsibilities**:
- Manage organization settings
- Create departments
- Manage staff and students
- View organization reports
- Configure organization features

**Access**:
- `/admin/` - College management
- Department CRUD
- User management
- Announcements
- Reports and analytics

### 3. Department Admin
**Scope**: Specific department(s)

**Responsibilities**:
- Manage department settings
- Assign teachers to courses
- Manage department students
- View department reports
- Course scheduling

**Access**:
- `/dept/` - Department management
- Teacher assignments
- Course management
- Section management
- Department reports

### 4. Teacher
**Scope**: Assigned classes/sections

**Responsibilities**:
- Create and grade assignments
- Mark attendance
- Enter grades
- Communicate with students/parents
- View class roster

**Access**:
- `/teacher/` - Teacher portal
- Assignment management
- Attendance tracking
- Grade entry
- Student communication
- Class timetable

### 5. Student
**Scope**: Personal academic data

**Responsibilities**:
- View assignments
- Submit work
- Check grades and attendance
- View timetable and exams
- Pay fees
- View announcements

**Access**:
- `/student/` - Student portal
- Assignment submissions
- Grades view
- Attendance records
- Fee payments
- Timetable and exams

### 6. Parent
**Scope**: Linked children's data

**Responsibilities**:
- Monitor children's performance
- View attendance and grades
- Track fee payments
- Communicate with teachers
- View announcements

**Access**:
- `/parent/` - Parent portal
- Multiple children dashboard
- Performance tracking
- Attendance monitoring
- Teacher communication
- Fee history

## Permission Matrix

| Feature | Super Admin | Tenant Admin | Dept Admin | Teacher | Student | Parent |
|---------|------------|--------------|------------|---------|---------|--------|
| Manage Companies | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manage Departments | ✅ | ✅ | Owned Only | ❌ | ❌ | ❌ |
| Manage Users | ✅ | ✅ | Dept Only | ❌ | ❌ | ❌ |
| Create Assignments | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Submit Assignments | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| Mark Attendance | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| View Attendance | ✅ | ✅ | ✅ | ✅ | Own | Children |
| Enter Grades | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| View Grades | ✅ | ✅ | ✅ | ✅ | Own | Children |
| Manage Fees | ✅ | ✅ | ❌ | ❌ | Pay Own | View Children |
| View Reports | ✅ | ✅ | Dept Only | Class Only | Own | Children |
| Announcements | ✅ | ✅ | ✅ | ✅ | View | View |

## Implementation

### Role Decorator
```python
from functools import wraps
from django.shortcuts import redirect

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('auth:login')
            
            if request.user.role not in allowed_roles:
                return redirect('auth:permission_denied')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### Usage Example
```python
@login_required
@role_required(['teacher', 'department_admin'])
def create_assignment(request):
    # Only teachers and dept admins can access
    pass

@login_required
@role_required(['student'])
def submit_assignment(request, assignment_id):
    # Only students can access
    pass
```

### Middleware
```python
class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check user role and permissions
        if request.user.is_authenticated:
            request.user_role = request.user.role
        
        response = self.get_response(request)
        return response
```

## Access Patterns

### Hierarchical Access
Higher roles can access lower role features:
```
Super Admin > Tenant Admin > Dept Admin > Teacher
```

### Data Scope
- **Super Admin**: All companies
- **Tenant Admin**: Own company
- **Dept Admin**: Assigned departments
- **Teacher**: Assigned classes
- **Student**: Own data
- **Parent**: Linked children

### URL-based Protection
```python
# saas_platform/urls.py
urlpatterns = [
    path('company/', include('company_admin.urls')),     # Super Admin
    path('admin/', include('college_management.urls')),  # Tenant Admin
    path('dept/', include('department_management.urls')),# Dept Admin
    path('teacher/', include('teacher.urls')),           # Teacher
    path('student/', include('student.urls')),           # Student
    path('parent/', include('parent.urls')),             # Parent
]
```

## Security Best Practices

### 1. Always Check Authentication
```python
@login_required
def my_view(request):
    pass
```

### 2. Verify Role
```python
@role_required(['teacher'])
def teacher_only_view(request):
    pass
```

### 3. Check Object Ownership
```python
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Verify ownership
    if assignment.teacher != request.user:
        return HttpResponseForbidden()
```

### 4. Filter Queries by Scope
```python
# Teacher sees only their sections
sections = Section.objects.filter(teachers=request.user)

# Student sees only their section
section = request.user.section
```

## Role Transitions

### Promoting Users
```python
# Teacher becomes Department Admin
user.role = 'department_admin'
user.managed_departments.add(department)
user.save()
```

### Multiple Roles
Currently not supported - each user has one role. For complex scenarios:
- Create separate accounts
- Or expand permissions within role

## Testing RBAC

```python
@pytest.mark.rbac
def test_student_cannot_access_teacher_view(authenticated_client):
    """Test RBAC prevents unauthorized access"""
    response = authenticated_client.get(reverse('teacher:dashboard'))
    assert response.status_code == 403
```

## Common Scenarios

### Teacher Creates Assignment
1. User authenticated: ✅
2. Role = 'teacher': ✅
3. Section assigned to teacher: ✅
4. Create assignment: ✅

### Student Views Grade
1. User authenticated: ✅
2. Role = 'student': ✅
3. Grade belongs to student: ✅
4. Grade is published: ✅
5. Display grade: ✅

### Parent Views Child Performance
1. User authenticated: ✅
2. Role = 'parent': ✅
3. ParentStudentLink exists: ✅
4. Display child data: ✅

## Related Documentation

- [Multi-Tenancy](multi_tenancy.md)
- [User Management](../02_Implementation/user_management.md)
- [Security](../04_Explanation/security.md)
