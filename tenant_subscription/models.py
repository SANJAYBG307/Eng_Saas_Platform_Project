"""
Subscription and Payment Models
Handles subscription plans, payments, invoices, and billing
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from core.models import BaseModel, Tenant, UserAccount


class SubscriptionPlan(BaseModel):
    """
    Subscription plans available for tenants
    Defines pricing tiers and features
    """
    PLAN_TYPES = [
        ('free', 'Free Trial'),
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    BILLING_PERIODS = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    billing_period = models.CharField(max_length=20, choices=BILLING_PERIODS)
    
    # Features & Limits
    max_students = models.PositiveIntegerField(default=50)
    max_teachers = models.PositiveIntegerField(default=10)
    max_departments = models.PositiveIntegerField(default=5)
    max_storage_gb = models.PositiveIntegerField(default=10, help_text="Storage limit in GB")
    
    # Feature Flags
    enable_sms = models.BooleanField(default=False)
    enable_email = models.BooleanField(default=True)
    enable_api_access = models.BooleanField(default=False)
    enable_custom_domain = models.BooleanField(default=False)
    enable_white_label = models.BooleanField(default=False)
    enable_analytics = models.BooleanField(default=False)
    enable_advanced_reports = models.BooleanField(default=False)
    enable_parent_portal = models.BooleanField(default=False)
    
    # Trial
    trial_days = models.PositiveIntegerField(default=14)
    
    # Stripe Integration
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Display
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'subscription_plans'
        ordering = ['display_order', 'price']
        indexes = [
            models.Index(fields=['plan_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['display_order']),
        ]
    
    def __str__(self):
        return f"{self.name} - ${self.price}/{self.billing_period}"
    
    def get_monthly_price(self):
        """Calculate equivalent monthly price"""
        if self.billing_period == 'monthly':
            return self.price
        elif self.billing_period == 'quarterly':
            return self.price / 3
        elif self.billing_period == 'annually':
            return self.price / 12
        return self.price
    
    def get_discount_percentage(self):
        """Calculate discount vs monthly billing"""
        if self.billing_period == 'quarterly':
            return 10  # 10% discount
        elif self.billing_period == 'annually':
            return 20  # 20% discount
        return 0


class TenantSubscription(BaseModel):
    """
    Active subscription for a tenant
    Links tenant to their subscription plan
    """
    SUBSCRIPTION_STATUS = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
    ]
    
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    
    # Subscription Details
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='trial')
    
    # Dates
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Stripe Integration
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Billing
    auto_renew = models.BooleanField(default=True)
    
    # Cancellation
    cancel_at_period_end = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'tenant_subscriptions'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['next_billing_date']),
            models.Index(fields=['stripe_subscription_id']),
        ]
    
    def __str__(self):
        return f"{self.tenant.name} - {self.plan.name} ({self.status})"
    
    def is_active(self):
        """Check if subscription is currently active"""
        return self.status in ['trial', 'active']
    
    def is_trial(self):
        """Check if subscription is in trial period"""
        return self.status == 'trial' and self.trial_end_date and self.trial_end_date > timezone.now()
    
    def days_until_expiry(self):
        """Calculate days until subscription expires"""
        if self.end_date:
            delta = self.end_date - timezone.now()
            return max(0, delta.days)
        return None
    
    def can_upgrade(self):
        """Check if tenant can upgrade their plan"""
        return self.status in ['trial', 'active']
    
    def can_downgrade(self):
        """Check if tenant can downgrade their plan"""
        return self.status == 'active'


class Payment(BaseModel):
    """
    Payment transactions for subscriptions
    """
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
    ]
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    subscription = models.ForeignKey(
        TenantSubscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    
    # Payment Details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    currency = models.CharField(max_length=3, default='USD')
    
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    # Stripe Integration
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Transaction Details
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    receipt_url = models.URLField(blank=True, null=True)
    
    # Failure Info
    failure_reason = models.TextField(blank=True, null=True)
    failure_code = models.CharField(max_length=50, blank=True, null=True)
    
    # Refund Info
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    refund_date = models.DateTimeField(null=True, blank=True)
    refund_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]
    
    def __str__(self):
        return f"{self.tenant.name} - ${self.amount} - {self.status}"
    
    def is_successful(self):
        """Check if payment was successful"""
        return self.status == 'succeeded'
    
    def can_refund(self):
        """Check if payment can be refunded"""
        return self.status == 'succeeded' and self.refund_amount < self.amount


class Invoice(BaseModel):
    """
    Invoices for subscription payments
    """
    INVOICE_STATUS = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('void', 'Void'),
    ]
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    subscription = models.ForeignKey(
        TenantSubscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoice'
    )
    
    # Invoice Details
    invoice_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='pending')
    
    # Amounts
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Dates
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    paid_date = models.DateTimeField(null=True, blank=True)
    
    # Stripe Integration
    stripe_invoice_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Billing Details
    billing_name = models.CharField(max_length=200)
    billing_email = models.EmailField()
    billing_address = models.TextField()
    
    # Line Items (stored as JSON)
    line_items = models.JSONField(default=list)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-issue_date', '-created_at']
        indexes = [
            models.Index(fields=['tenant', '-issue_date']),
            models.Index(fields=['status']),
            models.Index(fields=['invoice_number']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.tenant.name}"
    
    def is_overdue(self):
        """Check if invoice is overdue"""
        return self.status == 'pending' and self.due_date < timezone.now().date()
    
    def calculate_total(self):
        """Calculate total from subtotal, tax, and discount"""
        total = self.subtotal
        total += self.tax_amount
        total -= self.discount_amount
        return max(Decimal('0.00'), total)
    
    def save(self, *args, **kwargs):
        """Auto-calculate total before saving"""
        if self.tax_rate > 0:
            self.tax_amount = (self.subtotal * self.tax_rate / 100).quantize(Decimal('0.01'))
        self.total = self.calculate_total()
        super().save(*args, **kwargs)


class PaymentMethod(BaseModel):
    """
    Stored payment methods for tenants
    """
    CARD_TYPES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('discover', 'Discover'),
        ('other', 'Other'),
    ]
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    
    # Card Details (masked for security)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    last_four = models.CharField(max_length=4)
    exp_month = models.PositiveIntegerField()
    exp_year = models.PositiveIntegerField()
    
    # Stripe Integration
    stripe_payment_method_id = models.CharField(max_length=100, unique=True)
    
    # Status
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'payment_methods'
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['tenant', '-is_default']),
        ]
    
    def __str__(self):
        return f"{self.card_type} ending in {self.last_four}"
    
    def is_expired(self):
        """Check if card is expired"""
        now = timezone.now()
        return (self.exp_year < now.year or 
                (self.exp_year == now.year and self.exp_month < now.month))


class Coupon(BaseModel):
    """
    Discount coupons for subscriptions
    """
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Discount Details
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Validity
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Usage Limits
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Null = unlimited")
    times_used = models.PositiveIntegerField(default=0)
    max_uses_per_tenant = models.PositiveIntegerField(default=1)
    
    # Restrictions
    min_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    applicable_plans = models.ManyToManyField(
        SubscriptionPlan,
        blank=True,
        related_name='coupons'
    )
    
    # Stripe Integration
    stripe_coupon_id = models.CharField(max_length=100, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'coupons'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        if self.discount_type == 'percentage':
            return f"{self.code} - {self.discount_value}% off"
        return f"{self.code} - ${self.discount_value} off"
    
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from > now:
            return False
        if self.valid_until and self.valid_until < now:
            return False
        if self.max_uses and self.times_used >= self.max_uses:
            return False
        return True
    
    def calculate_discount(self, amount):
        """Calculate discount amount"""
        if self.discount_type == 'percentage':
            return (amount * self.discount_value / 100).quantize(Decimal('0.01'))
        return min(self.discount_value, amount)


class CouponUsage(BaseModel):
    """
    Track coupon usage by tenants
    """
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='usages'
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='coupon_usages'
    )
    subscription = models.ForeignKey(
        TenantSubscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'coupon_usages'
        ordering = ['-used_at']
        indexes = [
            models.Index(fields=['coupon', 'tenant']),
        ]
    
    def __str__(self):
        return f"{self.coupon.code} used by {self.tenant.name}"
