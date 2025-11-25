"""
URL configuration for tenant_subscription app
"""
from django.urls import path
from . import views

app_name = 'subscription'

urlpatterns = [
    # Public pages
    path('', views.pricing_page, name='pricing'),
    path('signup/', views.signup_page, name='signup'),
    path('checkout/', views.checkout_page, name='checkout'),
    path('contact-sales/', views.contact_sales_page, name='contact_sales'),
    
    # Payment API endpoints
    path('api/create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('api/confirm-payment/', views.confirm_payment, name='confirm_payment'),
    
    # Onboarding
    path('onboarding/', views.onboarding_wizard, name='onboarding'),
    path('import-users/', views.import_users_page, name='import_users'),
    path('welcome/', views.welcome_page, name='welcome'),
    
    # Subscription management (requires authentication)
    path('manage/', views.manage_subscription, name='manage'),
    path('cancel/', views.cancel_subscription, name='cancel'),
    
    # Webhook
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
