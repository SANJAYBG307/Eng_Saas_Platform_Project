"""
Health check views for Docker and monitoring
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
import os


def health_check(request):
    """
    Health check endpoint for Docker and load balancers
    Returns 200 if all services are healthy, 503 otherwise
    """
    health_status = {
        'status': 'healthy',
        'services': {}
    }
    
    is_healthy = True
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        is_healthy = False
    
    # Check Redis cache
    try:
        cache.set('health_check', 'ok', 10)
        result = cache.get('health_check')
        if result == 'ok':
            health_status['services']['cache'] = 'healthy'
        else:
            health_status['services']['cache'] = 'unhealthy: cache test failed'
            is_healthy = False
    except Exception as e:
        health_status['services']['cache'] = f'unhealthy: {str(e)}'
        is_healthy = False
    
    # Overall status
    if not is_healthy:
        health_status['status'] = 'unhealthy'
    
    status_code = 200 if is_healthy else 503
    return JsonResponse(health_status, status=status_code)


def readiness_check(request):
    """
    Readiness check for Kubernetes or orchestration systems
    Returns 200 when app is ready to receive traffic
    """
    # Add any initialization checks here
    return JsonResponse({
        'status': 'ready',
        'message': 'Application is ready to receive traffic'
    })


def liveness_check(request):
    """
    Liveness check for Kubernetes or orchestration systems
    Returns 200 if the application is alive
    """
    return JsonResponse({
        'status': 'alive',
        'message': 'Application is running'
    })
