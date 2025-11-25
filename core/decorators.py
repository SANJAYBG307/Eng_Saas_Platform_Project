"""
Decorators for core app
Role-based access control decorators
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles):
    """
    Decorator to restrict view access based on user roles
    Usage: @role_required(['super_admin', 'tenant_admin'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to continue.')
                return redirect('auth:login')
            
            user_role = request.user.role.name if hasattr(request.user, 'role') else None
            
            if user_role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('auth:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
