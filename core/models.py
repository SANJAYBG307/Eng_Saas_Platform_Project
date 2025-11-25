"""
Core Models - Multi-Tenant SaaS Platform
Contains: Tenant, UserAccount, Role, Permission, and related models
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


class BaseModel(models.Model):
    """Abstract base model with common fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


class Tenant(BaseModel):
    """
    Tenant Model - Represents a College/Institution
    Each tenant has isolated data
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    subdomain = models.CharField(max_length=63, unique=True, null=True, blank=True)
    
    # Contact Information
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=20)
    website = models.URLField(null=True, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    # Branding
    logo = models.ImageField(upload_to='tenant_logos/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default='#007bff')
    secondary_color = models.CharField(max_length=7, default='#6c757d')
    
    # Subscription Details
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('cancelled', 'Cancelled'),
            ('expired', 'Expired'),
        ],
        default='trial'
    )
    subscription_plan = models.CharField(max_length=50, null=True, blank=True)
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)
    trial_end_date = models.DateField(null=True, blank=True)
    
    # Settings
    timezone = models.CharField(max_length=50, default='Asia/Kolkata')
    date_format = models.CharField(max_length=20, default='DD/MM/YYYY')
    currency = models.CharField(max_length=3, default='INR')
    
    # Academic Year Settings
    academic_year_start_month = models.IntegerField(default=6)  # June
    academic_year_end_month = models.IntegerField(default=5)  # May
    
    # Limits
    max_students = models.IntegerField(default=1000)
    max_teachers = models.IntegerField(default=100)
    max_departments = models.IntegerField(default=10)
    max_storage_gb = models.IntegerField(default=10)
    
    # Usage Tracking
    current_students_count = models.IntegerField(default=0)
    current_teachers_count = models.IntegerField(default=0)
    current_departments_count = models.IntegerField(default=0)
    current_storage_used_gb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    onboarding_completed = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        db_table = 'tenants'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['subdomain']),
            models.Index(fields=['subscription_status']),
        ]
    
    def __str__(self):
        return self.name
    
    def is_subscription_active(self):
        """Check if tenant subscription is active"""
        return self.subscription_status == 'active' and (
            not self.subscription_end_date or 
            self.subscription_end_date >= timezone.now().date()
        )
    
    def days_until_expiry(self):
        """Calculate days until subscription expires"""
        if self.subscription_end_date:
            delta = self.subscription_end_date - timezone.now().date()
            return delta.days
        return None


class TenantDomain(BaseModel):
    """Custom domains for tenants"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='domains')
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'tenant_domains'
        unique_together = ['tenant', 'domain']
    
    def __str__(self):
        return f"{self.domain} -> {self.tenant.name}"


class Role(BaseModel):
    """
    Role Model - Defines user roles in the system
    Roles: super_admin, tenant_admin, department_admin, teacher, student, parent
    """
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('tenant_admin', 'Tenant Admin'),
        ('department_admin', 'Department Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Scope Level
    scope_level = models.IntegerField(
        help_text="1=System, 2=Tenant, 3=Department, 4=Section, 5=Individual",
        default=5
    )
    
    # Permissions flags
    can_manage_tenants = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_manage_departments = models.BooleanField(default=False)
    can_manage_subjects = models.BooleanField(default=False)
    can_manage_attendance = models.BooleanField(default=False)
    can_manage_assessments = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)
    can_manage_billing = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'roles'
        ordering = ['scope_level', 'name']
    
    def __str__(self):
        return self.display_name


class UserAccountManager(BaseUserManager):
    """Custom manager for UserAccount"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class UserAccount(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Custom User Model with Multi-Tenant Support
    """
    # Basic Info
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Profile
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        null=True, blank=True
    )
    
    # Multi-Tenant Relationship
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True, 
        blank=True
    )
    
    # Role
    role = models.ForeignKey(
        Role, 
        on_delete=models.PROTECT, 
        related_name='users',
        null=True
    )
    
    # Django Admin
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Authentication
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, null=True, blank=True)
    
    # Timestamps
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Settings
    language_preference = models.CharField(max_length=10, default='en')
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    objects = UserAccountManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'user_accounts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tenant', 'role']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    def is_super_admin(self):
        return self.role and self.role.name == 'super_admin'
    
    def is_tenant_admin(self):
        return self.role and self.role.name == 'tenant_admin'
    
    def is_department_admin(self):
        return self.role and self.role.name == 'department_admin'
    
    def is_teacher(self):
        return self.role and self.role.name == 'teacher'
    
    def is_student(self):
        return self.role and self.role.name == 'student'
    
    def is_parent(self):
        return self.role and self.role.name == 'parent'


class Department(BaseModel):
    """Department Model - Within a Tenant"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    
    # Department Head
    hod = models.ForeignKey(
        UserAccount, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='departments_headed'
    )
    
    # Contact
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    office_location = models.CharField(max_length=255, null=True, blank=True)
    
    # Metadata
    established_year = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'departments'
        unique_together = ['tenant', 'code']
        ordering = ['name']
        indexes = [
            models.Index(fields=['tenant', 'code']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.tenant.name}"


class Subject(BaseModel):
    """Subject/Course Model"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='subjects')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    
    credits = models.IntegerField(default=3)
    hours_per_week = models.IntegerField(default=3)
    
    # Subject Type
    subject_type = models.CharField(
        max_length=20,
        choices=[
            ('theory', 'Theory'),
            ('practical', 'Practical'),
            ('project', 'Project'),
            ('elective', 'Elective'),
        ],
        default='theory'
    )
    
    # Semester/Year
    semester = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    
    # Syllabus
    syllabus_file = models.FileField(upload_to='syllabi/', null=True, blank=True)
    
    class Meta:
        db_table = 'subjects'
        unique_together = ['tenant', 'department', 'code']
        ordering = ['department', 'semester', 'name']
        indexes = [
            models.Index(fields=['tenant', 'department']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class AcademicYear(BaseModel):
    """Academic Year Model"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='academic_years')
    
    name = models.CharField(max_length=50)  # e.g., "2023-2024"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'academic_years'
        unique_together = ['tenant', 'name']
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} - {self.tenant.name}"


class Section(BaseModel):
    """Section/Batch Model"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sections')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='sections')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='sections')
    
    name = models.CharField(max_length=100)  # e.g., "Section A", "Batch 2023"
    code = models.CharField(max_length=20)
    
    semester = models.IntegerField()
    year = models.IntegerField()
    
    # Capacity
    max_students = models.IntegerField(default=60)
    current_student_count = models.IntegerField(default=0)
    
    # Class Representative
    class_representative = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sections_represented'
    )
    
    class Meta:
        db_table = 'sections'
        unique_together = ['tenant', 'department', 'academic_year', 'code']
        ordering = ['department', 'year', 'semester', 'name']
        indexes = [
            models.Index(fields=['tenant', 'department']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.department.name}"


class TeacherSubjectAssignment(BaseModel):
    """Teacher assigned to teach a subject to a section"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='teacher_assignments')
    teacher = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='subject_assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teacher_assignments')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='teacher_assignments')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='teacher_assignments')
    
    is_primary = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'teacher_subject_assignments'
        unique_together = ['teacher', 'subject', 'section', 'academic_year']
        indexes = [
            models.Index(fields=['tenant', 'teacher']),
            models.Index(fields=['tenant', 'section']),
        ]
    
    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.subject.code} - {self.section.name}"


class StudentEnrollment(BaseModel):
    """Student enrollment in a section"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='student_enrollments')
    student = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='enrollments')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='student_enrollments')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='student_enrollments')
    
    enrollment_date = models.DateField(default=timezone.now)
    roll_number = models.CharField(max_length=50)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('graduated', 'Graduated'),
            ('dropped', 'Dropped'),
        ],
        default='active'
    )
    
    class Meta:
        db_table = 'student_enrollments'
        unique_together = ['tenant', 'student', 'section', 'academic_year']
        indexes = [
            models.Index(fields=['tenant', 'student']),
            models.Index(fields=['tenant', 'section']),
            models.Index(fields=['roll_number']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.section.name}"


class ParentStudentLink(BaseModel):
    """Link between parent and student"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='parent_student_links')
    parent = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='children_links')
    student = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='parents_links')
    
    relationship = models.CharField(
        max_length=20,
        choices=[
            ('father', 'Father'),
            ('mother', 'Mother'),
            ('guardian', 'Guardian'),
        ]
    )
    
    is_primary_contact = models.BooleanField(default=False)
    can_view_grades = models.BooleanField(default=True)
    can_view_attendance = models.BooleanField(default=True)
    can_view_behavior = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'parent_student_links'
        unique_together = ['parent', 'student']
        indexes = [
            models.Index(fields=['tenant', 'parent']),
            models.Index(fields=['tenant', 'student']),
        ]
    
    def __str__(self):
        return f"{self.parent.get_full_name()} -> {self.student.get_full_name()}"


class AuditLog(models.Model):
    """System-wide audit log"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Actor
    user = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, related_name='audit_logs')
    
    # Action
    action = models.CharField(max_length=50)  # create, update, delete, login, logout, etc.
    resource_type = models.CharField(max_length=100)  # Model name
    resource_id = models.CharField(max_length=255, null=True)
    
    # Details
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(null=True)
    changes = models.JSONField(null=True, blank=True)
    
    # Metadata
    status = models.CharField(
        max_length=20,
        choices=[('success', 'Success'), ('failure', 'Failure')],
        default='success'
    )
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['tenant', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
