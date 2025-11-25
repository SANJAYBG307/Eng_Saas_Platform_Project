"""
Signals for tenant subscription app
Handles automated actions on subscription events
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import TenantSubscription, Payment, Invoice
from core.models import Tenant
import uuid


@receiver(post_save, sender=TenantSubscription)
def update_tenant_subscription_status(sender, instance, created, **kwargs):
    """
    Update tenant status when subscription changes
    """
    if created:
        # New subscription created
        tenant = instance.tenant
        tenant.subscription_status = instance.status
        tenant.save(update_fields=['subscription_status', 'updated_at'])
    else:
        # Subscription updated
        if instance.status in ['cancelled', 'expired', 'suspended']:
            instance.tenant.subscription_status = instance.status
            instance.tenant.is_active = False
            instance.tenant.save(update_fields=['subscription_status', 'is_active', 'updated_at'])
        elif instance.status in ['trial', 'active']:
            instance.tenant.subscription_status = instance.status
            instance.tenant.is_active = True
            instance.tenant.save(update_fields=['subscription_status', 'is_active', 'updated_at'])


@receiver(post_save, sender=Payment)
def create_invoice_for_payment(sender, instance, created, **kwargs):
    """
    Automatically create invoice when payment is successful
    """
    if created and instance.status == 'succeeded' and instance.subscription:
        # Check if invoice already exists
        if not hasattr(instance, 'invoice'):
            # Generate unique invoice number
            invoice_number = f"INV-{timezone.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Create invoice
            Invoice.objects.create(
                tenant=instance.tenant,
                subscription=instance.subscription,
                payment=instance,
                invoice_number=invoice_number,
                status='paid',
                subtotal=instance.amount,
                tax_amount=0,
                discount_amount=0,
                total=instance.amount,
                currency=instance.currency,
                issue_date=timezone.now().date(),
                due_date=timezone.now().date(),
                paid_date=instance.payment_date or timezone.now(),
                billing_name=instance.tenant.name,
                billing_email=instance.tenant.email,
                billing_address=f"{instance.tenant.address_line1}, {instance.tenant.city}, {instance.tenant.state} {instance.tenant.postal_code}",
                line_items=[
                    {
                        'description': f'Subscription - {instance.subscription.plan.name}',
                        'quantity': 1,
                        'unit_price': float(instance.amount),
                        'total': float(instance.amount)
                    }
                ]
            )


@receiver(pre_save, sender=Invoice)
def check_overdue_invoices(sender, instance, **kwargs):
    """
    Mark invoices as overdue if past due date
    """
    if instance.status == 'pending' and instance.due_date < timezone.now().date():
        instance.status = 'overdue'
