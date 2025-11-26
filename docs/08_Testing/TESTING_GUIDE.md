# 🧪 Complete Testing Guide

## How to Test the Django SaaS Platform - Step-by-Step (Simple English)

---

## 📚 Table of Contents
1. [What is Testing?](#what-is-testing)
2. [Why Test This Project?](#why-test-this-project)
3. [Types of Tests](#types-of-tests)
4. [Setup for Testing](#setup-for-testing)
5. [Running Tests](#running-tests)
6. [Understanding Test Results](#understanding-test-results)
7. [Testing Each App](#testing-each-app)
8. [Common Testing Scenarios](#common-testing-scenarios)

---

## 🤔 What is Testing?

**Simple Explanation**: Testing means checking if your code works correctly.

**Example**: 
- You write code that adds 2 + 2
- Testing checks if it gives 4 (correct) or 5 (wrong)

**In this project**:
- We test if users can login
- We test if teachers can create assignments
- We test if students can only see their own data
- We test if payments work correctly

---

## 🎯 Why Test This Project?

### Reasons:
1. **Catch Bugs Early** - Find problems before users do
2. **Confidence** - Know your changes don't break existing features
3. **Documentation** - Tests show how features should work
4. **RBAC Verification** - Ensure students can't access teacher pages
5. **Data Security** - Verify tenants can't see each other's data

### Real Example:
```
Without Testing:
- You add a new feature
- It breaks the login system
- Users can't access the platform
- Emergency fix needed!

With Testing:
- You add a new feature
- Tests run automatically
- Tests fail, showing login is broken
- You fix it before deploying
- Users never see the problem ✅
```

---

## 📋 Types of Tests

### 1. Unit Tests (60% of tests)
**What**: Test small pieces of code in isolation  
**Example**: Test if a function calculates attendance percentage correctly

```python
def test_attendance_percentage():
    """Test if 8 present days out of 10 = 80%"""
    student = create_test_student()
    create_attendance(student, present=8, absent=2)
    
    result = student.get_attendance_percentage()
    
    assert result == 80.0  # Should be 80%
```

### 2. Integration Tests (30% of tests)
**What**: Test how different parts work together  
**Example**: Test if a teacher can create an assignment and student can see it

```python
def test_assignment_creation_flow():
    """Test complete assignment workflow"""
    # Teacher creates assignment
    teacher = login_as_teacher()
    assignment = teacher.create_assignment("Math Homework")
    
    # Student sees assignment
    student = login_as_student()
    visible_assignments = student.get_assignments()
    
    assert assignment in visible_assignments  # Student should see it
```

### 3. End-to-End Tests (10% of tests)
**What**: Test complete user journeys  
**Example**: Test entire signup process from visiting website to first login

```python
def test_college_signup_flow():
    """Test complete college registration"""
    # 1. Visit pricing page
    response = visit('/pricing')
    assert response.status == 200
    
    # 2. Click signup
    response = click('signup_button')
    
    # 3. Fill form
    fill_form({
        'college_name': 'Test College',
        'email': 'admin@testcollege.com',
        'subdomain': 'testcollege'
    })
    
    # 4. Complete payment
    complete_stripe_payment()
    
    # 5. Should be redirected to onboarding
    assert current_url == '/onboarding'
```

---

## 🛠️ Setup for Testing

### Step 1: Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 2: Install Testing Packages
```bash
pip install pytest pytest-django pytest-cov factory-boy faker
```

### Step 3: Create Test Database
Django automatically creates a test database when you run tests. It's temporary and gets deleted after tests finish.

### Step 4: Configure Pytest
File already exists: `pytest.ini`
```ini
[pytest]
DJANGO_SETTINGS_MODULE = saas_platform.settings
python_files = tests.py test_*.py *_tests.py
```

---

## ▶️ Running Tests

### Basic Commands

#### Run All Tests
```bash
pytest
```
**What it does**: Runs every test in the project  
**Time**: Takes 1-2 minutes  
**Output**: Shows how many passed/failed

#### Run Tests with Details
```bash
pytest -v
```
**What it does**: Shows each test name as it runs  
**Use when**: You want to see which specific tests are running

#### Run One Test File
```bash
pytest tests/unit/test_models.py
```
**What it does**: Only runs tests in that file  
**Use when**: You're working on a specific feature

#### Run One Test Function
```bash
pytest tests/unit/test_models.py::test_user_creation
```
**What it does**: Runs just that one test  
**Use when**: Debugging a specific problem

#### Run Tests with Coverage
```bash
pytest --cov=.
```
**What it does**: Shows which code is tested and which isn't  
**Output**: Percentage of code covered by tests

#### Generate HTML Coverage Report
```bash
pytest --cov=. --cov-report=html
```
**What it does**: Creates a website showing coverage  
**View at**: Open `htmlcov/index.html` in browser

### Advanced Commands

#### Stop on First Failure
```bash
pytest -x
```
**Use when**: You want to fix one problem at a time

#### Re-run Last Failed Tests
```bash
pytest --lf
```
**Use when**: You fixed something and want to check if it works now

#### Run Tests Matching a Pattern
```bash
pytest -k "test_rbac"
```
**What it does**: Runs all tests with "rbac" in the name  
**Example**: Runs test_rbac_student, test_rbac_teacher, etc.

#### Show Print Statements
```bash
pytest -s
```
**What it does**: Shows print() output during tests  
**Use when**: Debugging why a test fails

---

## 📊 Understanding Test Results

### Successful Test Output
```
======================== test session starts ========================
tests/unit/test_models.py::test_user_creation PASSED         [ 33%]
tests/unit/test_models.py::test_attendance PASSED             [ 66%]
tests/unit/test_models.py::test_assignment PASSED             [100%]

======================== 3 passed in 1.23s ========================
```

**What it means**:
- ✅ All 3 tests passed
- Took 1.23 seconds
- Your code is working correctly!

### Failed Test Output
```
======================== test session starts ========================
tests/unit/test_models.py::test_user_creation FAILED         [ 33%]

=========================== FAILURES ================================
___________________ test_user_creation _____________________________

    def test_user_creation():
        user = UserAccount.objects.create(username='test')
>       assert user.email == 'test@example.com'
E       AssertionError: assert None == 'test@example.com'

tests/unit/test_models.py:10: AssertionError
======================== 1 failed in 0.45s =========================
```

**What it means**:
- ❌ Test expected email to be 'test@example.com'
- ❌ But it was None (empty)
- ❌ Fix: Set email when creating user

### Coverage Report
```
Name                      Stmts   Miss  Cover
---------------------------------------------
core/models.py              250     12    95%
core/views.py               180      8    96%
teacher/views.py            150      5    97%
---------------------------------------------
TOTAL                      2500    125    95%
```

**What it means**:
- 95% of code is tested
- 125 lines never run in tests (might need more tests)
- **Good**: Above 80% is excellent
- **Target**: 85%+ coverage

---

## 🧪 Testing Each App

### Testing Core App (Authentication, Base Models)

#### What to Test:
- User login/logout
- User registration
- Role assignment
- Company (tenant) creation
- Multi-tenant isolation

#### Example Tests:

**Test 1: User Can Login**
```python
def test_user_login():
    """Test that user can login with correct password"""
    # Create a test user
    user = create_user(username='test', password='test123')
    
    # Try to login
    client = Client()
    response = client.post('/auth/login/', {
        'username': 'test',
        'password': 'test123'
    })
    
    # Should redirect to dashboard (successful login)
    assert response.status_code == 302
    assert response.url == '/dashboard/'
```

**Test 2: User Cannot Login with Wrong Password**
```python
def test_user_cannot_login_wrong_password():
    """Test that wrong password is rejected"""
    user = create_user(username='test', password='test123')
    
    client = Client()
    response = client.post('/auth/login/', {
        'username': 'test',
        'password': 'wrongpassword'
    })
    
    # Should stay on login page with error
    assert response.status_code == 200
    assert 'Invalid credentials' in response.content
```

**How to Run**:
```bash
pytest tests/unit/test_auth.py -v
```

---

### Testing RBAC (Role-Based Access Control)

#### What to Test:
- Students can't access teacher pages
- Teachers can't access admin pages
- Parents can only see their children's data
- Super admin can see everything

#### Example Tests:

**Test 1: Student Cannot Access Teacher Dashboard**
```python
def test_student_cannot_access_teacher_dashboard():
    """Test that students are blocked from teacher pages"""
    # Login as student
    student = create_user(role='student')
    client = Client()
    client.force_login(student)
    
    # Try to access teacher dashboard
    response = client.get('/teacher/dashboard/')
    
    # Should get 403 Forbidden
    assert response.status_code == 403
    assert 'Access denied' in response.content
```

**Test 2: Teacher Can Access Their Dashboard**
```python
def test_teacher_can_access_dashboard():
    """Test that teachers can access their dashboard"""
    # Login as teacher
    teacher = create_user(role='teacher')
    client = Client()
    client.force_login(teacher)
    
    # Access teacher dashboard
    response = client.get('/teacher/dashboard/')
    
    # Should succeed
    assert response.status_code == 200
    assert 'My Classes' in response.content
```

**How to Run**:
```bash
pytest -k "test_rbac" -v
```

---

### Testing Teacher App

#### What to Test:
- Creating assignments
- Grading submissions
- Marking attendance
- Teachers only see their classes

#### Example Tests:

**Test 1: Teacher Can Create Assignment**
```python
def test_teacher_create_assignment():
    """Test teacher creating a new assignment"""
    # Setup: Create teacher and section
    teacher = create_user(role='teacher')
    section = create_section(name='CS-A')
    section.teachers.add(teacher)
    
    # Login
    client = Client()
    client.force_login(teacher)
    
    # Create assignment
    response = client.post('/teacher/create-assignment/', {
        'title': 'Math Homework',
        'description': 'Solve problems 1-10',
        'section': section.id,
        'due_date': '2025-12-31',
    })
    
    # Should succeed
    assert response.status_code == 302  # Redirect after success
    
    # Verify assignment exists
    assignment = Assignment.objects.get(title='Math Homework')
    assert assignment.teacher == teacher
    assert assignment.section == section
```

**Test 2: Teacher Cannot Grade Other Teacher's Assignment**
```python
def test_teacher_cannot_grade_other_teacher_assignment():
    """Test that teachers can't grade assignments they didn't create"""
    # Teacher 1 creates assignment
    teacher1 = create_user(role='teacher', username='teacher1')
    assignment = Assignment.objects.create(
        title='Math Test',
        teacher=teacher1
    )
    
    # Teacher 2 tries to grade it
    teacher2 = create_user(role='teacher', username='teacher2')
    client = Client()
    client.force_login(teacher2)
    
    submission = create_submission(assignment=assignment)
    response = client.post(f'/teacher/grade/{submission.id}/', {
        'score': 95
    })
    
    # Should be forbidden
    assert response.status_code == 403
```

**How to Run**:
```bash
pytest tests/integration/test_teacher.py -v
```

---

### Testing Student App

#### What to Test:
- Students see only their own data
- Submitting assignments
- Viewing grades
- Viewing attendance

#### Example Tests:

**Test 1: Student Can View Their Grades**
```python
def test_student_view_own_grades():
    """Test student viewing their own grades"""
    # Create student with grades
    student = create_user(role='student')
    grade1 = create_grade(student=student, score=85)
    grade2 = create_grade(student=student, score=90)
    
    # Login
    client = Client()
    client.force_login(student)
    
    # View grades page
    response = client.get('/student/grades/')
    
    # Should see their grades
    assert response.status_code == 200
    assert '85' in response.content
    assert '90' in response.content
```

**Test 2: Student Cannot View Other Student's Grades**
```python
def test_student_cannot_view_other_grades():
    """Test that students can't see other students' grades"""
    # Create two students
    student1 = create_user(role='student', username='student1')
    student2 = create_user(role='student', username='student2')
    
    # Student 2 has grades
    grade = create_grade(student=student2, score=95)
    
    # Student 1 tries to view student 2's grades
    client = Client()
    client.force_login(student1)
    response = client.get(f'/student/grades/{student2.id}/')
    
    # Should be forbidden
    assert response.status_code == 403
```

**How to Run**:
```bash
pytest tests/integration/test_student.py -v
```

---

### Testing Parent App

#### What to Test:
- Parents see only their children's data
- Parents can have multiple children
- Parents cannot see other students

#### Example Tests:

**Test 1: Parent Can View Linked Child**
```python
def test_parent_view_child():
    """Test parent viewing their child's information"""
    # Create parent and child
    parent = create_user(role='parent')
    child = create_user(role='student')
    
    # Link parent to child
    ParentStudentLink.objects.create(
        parent=parent,
        student=child,
        relationship='father'
    )
    
    # Login as parent
    client = Client()
    client.force_login(parent)
    
    # View child's profile
    response = client.get(f'/parent/child/{child.id}/')
    
    # Should succeed
    assert response.status_code == 200
    assert child.get_full_name() in response.content
```

**Test 2: Parent Cannot View Unlinked Student**
```python
def test_parent_cannot_view_unlinked_student():
    """Test parent cannot see students who aren't their children"""
    parent = create_user(role='parent')
    other_student = create_user(role='student')
    
    # NO link created
    
    # Parent tries to view other student
    client = Client()
    client.force_login(parent)
    response = client.get(f'/parent/child/{other_student.id}/')
    
    # Should be forbidden
    assert response.status_code == 403
```

**How to Run**:
```bash
pytest tests/integration/test_parent.py -v
```

---

### Testing Multi-Tenant Isolation

#### What to Test:
- College A cannot see College B's data
- Users belong to one college only
- Cross-tenant access is blocked

#### Example Tests:

**Test 1: Tenant Cannot See Other Tenant's Students**
```python
def test_tenant_isolation():
    """Test that colleges can't see each other's students"""
    # Create two colleges
    college1 = create_company(name='College 1')
    college2 = create_company(name='College 2')
    
    # Create students in each
    student1 = create_user(role='student', company=college1)
    student2 = create_user(role='student', company=college2)
    
    # Create admin for college1
    admin1 = create_user(role='tenant_admin', company=college1)
    
    # Login as admin1
    client = Client()
    client.force_login(admin1)
    
    # Try to view student from college2
    response = client.get(f'/admin/student/{student2.id}/')
    
    # Should not find (404) because different tenant
    assert response.status_code == 404
```

**How to Run**:
```bash
pytest -k "test_tenant" -v
```

---

### Testing Payment Integration

#### What to Test:
- Stripe payment intent creation
- Payment confirmation
- Subscription activation
- Webhook handling

#### Example Tests:

**Test 1: Create Payment Intent**
```python
def test_create_payment_intent():
    """Test Stripe payment intent creation"""
    # Mock Stripe API
    with mock.patch('stripe.PaymentIntent.create') as mock_create:
        mock_create.return_value = {'id': 'pi_123', 'client_secret': 'secret_123'}
        
        # Select plan
        plan = SubscriptionPlan.objects.create(name='Basic', price=99.00)
        
        # Create payment intent
        response = client.post('/api/create-payment-intent/', {
            'plan_id': plan.id
        })
        
        # Should succeed
        assert response.status_code == 200
        assert response.json()['client_secret'] == 'secret_123'
```

**How to Run**:
```bash
pytest tests/integration/test_payments.py -v
```

---

## 🎯 Common Testing Scenarios

### Scenario 1: Testing a New Feature

**You added**: Ability for students to request leave

**Test it**:
```bash
# 1. Write test first
# tests/unit/test_leave.py

def test_student_can_request_leave():
    student = create_user(role='student')
    
    leave = LeaveRequest.objects.create(
        student=student,
        start_date='2025-12-01',
        end_date='2025-12-05',
        reason='Family function'
    )
    
    assert leave.status == 'pending'
    assert leave.student == student

# 2. Run the test
pytest tests/unit/test_leave.py -v

# 3. If it fails, fix your code

# 4. Run again until it passes
```

### Scenario 2: Testing After Making Changes

**You changed**: Modified how attendance percentage is calculated

**Test it**:
```bash
# Run attendance-related tests
pytest -k "attendance" -v

# If all pass, your change didn't break anything
# If some fail, your change broke something - fix it
```

### Scenario 3: Before Deploying to Production

**Always do**:
```bash
# Run ALL tests
pytest

# Check coverage
pytest --cov=. --cov-report=term-missing

# If all pass and coverage > 85%, safe to deploy
# If any fail, DO NOT deploy - fix first
```

---

## 🐛 Debugging Failed Tests

### Step 1: Read the Error Message
```
AssertionError: assert None == 'test@example.com'
```
**Means**: Expected 'test@example.com' but got None

### Step 2: Look at the Line Number
```
tests/unit/test_models.py:10: AssertionError
```
**Go to**: File `tests/unit/test_models.py`, line 10

### Step 3: Add Print Statements
```python
def test_user_creation():
    user = UserAccount.objects.create(username='test')
    print(f"DEBUG: User email is: {user.email}")  # Add this
    assert user.email == 'test@example.com'
```

### Step 4: Run with -s Flag
```bash
pytest tests/unit/test_models.py::test_user_creation -s
```
**Shows**: Your print statements

### Step 5: Fix the Bug
```python
# The problem: Didn't set email when creating user
# Fix: Add email parameter
user = UserAccount.objects.create(
    username='test',
    email='test@example.com'  # Add this
)
```

---

## ✅ Testing Checklist

Before saying "Project is tested":

- [ ] All unit tests pass (pytest)
- [ ] All integration tests pass
- [ ] RBAC tests verify all roles
- [ ] Multi-tenant isolation tests pass
- [ ] Coverage is above 85%
- [ ] No critical security tests fail
- [ ] Payment tests pass (if using Stripe)
- [ ] Can run tests on fresh database
- [ ] Tests run in under 2 minutes
- [ ] Documentation explains what each test does

---

## 📝 Best Practices

### DO:
✅ Write tests for new features  
✅ Run tests before committing code  
✅ Keep tests simple and readable  
✅ Use descriptive test names  
✅ Test both success and failure cases  

### DON'T:
❌ Skip writing tests ("I'll add them later")  
❌ Write tests that depend on each other  
❌ Test external services without mocking  
❌ Ignore failing tests  
❌ Write tests that take forever to run  

---

## 🎓 Summary

**Testing in Simple Steps**:
1. Write code
2. Write test that checks if code works
3. Run test (`pytest`)
4. If test passes ✅ - Great!
5. If test fails ❌ - Fix code and try again
6. Repeat until all tests pass
7. Now you're confident your code works!

**Remember**:
- Tests are your safety net
- They catch bugs before users see them
- They make you confident when changing code
- They document how features should work

**Quick Commands**:
```bash
pytest                      # Run all tests
pytest --cov=.             # With coverage
pytest -k "test_name"      # Run specific test
pytest -v                  # Verbose output
pytest -x                  # Stop on first failure
```

---

**You're now ready to test the entire Django SaaS Platform!** 🚀
