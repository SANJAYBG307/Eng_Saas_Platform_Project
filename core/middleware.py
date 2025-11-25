"""
Middleware for Multi-Tenant SaaS Platform
- TenantMiddleware: Identifies and sets current tenant
- RoleBasedAccessMiddleware: Enforces role-based access control
"""

from django.utils.functional import SimpleLazyObject
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden, JsonResponse
from django.core.cache import cache
from .models import Tenant, TenantDomain
import logging

logger = logging.getLogger(__name__)


def get_tenant_from_request(request):
    """
    Identify tenant from request using:
    1. Subdomain
    2. Custom domain
    3. Session (for tenant admins switching tenants)
    4. Header (for API requests)
    """
    
    # Check if already cached in request
    if hasattr(request, '_cached_tenant'):
        return request._cached_tenant
    
    tenant = None
    
    # Method 1: Check X-Tenant-ID header (for API requests)
    tenant_id = request.headers.get('X-Tenant-ID')
    if tenant_id:
        try:
            tenant = Tenant.objects.get(id=tenant_id, is_active=True)
        except Tenant.DoesNotExist:
            pass
    
    # Method 2: Check subdomain
    if not tenant:
        host = request.get_host().split(':')[0]  # Remove port
        parts = host.split('.')
        
        if len(parts) > 2:  # e.g., college1.saasplatform.com
            subdomain = parts[0]
            if subdomain not in ['www', 'api', 'admin']:
                try:
                    tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
                except Tenant.DoesNotExist:
                    pass
    
    # Method 3: Check custom domain
    if not tenant:
        try:
            tenant_domain = TenantDomain.objects.select_related('tenant').get(
                domain=host,
                is_verified=True,
                is_active=True
            )
            tenant = tenant_domain.tenant
        except TenantDomain.DoesNotExist:
            pass
    
    # Method 4: Check session (for super admin impersonation or testing)
    if not tenant and 'tenant_id' in request.session:
        try:
            tenant = Tenant.objects.get(id=request.session['tenant_id'], is_active=True)
        except Tenant.DoesNotExist:
            pass
    
    # Cache the result
    request._cached_tenant = tenant
    return tenant


class TenantMiddleware:
    """
    Middleware to identify and set current tenant for each request
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get tenant from request
        tenant = get_tenant_from_request(request)
        
        # Attach tenant to request
        request.tenant = tenant
        
        # Set SimpleLazyObject for lazy evaluation
        request.tenant = SimpleLazyObject(lambda: get_tenant_from_request(request))
        
        # Check if tenant is valid and subscription is active
        if tenant:
            # Check subscription status
            if not tenant.is_subscription_active():
                # Allow access to billing and subscription pages
                if not request.path.startswith('/billing/') and not request.path.startswith('/subscription/'):
                    if request.path.startswith('/api/'):
                        return JsonResponse({
                            'error': 'Subscription expired or inactive',
                            'code': 'SUBSCRIPTION_INACTIVE'
                        }, status=403)
                    else:
                        return redirect('subscription:expired')
        
        response = self.get_response(request)
        
        # Add tenant info to response headers (for debugging)
        if tenant and hasattr(response, '__setitem__'):
            response['X-Tenant-Name'] = tenant.name
            response['X-Tenant-ID'] = str(tenant.id)
        
        return response


class RoleBasedAccessMiddleware:
    """
    Middleware to enforce role-based access control
    """
    
    # URL patterns that don't require authentication
    PUBLIC_URLS = [
        '/login/',
        '/logout/',
        '/signup/',
        '/forgot-password/',
        '/reset-password/',
        '/static/',
        '/media/',
        '/pricing/',
        '/',
        '/api/auth/',
    ]
    
    # URL patterns accessible by roles
    ROLE_URL_MAPPING = {
        'super_admin': ['/company/', '/admin/'],  # Company admin has full access
        'tenant_admin': ['/admin/', '/college/'],
        'department_admin': ['/dept/'],
        'teacher': ['/teacher/'],
        'student': ['/student/'],
        'parent': ['/parent/'],
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if URL is public
        if self._is_public_url(request.path):
            return self.get_response(request)
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            if request.path.startswith('/api/'):
                return JsonResponse({'error': 'Authentication required'}, status=401)
            return redirect(f"{reverse('login')}?next={request.path}")
        
        # Super admins have access to everything
        if request.user.is_superuser or (request.user.role and request.user.is_super_admin()):
            return self.get_response(request)
        
        # Check role-based access
        user_role = request.user.role.name if request.user.role else None
        
        if not user_role:
            logger.warning(f"User {request.user.email} has no role assigned")
            return HttpResponseForbidden("Access denied: No role assigned")
        
        # Check if user has access to the requested URL
        if not self._has_url_access(user_role, request.path):
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Access denied',
                    'code': 'INSUFFICIENT_PERMISSIONS'
                }, status=403)
            return HttpResponseForbidden("Access denied: Insufficient permissions")
        
        # Tenant isolation check (except for super_admin)
        if user_role != 'super_admin' and hasattr(request, 'tenant'):
            if request.tenant and request.user.tenant_id != request.tenant.id:
                return HttpResponseForbidden("Access denied: Tenant mismatch")
        
        response = self.get_response(request)
        
        # Add role info to response headers (for debugging)
        if hasattr(response, '__setitem__'):
            response['X-User-Role'] = user_role
        
        return response
    
    def _is_public_url(self, path):
        """Check if URL is public"""
        for public_url in self.PUBLIC_URLS:
            if path.startswith(public_url):
                return True
        return False
    
    def _has_url_access(self, role, path):
        """Check if role has access to the URL"""
        if role not in self.ROLE_URL_MAPPING:
            return False
        
        allowed_prefixes = self.ROLE_URL_MAPPING[role]
        for prefix in allowed_prefixes:
            if path.startswith(prefix):
                return True
        
        return False


class AuditLogMiddleware:
    """
    Middleware to log all actions for audit purposes
    """
    
    # Actions to log
    LOGGED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Log only specific methods
        if request.method in self.LOGGED_METHODS and request.user.is_authenticated:
            self._log_action(request, response)
        
        return response
    
    def _log_action(self, request, response):
        """Log the action to audit log"""
        from .models import AuditLog
        from .utils import get_client_ip
        
        try:
            # Determine action type
            action_map = {
                'POST': 'create',
                'PUT': 'update',
                'PATCH': 'update',
                'DELETE': 'delete',
            }
            action = action_map.get(request.method, 'unknown')
            
            # Create audit log entry
            AuditLog.objects.create(
                user=request.user,
                tenant=getattr(request, 'tenant', None),
                action=action,
                resource_type=request.path.split('/')[1] if len(request.path.split('/')) > 1 else 'unknown',
                description=f"{request.method} {request.path}",
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                status='success' if 200 <= response.status_code < 400 else 'failure'
            )
        except Exception as e:
            logger.error(f"Error logging audit trail: {str(e)}")
