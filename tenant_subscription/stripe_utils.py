"""
Stripe Integration Utilities
Handles Stripe API calls for payments and subscriptions
"""
import stripe
from django.conf import settings
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from .models import (
    SubscriptionPlan, TenantSubscription, Payment,
    PaymentMethod, Invoice
)
import uuid

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service class for Stripe API operations"""
    
    @staticmethod
    def create_customer(tenant, email):
        """
        Create a Stripe customer for a tenant
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=tenant.name,
                metadata={
                    'tenant_id': str(tenant.id),
                    'tenant_name': tenant.name,
                }
            )
            return customer
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe customer creation failed: {str(e)}")
    
    @staticmethod
    def create_subscription(customer_id, price_id, trial_days=None):
        """
        Create a Stripe subscription
        """
        try:
            subscription_data = {
                'customer': customer_id,
                'items': [{'price': price_id}],
                'payment_behavior': 'default_incomplete',
                'expand': ['latest_invoice.payment_intent'],
            }
            
            if trial_days and trial_days > 0:
                subscription_data['trial_period_days'] = trial_days
            
            subscription = stripe.Subscription.create(**subscription_data)
            return subscription
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe subscription creation failed: {str(e)}")
    
    @staticmethod
    def cancel_subscription(subscription_id, at_period_end=False):
        """
        Cancel a Stripe subscription
        """
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe subscription cancellation failed: {str(e)}")
    
    @staticmethod
    def update_subscription(subscription_id, new_price_id):
        """
        Update subscription plan
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': new_price_id,
                }]
            )
            return subscription
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe subscription update failed: {str(e)}")
    
    @staticmethod
    def create_payment_intent(amount, currency='usd', customer_id=None, metadata=None):
        """
        Create a payment intent for one-time payments
        """
        try:
            intent_data = {
                'amount': int(amount * 100),  # Convert to cents
                'currency': currency,
                'automatic_payment_methods': {'enabled': True},
            }
            
            if customer_id:
                intent_data['customer'] = customer_id
            
            if metadata:
                intent_data['metadata'] = metadata
            
            payment_intent = stripe.PaymentIntent.create(**intent_data)
            return payment_intent
        except stripe.error.StripeError as e:
            raise Exception(f"Payment intent creation failed: {str(e)}")
    
    @staticmethod
    def attach_payment_method(payment_method_id, customer_id):
        """
        Attach payment method to customer
        """
        try:
            payment_method = stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id,
            )
            return payment_method
        except stripe.error.StripeError as e:
            raise Exception(f"Payment method attachment failed: {str(e)}")
    
    @staticmethod
    def set_default_payment_method(customer_id, payment_method_id):
        """
        Set default payment method for customer
        """
        try:
            customer = stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    'default_payment_method': payment_method_id,
                },
            )
            return customer
        except stripe.error.StripeError as e:
            raise Exception(f"Setting default payment method failed: {str(e)}")
    
    @staticmethod
    def detach_payment_method(payment_method_id):
        """
        Detach payment method from customer
        """
        try:
            payment_method = stripe.PaymentMethod.detach(payment_method_id)
            return payment_method
        except stripe.error.StripeError as e:
            raise Exception(f"Payment method detachment failed: {str(e)}")
    
    @staticmethod
    def create_coupon(code, discount_type, discount_value, duration='once'):
        """
        Create a Stripe coupon
        """
        try:
            coupon_data = {
                'id': code,
                'duration': duration,
            }
            
            if discount_type == 'percentage':
                coupon_data['percent_off'] = float(discount_value)
            else:
                coupon_data['amount_off'] = int(discount_value * 100)
                coupon_data['currency'] = 'usd'
            
            coupon = stripe.Coupon.create(**coupon_data)
            return coupon
        except stripe.error.StripeError as e:
            raise Exception(f"Coupon creation failed: {str(e)}")
    
    @staticmethod
    def retrieve_invoice(invoice_id):
        """
        Retrieve invoice from Stripe
        """
        try:
            invoice = stripe.Invoice.retrieve(invoice_id)
            return invoice
        except stripe.error.StripeError as e:
            raise Exception(f"Invoice retrieval failed: {str(e)}")
    
    @staticmethod
    def create_refund(payment_intent_id, amount=None, reason=None):
        """
        Create a refund for a payment
        """
        try:
            refund_data = {'payment_intent': payment_intent_id}
            
            if amount:
                refund_data['amount'] = int(amount * 100)
            
            if reason:
                refund_data['reason'] = reason
            
            refund = stripe.Refund.create(**refund_data)
            return refund
        except stripe.error.StripeError as e:
            raise Exception(f"Refund creation failed: {str(e)}")


def handle_stripe_webhook(event_type, data):
    """
    Handle Stripe webhook events
    """
    try:
        if event_type == 'customer.subscription.created':
            handle_subscription_created(data)
        elif event_type == 'customer.subscription.updated':
            handle_subscription_updated(data)
        elif event_type == 'customer.subscription.deleted':
            handle_subscription_deleted(data)
        elif event_type == 'invoice.paid':
            handle_invoice_paid(data)
        elif event_type == 'invoice.payment_failed':
            handle_invoice_payment_failed(data)
        elif event_type == 'payment_intent.succeeded':
            handle_payment_succeeded(data)
        elif event_type == 'payment_intent.payment_failed':
            handle_payment_failed(data)
        else:
            print(f"Unhandled event type: {event_type}")
    except Exception as e:
        print(f"Error handling webhook: {str(e)}")
        raise


def handle_subscription_created(subscription_data):
    """Handle subscription created webhook"""
    stripe_subscription_id = subscription_data['id']
    
    # Update our subscription record
    try:
        tenant_subscription = TenantSubscription.objects.get(
            stripe_subscription_id=stripe_subscription_id
        )
        tenant_subscription.status = 'active' if subscription_data['status'] == 'active' else 'trial'
        tenant_subscription.save()
    except TenantSubscription.DoesNotExist:
        print(f"Subscription not found: {stripe_subscription_id}")


def handle_subscription_updated(subscription_data):
    """Handle subscription updated webhook"""
    stripe_subscription_id = subscription_data['id']
    
    try:
        tenant_subscription = TenantSubscription.objects.get(
            stripe_subscription_id=stripe_subscription_id
        )
        
        # Update status
        status_mapping = {
            'active': 'active',
            'trialing': 'trial',
            'past_due': 'past_due',
            'canceled': 'cancelled',
            'unpaid': 'expired',
        }
        
        stripe_status = subscription_data['status']
        if stripe_status in status_mapping:
            tenant_subscription.status = status_mapping[stripe_status]
        
        # Update dates
        if subscription_data.get('current_period_end'):
            tenant_subscription.next_billing_date = datetime.fromtimestamp(
                subscription_data['current_period_end'], tz=timezone.utc
            )
        
        if subscription_data.get('cancel_at_period_end'):
            tenant_subscription.cancel_at_period_end = subscription_data['cancel_at_period_end']
        
        tenant_subscription.save()
    except TenantSubscription.DoesNotExist:
        print(f"Subscription not found: {stripe_subscription_id}")


def handle_subscription_deleted(subscription_data):
    """Handle subscription deleted webhook"""
    stripe_subscription_id = subscription_data['id']
    
    try:
        tenant_subscription = TenantSubscription.objects.get(
            stripe_subscription_id=stripe_subscription_id
        )
        tenant_subscription.status = 'cancelled'
        tenant_subscription.cancelled_at = timezone.now()
        tenant_subscription.save()
    except TenantSubscription.DoesNotExist:
        print(f"Subscription not found: {stripe_subscription_id}")


def handle_invoice_paid(invoice_data):
    """Handle invoice paid webhook"""
    stripe_invoice_id = invoice_data['id']
    amount = Decimal(invoice_data['amount_paid']) / 100
    
    try:
        # Update existing invoice or create new one
        invoice, created = Invoice.objects.get_or_create(
            stripe_invoice_id=stripe_invoice_id,
            defaults={
                'invoice_number': f"INV-{timezone.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}",
                'status': 'paid',
                'subtotal': amount,
                'total': amount,
                'paid_date': timezone.now(),
            }
        )
        
        if not created:
            invoice.status = 'paid'
            invoice.paid_date = timezone.now()
            invoice.save()
    except Exception as e:
        print(f"Error handling invoice paid: {str(e)}")


def handle_invoice_payment_failed(invoice_data):
    """Handle invoice payment failed webhook"""
    stripe_invoice_id = invoice_data['id']
    
    try:
        invoice = Invoice.objects.get(stripe_invoice_id=stripe_invoice_id)
        invoice.status = 'overdue'
        invoice.save()
    except Invoice.DoesNotExist:
        print(f"Invoice not found: {stripe_invoice_id}")


def handle_payment_succeeded(payment_intent_data):
    """Handle payment succeeded webhook"""
    stripe_payment_intent_id = payment_intent_data['id']
    
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=stripe_payment_intent_id)
        payment.status = 'succeeded'
        payment.payment_date = timezone.now()
        payment.save()
    except Payment.DoesNotExist:
        print(f"Payment not found: {stripe_payment_intent_id}")


def handle_payment_failed(payment_intent_data):
    """Handle payment failed webhook"""
    stripe_payment_intent_id = payment_intent_data['id']
    
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=stripe_payment_intent_id)
        payment.status = 'failed'
        
        # Get failure reason
        if 'last_payment_error' in payment_intent_data:
            error = payment_intent_data['last_payment_error']
            payment.failure_reason = error.get('message', '')
            payment.failure_code = error.get('code', '')
        
        payment.save()
    except Payment.DoesNotExist:
        print(f"Payment not found: {stripe_payment_intent_id}")
