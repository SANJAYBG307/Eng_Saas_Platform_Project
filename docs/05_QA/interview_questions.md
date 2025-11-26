# Interview Questions & Answers

## 🎯 Technical Questions About Your Django SaaS Project

---

## 🏗️ Architecture & Design

### Q1: Explain the overall architecture of your SaaS platform.

**Answer:**
```
The platform follows a multi-layered architecture:

┌─────────────────────────────────────────┐
│         Frontend (Bootstrap 5)          │
│     (Django Templates + JavaScript)     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Django Application Layer           │
│   ┌─────────────────────────────────┐   │
│   │   7 Django Apps (Modular)       │   │
│   │   - company_admin               │   │
│   │   - tenant_subscription         │   │
│   │   - college_management          │   │
│   │   - department_management       │   │
│   │   - teacher                     │   │
│   │   - student                     │   │
│   │   - parent                      │   │
│   └─────────────────────────────────┘   │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │   Custom Middleware             │   │
│   │   - Tenant Identification       │   │
│   │   - Role-Based Access Control   │   │
│   │   - Audit Logging               │   │
│   └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Database Layer                  │
│   ┌──────────────┐  ┌────────────────┐ │
│   │ MySQL 8.0    │  │ Redis Cache    │ │
│   │ (52 Models)  │  │ (Session/Data) │ │
│   └──────────────┘  └────────────────┘ │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Infrastructure Layer               │
│   - Docker Containers (6 services)      │
│   - Nginx Reverse Proxy                 │
│   - Celery Background Tasks             │
│   - Stripe Payment Integration          │
└─────────────────────────────────────────┘
```

**Key Design Principles:**
1. **Separation of Concerns** - Each app handles one domain
2. **Multi-Tenancy** - Schema-based isolation
3. **Role-Based Access Control** - 6 hierarchical roles
4. **Asynchronous Processing** - Celery for heavy tasks
5. **Caching Strategy** - Redis for performance
6. **Microservices-Ready** - Can be split later

---

### Q2: How did you implement multi-tenancy? Why that approach?

**Answer:**

**Approach: Schema-Based Multi-Tenancy**

```python
# Each tenant gets its own database schema
# Example: college1_schema, college2_schema, etc.

# Middleware extracts tenant from subdomain
class TenantMiddleware:
    def __call__(self, request):
        # Extract tenant from domain
        # college1.platform.com → college1
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]
        
        # Get tenant from database
        tenant = Company.objects.get(subdomain=subdomain)
        
        # Switch to tenant's schema
        connection.set_schema(tenant.schema_name)
        
        # Attach to request for views
        request.tenant = tenant
        request.company = tenant
```

**Why Schema-Based?**

| Approach | Pros | Cons | Our Choice |
|----------|------|------|------------|
| **Shared Schema** | Simple, one DB | Security risk, complex queries | ❌ |
| **Separate DBs** | Max isolation | Hard to manage 1000s of DBs | ❌ |
| **Schema-Based** | Good isolation, manageable | Medium complexity | ✅ |

**Benefits:**
1. **Security** - Complete data isolation at DB level
2. **Performance** - Smaller tables per schema, faster queries
3. **Scalability** - Can have thousands of schemas in one DB
4. **Backup/Restore** - Can backup individual tenant
5. **Compliance** - Easier to meet data residency requirements

**Additional Safety Layer:**
```python
# Every model has company FK as extra security
class BaseModel(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True
        
# Auto-filter by company in views
students = Student.objects.filter(company=request.tenant)
```

---

### Q3: Explain your RBAC implementation. How do you enforce permissions?

**Answer:**

**6-Level Role Hierarchy:**

```
super_admin (Company Admin)
    ↓ Manages all tenants
tenant_admin (College Admin)
    ↓ Manages their college
department_admin (HOD)
    ↓ Manages their department
teacher
    ↓ Manages their classes
student
    ↓ Views own data
parent
    ↓ Views children's data
```

**Implementation Layers:**

**1. Database Model:**
```python
class UserAccount(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('tenant_admin', 'Tenant Admin'),
        ('department_admin', 'Department Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
```

**2. Middleware:**
```python
class RoleMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated:
            request.user_role = request.user.role
            request.is_super_admin = request.user.role == 'super_admin'
            request.is_tenant_admin = request.user.role == 'tenant_admin'
            # ... other role checks
```

**3. Decorator:**
```python
def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                raise PermissionDenied("Access denied")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@role_required(['teacher', 'department_admin'])
def create_assignment(request):
    # Only teachers and dept admins can access
    pass
```

**4. Query-Level Filtering:**
```python
# Automatically scope data by role
def get_queryset(request):
    if request.user.role == 'super_admin':
        return Student.objects.all()  # All tenants
    elif request.user.role == 'tenant_admin':
        return Student.objects.filter(company=request.tenant)  # Their college
    elif request.user.role == 'department_admin':
        return Student.objects.filter(
            company=request.tenant,
            department=request.user.department
        )  # Their department
    elif request.user.role == 'teacher':
        return Student.objects.filter(
            section__teachers=request.user
        )  # Their students
    elif request.user.role == 'student':
        return Student.objects.filter(id=request.user.id)  # Only self
    elif request.user.role == 'parent':
        return Student.objects.filter(
            parents__parent=request.user
        )  # Their children
```

**5. Template-Level:**
```django
{% if user.role == 'teacher' %}
    <a href="{% url 'teacher:create_assignment' %}">Create Assignment</a>
{% endif %}

{% if user.role in 'teacher,department_admin,tenant_admin' %}
    <a href="{% url 'teacher:view_all_grades' %}">View All Grades</a>
{% endif %}
```

**Testing RBAC:**
```python
@pytest.mark.rbac
def test_student_cannot_access_teacher_dashboard():
    client = Client()
    student_user = UserAccount.objects.create(role='student')
    client.force_login(student_user)
    
    response = client.get(reverse('teacher:dashboard'))
    
    assert response.status_code == 403  # Forbidden
```

---

## 💾 Database & Models

### Q4: Walk me through your database design. How many models? Key relationships?

**Answer:**

**52 Models Across 8 Apps:**

**Core App (21 models):**
```python
# Authentication & Tenant
- Company (tenant information)
- UserAccount (custom user with role)

# Academic Structure
- AcademicYear
- Department (e.g., Computer Science)
- Subject (e.g., Data Structures)
- Section (e.g., CS-A, CS-B)
- TeacherSectionAssignment (M2M through model)

# Communication
- Announcement
- Message
- Notification

# Relationships
- ParentStudentLink (parent can have multiple children)
```

**Key Relationships:**

```
Company (1) ─────┬──── (*) UserAccount
                 ├──── (*) Department
                 └──── (*) Section

Department (1) ──┬──── (*) UserAccount (students/teachers)
                 └──── (*) Section

Section (*) ─────── (*) Teacher (M2M via TeacherSectionAssignment)
        (1) ─────── (*) Student

Parent (*) ──────── (*) Student (M2M via ParentStudentLink)

Assignment (1) ──── (*) Submission
           (1) ──── (*) Grade

Subject (1) ────── (*) Assignment
        (*) ────── (*) Section (M2M)
```

**College Management (17 models):**
- Staff, Course, Batch, Fee structures, Hostel, Library, etc.

**Subscription (7 models):**
```python
- SubscriptionPlan (Basic, Pro, Enterprise)
- Subscription (active subscription per tenant)
- Payment (Stripe payment records)
- Invoice (billing documents)
```

**Teacher App (5 models):**
- Assignment, Submission, Grade, Attendance, ClassNote

**Student/Parent Apps (2 models each):**
- FeePayment, LeaveRequest

**Design Decisions:**

1. **Every model extends BaseModel:**
```python
class BaseModel(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
```

2. **Soft Deletes:**
- Never hard delete data
- Use `is_active=False` for soft delete
- Can recover accidentally deleted data

3. **Audit Trail:**
- `created_at` and `updated_at` on all models
- Separate AuditLog model for critical actions

4. **Indexes:**
```python
class Student(BaseModel):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL)
    
    class Meta:
        indexes = [
            models.Index(fields=['company', 'section']),  # Common query
            models.Index(fields=['company', 'is_active']),  # Filtering
        ]
```

---

### Q5: How do you handle the parent-child relationship? A parent can have multiple children.

**Answer:**

**Many-to-Many Relationship with Extra Data:**

```python
class ParentStudentLink(BaseModel):
    """
    Links parents to students with relationship type.
    A parent can have multiple children.
    A student can have multiple parents (father, mother, guardian).
    """
    parent = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='children',
        limit_choices_to={'role': 'parent'}
    )
    student = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='parents',
        limit_choices_to={'role': 'student'}
    )
    relationship = models.CharField(
        max_length=20,
        choices=[
            ('father', 'Father'),
            ('mother', 'Mother'),
            ('guardian', 'Legal Guardian'),
            ('other', 'Other'),
        ]
    )
    is_primary_contact = models.BooleanField(default=False)
    can_view_grades = models.BooleanField(default=True)
    can_view_attendance = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['parent', 'student']
```

**Usage in Views:**

**Parent Dashboard:**
```python
@role_required(['parent'])
def parent_dashboard(request):
    # Get all linked children
    children_links = request.user.children.select_related(
        'student',
        'student__section',
        'student__section__department'
    ).all()
    
    children_data = []
    for link in children_links:
        child = link.student
        
        # Aggregate data for each child
        children_data.append({
            'name': child.get_full_name(),
            'relationship': link.get_relationship_display(),
            'section': child.section,
            'attendance': child.get_attendance_percentage(),
            'pending_assignments': Assignment.objects.filter(
                section=child.section,
                submissions__isnull=True
            ).count(),
            'recent_grades': Grade.objects.filter(
                student=child
            ).order_by('-created_at')[:5],
            'fee_dues': FeePayment.objects.filter(
                student=child,
                status='pending'
            ).aggregate(total=Sum('amount'))['total'] or 0,
        })
    
    return render(request, 'parent/dashboard.html', {
        'children': children_data
    })
```

**Switching Between Children:**
```python
@role_required(['parent'])
def view_child_details(request, student_id):
    # Verify parent owns this child
    try:
        link = request.user.children.get(student_id=student_id)
    except ParentStudentLink.DoesNotExist:
        raise PermissionDenied("You don't have access to this student")
    
    child = link.student
    
    # Check permissions
    if not link.can_view_grades:
        # Hide grades section
        pass
    
    return render(request, 'parent/child_detail.html', {
        'child': child,
        'relationship': link.relationship,
        'permissions': {
            'can_view_grades': link.can_view_grades,
            'can_view_attendance': link.can_view_attendance,
        }
    })
```

**Student Side:**
```python
@role_required(['student', 'teacher', 'department_admin'])
def student_profile(request, student_id):
    student = get_object_or_404(UserAccount, id=student_id, role='student')
    
    # Get all parents
    parent_links = student.parents.select_related('parent').all()
    
    context = {
        'student': student,
        'parents': [
            {
                'name': link.parent.get_full_name(),
                'relationship': link.get_relationship_display(),
                'email': link.parent.email,
                'phone': link.parent.phone,
                'is_primary': link.is_primary_contact,
            }
            for link in parent_links
        ]
    }
    
    return render(request, 'student/profile.html', context)
```

**Creating Link (During Onboarding):**
```python
def link_parent_to_student(request):
    if request.method == 'POST':
        form = ParentLinkForm(request.POST)
        if form.is_valid():
            parent_email = form.cleaned_data['parent_email']
            student_id = form.cleaned_data['student_id']
            relationship = form.cleaned_data['relationship']
            
            # Get or create parent user
            parent, created = UserAccount.objects.get_or_create(
                email=parent_email,
                company=request.tenant,
                defaults={
                    'role': 'parent',
                    'username': parent_email.split('@')[0],
                }
            )
            
            # Create link
            ParentStudentLink.objects.create(
                parent=parent,
                student_id=student_id,
                relationship=relationship,
                company=request.tenant,
                is_primary_contact=(relationship in ['father', 'mother'])
            )
            
            # Send invitation email to parent
            if created:
                send_parent_invitation_email(parent)
            
            messages.success(request, f'Parent linked successfully')
            return redirect('student:profile', student_id=student_id)
```

---

## 💳 Payment & Subscription

### Q6: How does the Stripe payment integration work?

**Answer:**

**Complete Subscription Flow:**

**1. Plan Selection:**
```python
# tenant_subscription/views.py
def pricing_page(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    return render(request, 'subscription/pricing.html', {'plans': plans})
```

**2. College Registration:**
```python
def signup_page(request):
    if request.method == 'POST':
        form = CollegeSignupForm(request.POST)
        if form.is_valid():
            # Save college info in session
            request.session['signup_data'] = form.cleaned_data
            request.session['selected_plan'] = request.POST.get('plan_id')
            
            return redirect('subscription:checkout')
    
    return render(request, 'subscription/signup.html', {'form': form})
```

**3. Checkout & Payment Intent:**
```python
def checkout_page(request):
    signup_data = request.session.get('signup_data')
    plan_id = request.session.get('selected_plan')
    plan = SubscriptionPlan.objects.get(id=plan_id)
    
    # Create Stripe customer
    customer = stripe.Customer.create(
        email=signup_data['email'],
        name=signup_data['college_name'],
        metadata={
            'college_name': signup_data['college_name'],
            'plan_id': plan.id,
        }
    )
    
    # Create payment intent
    intent = stripe.PaymentIntent.create(
        amount=int(plan.price * 100),  # Convert to cents
        currency='usd',
        customer=customer.id,
        metadata={
            'plan_id': plan.id,
            'college_name': signup_data['college_name'],
        },
        description=f'{plan.name} Plan Subscription',
    )
    
    return render(request, 'subscription/checkout.html', {
        'client_secret': intent.client_secret,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'plan': plan,
    })
```

**4. Frontend (Stripe.js):**
```javascript
// checkout.html
const stripe = Stripe('{{ stripe_public_key }}');
const elements = stripe.elements();
const cardElement = elements.create('card');
cardElement.mount('#card-element');

const form = document.getElementById('payment-form');
form.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const {error, paymentIntent} = await stripe.confirmCardPayment(
        '{{ client_secret }}',
        {
            payment_method: {
                card: cardElement,
                billing_details: {
                    name: '{{ signup_data.admin_name }}',
                    email: '{{ signup_data.email }}',
                }
            }
        }
    );
    
    if (error) {
        // Show error
        document.getElementById('error-message').textContent = error.message;
    } else if (paymentIntent.status === 'succeeded') {
        // Redirect to confirmation
        window.location.href = '/confirm-payment/?payment_intent=' + paymentIntent.id;
    }
});
```

**5. Payment Confirmation:**
```python
def confirm_payment(request):
    payment_intent_id = request.GET.get('payment_intent')
    
    # Verify with Stripe
    intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    
    if intent.status == 'succeeded':
        signup_data = request.session.get('signup_data')
        plan_id = request.session.get('selected_plan')
        
        # Create Company (Tenant)
        company = Company.objects.create(
            name=signup_data['college_name'],
            subdomain=signup_data['subdomain'],
            schema_name=f"{signup_data['subdomain']}_schema",
            stripe_customer_id=intent.customer,
        )
        
        # Create admin user
        admin = UserAccount.objects.create_user(
            username=signup_data['admin_email'].split('@')[0],
            email=signup_data['admin_email'],
            first_name=signup_data['admin_name'].split()[0],
            last_name=' '.join(signup_data['admin_name'].split()[1:]),
            role='tenant_admin',
            company=company,
        )
        admin.set_password(signup_data['password'])
        admin.save()
        
        # Create subscription
        plan = SubscriptionPlan.objects.get(id=plan_id)
        subscription = Subscription.objects.create(
            company=company,
            plan=plan,
            status='active',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=plan.billing_interval_days),
        )
        
        # Record payment
        Payment.objects.create(
            company=company,
            subscription=subscription,
            amount=plan.price,
            currency='usd',
            stripe_payment_intent_id=payment_intent_id,
            status='succeeded',
        )
        
        # Clear session
        del request.session['signup_data']
        del request.session['selected_plan']
        
        # Redirect to onboarding
        return redirect('subscription:onboarding', company_id=company.id)
    
    return render(request, 'subscription/payment_failed.html')
```

**6. Webhook for Recurring Payments:**
```python
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle events
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        # Update payment status
        Payment.objects.filter(
            stripe_payment_intent_id=payment_intent.id
        ).update(status='succeeded')
        
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        # Handle failed payment
        subscription = Subscription.objects.get(
            company__stripe_customer_id=payment_intent.customer
        )
        subscription.status = 'payment_failed'
        subscription.save()
        
        # Send notification email
        send_payment_failed_email(subscription.company.admin_email)
        
    elif event.type == 'customer.subscription.deleted':
        subscription_obj = event.data.object
        # Cancel subscription
        subscription = Subscription.objects.get(
            stripe_subscription_id=subscription_obj.id
        )
        subscription.status = 'canceled'
        subscription.end_date = timezone.now()
        subscription.save()
    
    return HttpResponse(status=200)
```

**Security Measures:**
1. **PCI Compliance** - Stripe handles card data (never touches our server)
2. **Webhook Signature** - Verify requests are from Stripe
3. **Idempotency** - Use payment_intent_id as unique key
4. **HTTPS Only** - All payment pages force HTTPS
5. **Rate Limiting** - Prevent abuse

---

## 🔧 Technical Implementation

### Q7: How do you handle asynchronous tasks? Give examples.

**Answer:**

**Celery Setup:**

```python
# saas_platform/celery.py
from celery import Celery

app = Celery('saas_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Settings
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'UTC'
```

**Use Cases:**

**1. Email Sending:**
```python
# core/tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_welcome_email(user_id):
    """Send welcome email asynchronously"""
    user = UserAccount.objects.get(id=user_id)
    
    send_mail(
        subject='Welcome to Our Platform',
        message=f'Hello {user.first_name}, welcome!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    
# Usage in view
def signup_view(request):
    user = create_user(...)
    send_welcome_email.delay(user.id)  # Async, non-blocking
```

**2. Bulk CSV Import:**
```python
@shared_task
def import_students_from_csv(file_path, company_id):
    """Import hundreds of students without blocking UI"""
    company = Company.objects.get(id=company_id)
    
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            UserAccount.objects.create(
                username=row['email'].split('@')[0],
                email=row['email'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                role='student',
                company=company,
            )
    
    # Send completion email
    send_mail(
        subject='Student Import Complete',
        message=f'Successfully imported {reader.line_num} students',
        ...
    )

# Usage
def import_users_page(request):
    if request.method == 'POST':
        file = request.FILES['csv_file']
        # Save file
        file_path = handle_uploaded_file(file)
        
        # Trigger async task
        import_students_from_csv.delay(file_path, request.tenant.id)
        
        messages.success(request, 'Import started! You\'ll receive an email when done.')
        return redirect('subscription:welcome')
```

**3. Report Generation:**
```python
@shared_task
def generate_monthly_report(company_id, month, year):
    """Generate PDF report for entire college"""
    company = Company.objects.get(id=company_id)
    
    # Collect data (can take 30-60 seconds)
    students = UserAccount.objects.filter(company=company, role='student').count()
    teachers = UserAccount.objects.filter(company=company, role='teacher').count()
    attendance_avg = Attendance.objects.filter(
        company=company,
        date__month=month,
        date__year=year
    ).aggregate(avg=Avg('percentage'))['avg']
    
    # Generate PDF
    pdf = generate_pdf({
        'students': students,
        'teachers': teachers,
        'attendance_avg': attendance_avg,
        ...
    })
    
    # Upload to S3
    url = upload_to_s3(pdf, f'reports/{company.id}/{month}-{year}.pdf')
    
    # Notify admin
    send_mail(
        subject='Monthly Report Ready',
        message=f'Download: {url}',
        recipient_list=[company.admin_email],
    )

# Usage
@role_required(['tenant_admin'])
def request_report(request):
    generate_monthly_report.delay(
        company_id=request.tenant.id,
        month=request.POST['month'],
        year=request.POST['year']
    )
    messages.success(request, 'Report generation started')
```

**4. Scheduled Tasks (Celery Beat):**
```python
# saas_platform/celery.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-daily-attendance-reminders': {
        'task': 'core.tasks.send_daily_attendance_reminders',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9 AM
    },
    'check-expired-subscriptions': {
        'task': 'tenant_subscription.tasks.check_expired_subscriptions',
        'schedule': crontab(hour=0, minute=0),  # Every day at midnight
    },
    'generate-weekly-reports': {
        'task': 'company_admin.tasks.generate_weekly_reports',
        'schedule': crontab(day_of_week=1, hour=6, minute=0),  # Monday 6 AM
    },
}

# Task implementations
@shared_task
def send_daily_attendance_reminders():
    """Remind teachers who haven't marked attendance"""
    today = timezone.now().date()
    
    # Find teachers with classes today but no attendance marked
    teachers = UserAccount.objects.filter(
        role='teacher',
        section__timetable__day_of_week=today.weekday(),
    ).exclude(
        section__attendance__date=today
    ).distinct()
    
    for teacher in teachers:
        send_mail(
            subject='Reminder: Mark Today\'s Attendance',
            message='You have classes today but haven\'t marked attendance yet.',
            recipient_list=[teacher.email],
        )

@shared_task
def check_expired_subscriptions():
    """Deactivate expired subscriptions"""
    expired = Subscription.objects.filter(
        status='active',
        end_date__lt=timezone.now()
    )
    
    for subscription in expired:
        subscription.status = 'expired'
        subscription.save()
        
        # Notify admin
        send_mail(
            subject='Subscription Expired',
            message='Your subscription has expired. Please renew.',
            recipient_list=[subscription.company.admin_email],
        )
```

**Benefits:**
1. **Non-blocking** - Users don't wait for slow operations
2. **Scalability** - Can add more workers to handle load
3. **Reliability** - Tasks retry on failure
4. **Scheduling** - Automated daily/weekly tasks
5. **Monitoring** - Flower for task monitoring

---

### Q8: How do you optimize database queries? Give examples.

**Answer:**

**Problem: N+1 Queries**

**Bad (Without Optimization):**
```python
# This generates 1 + N queries!
students = Student.objects.all()  # 1 query
for student in students:
    print(student.section.name)  # N queries (one per student)
    print(student.department.name)  # N more queries
```

**Good (With select_related):**
```python
# This generates just 1 query with JOIN
students = Student.objects.select_related(
    'section',
    'section__department'
).all()

for student in students:
    print(student.section.name)  # No additional query
    print(student.section.department.name)  # No additional query
```

**Query Optimization Techniques:**

**1. select_related (for ForeignKey, OneToOne):**
```python
# Student detail page
def student_detail(request, student_id):
    student = UserAccount.objects.select_related(
        'company',
        'section',
        'section__department',
        'section__academicyear'
    ).get(id=student_id)
    
    # All related objects loaded in one query
    # No additional queries when accessing:
    print(student.company.name)
    print(student.section.name)
    print(student.section.department.name)
```

**2. prefetch_related (for ManyToMany, Reverse ForeignKey):**
```python
# Teacher dashboard with all sections
def teacher_dashboard(request):
    teacher = request.user
    
    # Load teacher with all sections and students in 3 queries total
    sections = Section.objects.prefetch_related(
        'students',  # M2M
        'students__parents',  # Reverse FK
        'subjects',  # M2M
    ).filter(teachers=teacher)
    
    # No additional queries when accessing:
    for section in sections:
        for student in section.students.all():
            print(student.name)  # Already loaded
            for parent in student.parents.all():
                print(parent.email)  # Already loaded
```

**3. Prefetch Objects (Custom Prefetch):**
```python
from django.db.models import Prefetch

def student_list_with_recent_grades(request):
    # Load students with only recent grades (not all grades)
    students = UserAccount.objects.prefetch_related(
        Prefetch(
            'grade_set',
            queryset=Grade.objects.select_related('assignment').order_by('-created_at')[:5],
            to_attr='recent_grades'
        )
    ).filter(role='student', company=request.tenant)
    
    for student in students:
        for grade in student.recent_grades:  # Only 5 most recent
            print(f'{grade.assignment.title}: {grade.score}')
```

**4. Annotate (Aggregate Data):**
```python
from django.db.models import Count, Avg, Sum

def section_statistics(request):
    # Calculate stats in database, not Python
    sections = Section.objects.annotate(
        student_count=Count('students'),
        avg_attendance=Avg('students__attendance__percentage'),
        total_assignments=Count('assignment'),
    ).filter(company=request.tenant)
    
    # Stats already calculated
    for section in sections:
        print(f'{section.name}: {section.student_count} students')
        print(f'Avg Attendance: {section.avg_attendance}%')
```

**5. only() and defer():**
```python
# Load only specific fields
def student_name_list(request):
    # Only load name fields, not all user data
    students = UserAccount.objects.only(
        'id', 'first_name', 'last_name', 'email'
    ).filter(role='student', company=request.tenant)
    
    # Much smaller query, faster response

# Defer heavy fields
def student_list_without_profile_pic(request):
    # Don't load profile_picture (large binary field)
    students = UserAccount.objects.defer(
        'profile_picture', 'bio'
    ).filter(role='student', company=request.tenant)
```

**6. Database Indexes:**
```python
class Student(BaseModel):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        indexes = [
            # Composite index for common query
            models.Index(fields=['company', 'section', 'is_active']),
            # Index for filtering
            models.Index(fields=['company', 'created_at']),
        ]
```

**7. Caching:**
```python
from django.core.cache import cache

def get_section_timetable(section_id):
    cache_key = f'timetable_section_{section_id}'
    
    # Check cache first
    timetable = cache.get(cache_key)
    
    if timetable is None:
        # If not cached, query database
        timetable = Timetable.objects.filter(
            section_id=section_id
        ).select_related('subject', 'teacher').all()
        
        # Cache for 1 hour
        cache.set(cache_key, timetable, 3600)
    
    return timetable

# Invalidate cache when updated
def update_timetable(request):
    # ... update logic ...
    
    # Clear cache
    cache.delete(f'timetable_section_{section_id}')
```

**8. Bulk Operations:**
```python
# Bad: N queries
for row in csv_data:
    Student.objects.create(...)  # N INSERT queries

# Good: 1 query
students = [
    Student(name=row['name'], email=row['email'])
    for row in csv_data
]
Student.objects.bulk_create(students)  # 1 INSERT with multiple values

# Bulk update
students = Student.objects.filter(section_id=old_section_id)
students.update(section_id=new_section_id)  # 1 UPDATE query
```

**Monitoring:**
```python
# Django Debug Toolbar shows:
# - Number of queries
# - Query time
# - Duplicate queries
# - Similar queries that could be optimized

# settings.py (dev only)
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

**Result**: Reduced queries from 500+ to 10-15 per page load.

---

## 🧪 Testing

### Q9: What is your testing strategy? How do you test RBAC?

**Answer:**

**Testing Pyramid:**
```
          /\
         /E2E\      10% - End-to-end (full workflows)
        /------\
       /Integration\ 30% - Integration (views, APIs)
      /------------\
     /   Unit Tests  \ 60% - Unit (models, utils)
    /----------------\
```

**Testing Stack:**
- **pytest** - Test framework
- **pytest-django** - Django integration
- **factory_boy** - Test data factories
- **faker** - Realistic fake data
- **pytest-cov** - Coverage reporting

**Test Structure:**

```
tests/
├── conftest.py              # Fixtures
├── unit/
│   ├── test_models.py       # Model methods
│   ├── test_forms.py        # Form validation
│   └── test_utils.py        # Utility functions
├── integration/
│   ├── test_views.py        # View responses
│   ├── test_rbac.py         # Permission tests
│   └── test_api.py          # API endpoints
└── e2e/
    ├── test_signup_flow.py  # Complete signup
    └── test_assignment_flow.py  # Teacher creates, student submits
```

**Fixtures (conftest.py):**
```python
import pytest
from django.test import Client
from core.models import Company, UserAccount

@pytest.fixture
def company():
    """Create a test tenant"""
    return Company.objects.create(
        name='Test College',
        subdomain='testcollege',
        schema_name='testcollege_schema'
    )

@pytest.fixture
def super_admin_user(company):
    """Create super admin user"""
    return UserAccount.objects.create_user(
        username='superadmin',
        email='super@example.com',
        password='testpass123',
        role='super_admin',
        company=company
    )

@pytest.fixture
def tenant_admin_user(company):
    return UserAccount.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='testpass123',
        role='tenant_admin',
        company=company
    )

@pytest.fixture
def teacher_user(company, department):
    return UserAccount.objects.create_user(
        username='teacher',
        email='teacher@example.com',
        password='testpass123',
        role='teacher',
        company=company,
        department=department
    )

@pytest.fixture
def student_user(company, section):
    return UserAccount.objects.create_user(
        username='student',
        email='student@example.com',
        password='testpass123',
        role='student',
        company=company,
        section=section
    )

@pytest.fixture
def authenticated_client(client, user):
    """Client with logged-in user"""
    client.force_login(user)
    return client
```

**RBAC Testing:**

```python
import pytest
from django.urls import reverse
from django.test import Client

@pytest.mark.django_db
class TestRBAC:
    """Test Role-Based Access Control"""
    
    def test_super_admin_can_access_all_tenants(self, super_admin_user):
        client = Client()
        client.force_login(super_admin_user)
        
        response = client.get(reverse('company_admin:dashboard'))
        assert response.status_code == 200
        
        # Should see all companies
        response = client.get(reverse('company_admin:tenant_list'))
        assert response.status_code == 200
    
    def test_tenant_admin_cannot_access_super_admin_pages(self, tenant_admin_user):
        client = Client()
        client.force_login(tenant_admin_user)
        
        response = client.get(reverse('company_admin:dashboard'))
        assert response.status_code == 403  # Forbidden
    
    def test_teacher_can_create_assignment(self, teacher_user, section):
        client = Client()
        client.force_login(teacher_user)
        
        # Assign teacher to section
        section.teachers.add(teacher_user)
        
        response = client.post(reverse('teacher:create_assignment'), {
            'title': 'Test Assignment',
            'description': 'Test description',
            'section': section.id,
            'due_date': '2024-12-31',
        })
        
        assert response.status_code == 302  # Redirect after success
        assert Assignment.objects.filter(title='Test Assignment').exists()
    
    def test_student_cannot_create_assignment(self, student_user):
        client = Client()
        client.force_login(student_user)
        
        response = client.get(reverse('teacher:create_assignment'))
        assert response.status_code == 403  # Forbidden
    
    def test_student_can_only_see_own_grades(self, student_user, another_student):
        client = Client()
        client.force_login(student_user)
        
        # Try to access another student's grades
        response = client.get(
            reverse('student:grades', kwargs={'student_id': another_student.id})
        )
        assert response.status_code == 403
        
        # Can access own grades
        response = client.get(
            reverse('student:grades', kwargs={'student_id': student_user.id})
        )
        assert response.status_code == 200
    
    def test_parent_can_only_see_linked_children(self, parent_user, their_child, other_student):
        client = Client()
        client.force_login(parent_user)
        
        # Link parent to child
        ParentStudentLink.objects.create(
            parent=parent_user,
            student=their_child,
            relationship='father'
        )
        
        # Can see their child
        response = client.get(
            reverse('parent:child_detail', kwargs={'student_id': their_child.id})
        )
        assert response.status_code == 200
        
        # Cannot see other student
        response = client.get(
            reverse('parent:child_detail', kwargs={'student_id': other_student.id})
        )
        assert response.status_code == 403
    
    def test_tenant_isolation(self, company1, company2, user1_company1, user2_company2):
        """Test users from different tenants can't see each other's data"""
        client = Client()
        client.force_login(user1_company1)
        
        # Create student in company2
        student_company2 = UserAccount.objects.create(
            username='student2',
            role='student',
            company=company2
        )
        
        # User from company1 tries to access company2 student
        response = client.get(
            reverse('student:profile', kwargs={'student_id': student_company2.id})
        )
        assert response.status_code == 404  # Not found (filtered by tenant)
```

**Model Testing:**
```python
@pytest.mark.django_db
class TestModels:
    
    def test_student_attendance_percentage(self, student_user):
        """Test attendance percentage calculation"""
        # Create 10 attendance records
        for i in range(10):
            Attendance.objects.create(
                student=student_user,
                date=f'2024-01-{i+1:02d}',
                status='present' if i < 8 else 'absent'  # 80% attendance
            )
        
        assert student_user.get_attendance_percentage() == 80.0
    
    def test_assignment_is_overdue(self, assignment):
        """Test overdue detection"""
        assignment.due_date = timezone.now() - timedelta(days=1)
        assignment.save()
        
        assert assignment.is_overdue() is True
    
    def test_parent_student_link_unique(self, parent_user, student_user):
        """Test can't link same parent-student twice"""
        ParentStudentLink.objects.create(
            parent=parent_user,
            student=student_user,
            relationship='father'
        )
        
        with pytest.raises(IntegrityError):
            ParentStudentLink.objects.create(
                parent=parent_user,
                student=student_user,
                relationship='father'
            )
```

**Integration Testing:**
```python
@pytest.mark.django_db
class TestAssignmentFlow:
    """Test complete assignment workflow"""
    
    def test_teacher_create_assignment_student_submit(
        self, teacher_user, student_user, section
    ):
        # Teacher creates assignment
        teacher_client = Client()
        teacher_client.force_login(teacher_user)
        
        response = teacher_client.post(reverse('teacher:create_assignment'), {
            'title': 'Math Homework',
            'description': 'Solve problems 1-10',
            'section': section.id,
            'due_date': (timezone.now() + timedelta(days=7)).date(),
        })
        
        assignment = Assignment.objects.get(title='Math Homework')
        
        # Student submits assignment
        student_client = Client()
        student_client.force_login(student_user)
        
        response = student_client.post(
            reverse('student:submit_assignment', kwargs={'assignment_id': assignment.id}),
            {
                'content': 'My solutions...',
                'file': SimpleUploadedFile('homework.pdf', b'file content')
            }
        )
        
        assert Submission.objects.filter(
            assignment=assignment,
            student=student_user
        ).exists()
        
        # Teacher grades submission
        submission = Submission.objects.get(assignment=assignment, student=student_user)
        
        response = teacher_client.post(
            reverse('teacher:grade_submission', kwargs={'submission_id': submission.id}),
            {'score': 95, 'feedback': 'Great work!'}
        )
        
        submission.refresh_from_db()
        assert submission.grade.score == 95
```

**Coverage:**
```bash
# Run tests with coverage
pytest --cov=. --cov-report=html

# Results:
# Name                               Stmts   Miss  Cover
# ------------------------------------------------------
# core/models.py                       250     12    95%
# core/views.py                        180      8    96%
# teacher/views.py                     150      5    97%
# company_admin/views.py               120      10   92%
# TOTAL                               2500    125    95%
```

**CI/CD Integration:**
```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_db
        
      redis:
        image: redis:7
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

*Continue to next section...*
