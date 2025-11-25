"""
Utility Functions for Core App
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_email_notification(subject, recipient_list, template_name, context, from_email=None):
    """
    Send email notification using template
    
    Args:
        subject: Email subject
        recipient_list: List of recipient emails
        template_name: Template name (without extension)
        context: Context dictionary for template
        from_email: From email address (optional)
    """
    try:
        # Render HTML content
        html_content = render_to_string(f'emails/{template_name}.html', context)
        
        # Render plain text content
        text_content = render_to_string(f'emails/{template_name}.txt', context)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        logger.info(f"Email sent to {recipient_list}: {subject}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False


def generate_unique_code(prefix='', length=8):
    """Generate unique alphanumeric code"""
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(chars) for _ in range(length))
    return f"{prefix}{code}" if prefix else code


def format_file_size(bytes_size):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def calculate_age(date_of_birth):
    """Calculate age from date of birth"""
    from datetime import date
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


def slugify_unique(model, text, slug_field='slug'):
    """Generate unique slug for a model"""
    from django.utils.text import slugify
    
    slug = slugify(text)
    unique_slug = slug
    counter = 1
    
    while model.objects.filter(**{slug_field: unique_slug}).exists():
        unique_slug = f"{slug}-{counter}"
        counter += 1
    
    return unique_slug


def get_current_academic_year(tenant):
    """Get current academic year for a tenant"""
    from .models import AcademicYear
    from django.utils import timezone
    
    try:
        return AcademicYear.objects.get(
            tenant=tenant,
            is_current=True,
            is_active=True
        )
    except AcademicYear.DoesNotExist:
        # Try to find academic year based on current date
        today = timezone.now().date()
        academic_year = AcademicYear.objects.filter(
            tenant=tenant,
            start_date__lte=today,
            end_date__gte=today,
            is_active=True
        ).first()
        
        if academic_year:
            academic_year.is_current = True
            academic_year.save()
        
        return academic_year


def check_user_permission(user, permission_name):
    """
    Check if user has specific permission based on role
    
    Args:
        user: UserAccount instance
        permission_name: Permission name (e.g., 'can_manage_users')
    
    Returns:
        bool: True if user has permission
    """
    if not user.is_authenticated or not user.role:
        return False
    
    # Super admin has all permissions
    if user.is_super_admin() or user.is_superuser:
        return True
    
    # Check role permissions
    return getattr(user.role, permission_name, False)


def create_audit_log(user, action, resource_type, resource_id=None, description='', tenant=None, request=None):
    """
    Create audit log entry
    
    Args:
        user: UserAccount instance
        action: Action type (create, update, delete, etc.)
        resource_type: Type of resource (model name)
        resource_id: ID of the resource
        description: Description of the action
        tenant: Tenant instance
        request: HTTP request object
    """
    from .models import AuditLog
    
    try:
        audit_data = {
            'user': user,
            'tenant': tenant or (user.tenant if user else None),
            'action': action,
            'resource_type': resource_type,
            'resource_id': str(resource_id) if resource_id else None,
            'description': description,
        }
        
        if request:
            audit_data['ip_address'] = get_client_ip(request)
            audit_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        AuditLog.objects.create(**audit_data)
    except Exception as e:
        logger.error(f"Error creating audit log: {str(e)}")


def validate_tenant_limits(tenant, check_type, count=1):
    """
    Validate if tenant can add more resources based on subscription limits
    
    Args:
        tenant: Tenant instance
        check_type: Type of check ('students', 'teachers', 'departments', 'storage')
        count: Number of resources to add (default 1)
    
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if check_type == 'students':
        if tenant.current_students_count + count > tenant.max_students:
            return False, f"Student limit exceeded. Maximum: {tenant.max_students}"
    
    elif check_type == 'teachers':
        if tenant.current_teachers_count + count > tenant.max_teachers:
            return False, f"Teacher limit exceeded. Maximum: {tenant.max_teachers}"
    
    elif check_type == 'departments':
        if tenant.current_departments_count + count > tenant.max_departments:
            return False, f"Department limit exceeded. Maximum: {tenant.max_departments}"
    
    elif check_type == 'storage':
        if tenant.current_storage_used_gb + count > tenant.max_storage_gb:
            return False, f"Storage limit exceeded. Maximum: {tenant.max_storage_gb} GB"
    
    return True, ""


def increment_tenant_usage(tenant, usage_type, count=1):
    """
    Increment tenant usage counter
    
    Args:
        tenant: Tenant instance
        usage_type: Type of usage ('students', 'teachers', 'departments', 'storage')
        count: Amount to increment (default 1)
    """
    from django.db.models import F
    
    if usage_type == 'students':
        tenant.current_students_count = F('current_students_count') + count
    elif usage_type == 'teachers':
        tenant.current_teachers_count = F('current_teachers_count') + count
    elif usage_type == 'departments':
        tenant.current_departments_count = F('current_departments_count') + count
    elif usage_type == 'storage':
        tenant.current_storage_used_gb = F('current_storage_used_gb') + count
    
    tenant.save()
    tenant.refresh_from_db()


def decrement_tenant_usage(tenant, usage_type, count=1):
    """
    Decrement tenant usage counter
    
    Args:
        tenant: Tenant instance
        usage_type: Type of usage ('students', 'teachers', 'departments', 'storage')
        count: Amount to decrement (default 1)
    """
    from django.db.models import F
    
    if usage_type == 'students':
        tenant.current_students_count = F('current_students_count') - count
    elif usage_type == 'teachers':
        tenant.current_teachers_count = F('current_teachers_count') - count
    elif usage_type == 'departments':
        tenant.current_departments_count = F('current_departments_count') - count
    elif usage_type == 'storage':
        tenant.current_storage_used_gb = F('current_storage_used_gb') - count
    
    tenant.save()
    tenant.refresh_from_db()
