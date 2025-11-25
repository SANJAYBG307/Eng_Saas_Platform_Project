"""
Django Admin Configuration for Core Models
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    Tenant, TenantDomain, Role, UserAccount, Department, Subject,
    AcademicYear, Section, TeacherSubjectAssignment, StudentEnrollment,
    ParentStudentLink, AuditLog
)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'subscription_status', 'subscription_end_date', 'is_active', 'created_at']
    list_filter = ['subscription_status', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'email', 'subdomain']
    readonly_fields = ['id', 'created_at', 'updated_at', 'current_students_count', 'current_teachers_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'subdomain', 'logo')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code')
        }),
        ('Branding', {
            'fields': ('primary_color', 'secondary_color')
        }),
        ('Subscription', {
            'fields': (
                'subscription_status', 'subscription_plan', 
                'subscription_start_date', 'subscription_end_date', 
                'trial_end_date', 'stripe_customer_id'
            )
        }),
        ('Limits & Usage', {
            'fields': (
                'max_students', 'current_students_count',
                'max_teachers', 'current_teachers_count',
                'max_departments', 'current_departments_count',
                'max_storage_gb', 'current_storage_used_gb'
            )
        }),
        ('Settings', {
            'fields': ('timezone', 'date_format', 'currency', 'academic_year_start_month', 'academic_year_end_month')
        }),
        ('Metadata', {
            'fields': ('is_active', 'onboarding_completed', 'id', 'created_at', 'updated_at')
        }),
    )


@admin.register(TenantDomain)
class TenantDomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary', 'is_verified', 'is_active']
    list_filter = ['is_primary', 'is_verified', 'is_active']
    search_fields = ['domain', 'tenant__name']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'scope_level', 'is_active']
    list_filter = ['scope_level', 'is_active']
    search_fields = ['name', 'display_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'description', 'scope_level')
        }),
        ('Permissions', {
            'fields': (
                'can_manage_tenants', 'can_manage_users', 'can_manage_departments',
                'can_manage_subjects', 'can_manage_attendance', 'can_manage_assessments',
                'can_view_reports', 'can_manage_billing'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(UserAccount)
class UserAccountAdmin(BaseUserAdmin):
    list_display = ['email', 'get_full_name', 'role', 'tenant', 'is_active', 'email_verified', 'date_joined']
    list_filter = ['role', 'is_active', 'email_verified', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    readonly_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone', 'date_of_birth', 'gender', 'profile_picture')
        }),
        ('Role & Tenant', {
            'fields': ('role', 'tenant')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Security', {
            'fields': ('email_verified', 'phone_verified', 'two_factor_enabled')
        }),
        ('Preferences', {
            'fields': ('language_preference', 'notification_preferences')
        }),
        ('Metadata', {
            'fields': ('id', 'date_joined', 'last_login', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'tenant'),
        }),
    )
    
    ordering = ['-created_at']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'tenant', 'hod', 'is_active', 'created_at']
    list_filter = ['tenant', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'tenant__name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'subject_type', 'credits', 'semester', 'is_active']
    list_filter = ['department', 'subject_type', 'semester', 'year', 'is_active']
    search_fields = ['name', 'code', 'department__name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'start_date', 'end_date', 'is_current', 'is_active']
    list_filter = ['tenant', 'is_current', 'is_active']
    search_fields = ['name', 'tenant__name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'semester', 'year', 'current_student_count', 'max_students', 'is_active']
    list_filter = ['department', 'academic_year', 'semester', 'year', 'is_active']
    search_fields = ['name', 'code', 'department__name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(TeacherSubjectAssignment)
class TeacherSubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'section', 'academic_year', 'is_primary', 'is_active']
    list_filter = ['academic_year', 'is_primary', 'is_active']
    search_fields = ['teacher__first_name', 'teacher__last_name', 'subject__name', 'section__name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'section', 'roll_number', 'academic_year', 'status', 'is_active']
    list_filter = ['academic_year', 'status', 'is_active']
    search_fields = ['student__first_name', 'student__last_name', 'roll_number', 'section__name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ParentStudentLink)
class ParentStudentLinkAdmin(admin.ModelAdmin):
    list_display = ['parent', 'student', 'relationship', 'is_primary_contact', 'is_active']
    list_filter = ['relationship', 'is_primary_contact', 'is_active']
    search_fields = ['parent__first_name', 'parent__last_name', 'student__first_name', 'student__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource_type', 'status', 'timestamp']
    list_filter = ['action', 'resource_type', 'status', 'timestamp']
    search_fields = ['user__email', 'description', 'resource_type']
    readonly_fields = ['id', 'timestamp', 'user', 'tenant', 'action', 'resource_type', 'resource_id', 
                       'description', 'ip_address', 'user_agent', 'changes', 'status']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
