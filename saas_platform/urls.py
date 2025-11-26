"""
URL configuration for SaaS Platform - Multi-Tenant Engineering SaaS
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from core.health_views import health_check, readiness_check, liveness_check

urlpatterns = [
    # Health check endpoints
    path('health/', health_check, name='health_check'),
    path('readiness/', readiness_check, name='readiness_check'),
    path('liveness/', liveness_check, name='liveness_check'),
    
    # Django Admin
    path('django-admin/', admin.site.urls),
    
    # Core (Authentication, etc.)
    path('auth/', include('core.urls', namespace='auth')),
    
    # Company Admin App (Super Admin)
    path('company/', include('company_admin.urls', namespace='company_admin')),
    
    # Tenant Subscription App (Public)
    path('', include('tenant_subscription.urls', namespace='subscription')),
    
    # College Management App (Tenant Admin)
    path('admin/', include('college_management.urls', namespace='college')),
    
    # Department Management App (Department Admin/HOD)
    path('dept/', include('department_management.urls', namespace='department')),
    
    # Teacher App
    path('teacher/', include('teacher.urls', namespace='teacher')),
    
    # Student App
    path('student/', include('student.urls', namespace='student')),
    
    # Parent App
    path('parent/', include('parent.urls', namespace='parent'))
    # path('teacher/', include('teacher.urls', namespace='teacher')),
    
    # Student App - TODO: Build
    # path('student/', include('student.urls', namespace='student')),
    
    # Parent App - TODO: Build
    # path('parent/', include('parent.urls', namespace='parent')),
    
    # API Endpoints (if using DRF) - TODO: Build APIs
    # path('api/', include([
    #     path('auth/', include('core.api.urls')),
    #     path('company/', include('company_admin.api.urls')),
    #     path('college/', include('college_management.api.urls')),
    #     path('department/', include('department_management.api.urls')),
    #     path('teacher/', include('teacher.api.urls')),
    #     path('student/', include('student.api.urls')),
    #     path('parent/', include('parent.api.urls')),
    # ])),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Add debug toolbar if installed
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Customize admin site
admin.site.site_header = "Engineering SaaS Platform Admin"
admin.site.site_title = "SaaS Admin Portal"
admin.site.index_title = "Welcome to Engineering SaaS Platform Administration"
