"""
URL Configuration for company_admin app
"""
from django.urls import path
from . import views

app_name = 'company_admin'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Tenant Management
    path('tenants/', views.tenant_list, name='tenant_list'),
    path('tenants/<int:tenant_id>/', views.tenant_detail, name='tenant_detail'),
    
    # Subscription Oversight
    path('subscriptions/', views.subscription_oversight, name='subscription_oversight'),
    
    # User Management
    path('users/', views.user_management, name='user_management'),
    
    # Analytics
    path('analytics/', views.analytics_reporting, name='analytics_reporting'),
    
    # System Settings
    path('settings/', views.system_settings, name='system_settings'),
    
    # Support Tickets
    path('tickets/', views.support_tickets, name='support_tickets'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    
    # Billing
    path('billing/', views.billing_management, name='billing_management'),
    
    # Audit Trail
    path('audit/', views.audit_trail, name='audit_trail'),
    
    # System Health
    path('health/', views.system_health, name='system_health'),
]
