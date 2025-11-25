"""
Context Processors for Templates
"""

from django.conf import settings


def site_context(request):
    """Add site-wide context variables"""
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_URL': settings.SITE_URL,
        'COMPANY_EMAIL': settings.COMPANY_EMAIL,
        'COMPANY_PHONE': settings.COMPANY_PHONE,
    }


def tenant_context(request):
    """Add tenant-specific context variables"""
    context = {
        'tenant': None,
        'is_tenant_admin': False,
        'is_department_admin': False,
        'is_teacher': False,
        'is_student': False,
        'is_parent': False,
        'is_super_admin': False,
    }
    
    # Add tenant if available
    if hasattr(request, 'tenant'):
        context['tenant'] = request.tenant
    
    # Add user role information
    if request.user.is_authenticated and request.user.role:
        role_name = request.user.role.name
        context['is_super_admin'] = role_name == 'super_admin' or request.user.is_superuser
        context['is_tenant_admin'] = role_name == 'tenant_admin'
        context['is_department_admin'] = role_name == 'department_admin'
        context['is_teacher'] = role_name == 'teacher'
        context['is_student'] = role_name == 'student'
        context['is_parent'] = role_name == 'parent'
        context['user_role'] = role_name
        context['user_role_display'] = request.user.role.display_name
    
    return context
