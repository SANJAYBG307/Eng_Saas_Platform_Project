from django.apps import AppConfig


class TenantSubscriptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tenant_subscription'
    verbose_name = 'Tenant Subscription Management'
    
    def ready(self):
        """Import signals when app is ready"""
        import tenant_subscription.signals
