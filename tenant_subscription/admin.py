"""
Admin configuration for tenant subscription app
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SubscriptionPlan, TenantSubscription, Payment,
    Invoice, PaymentMethod, Coupon, CouponUsage
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'plan_type', 'price', 'billing_period',
        'max_students', 'max_teachers', 'is_popular', 'is_active', 'display_order'
    ]
    list_filter = ['plan_type', 'billing_period', 'is_popular', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', 'price']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'plan_type', 'description', 'display_order')
        }),
        ('Pricing', {
            'fields': ('price', 'billing_period', 'trial_days')
        }),
        ('Limits', {
            'fields': ('max_students', 'max_teachers', 'max_departments', 'max_storage_gb')
        }),
        ('Features', {
            'fields': (
                'enable_sms', 'enable_email', 'enable_api_access',
                'enable_custom_domain', 'enable_white_label', 'enable_analytics',
                'enable_advanced_reports', 'enable_parent_portal'
            ),
            'classes': ('collapse',)
        }),
        ('Stripe Integration', {
            'fields': ('stripe_price_id', 'stripe_product_id'),
            'classes': ('collapse',)
        }),
        ('Display', {
            'fields': ('is_popular', 'is_active')
        }),
    )


@admin.register(TenantSubscription)
class TenantSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'tenant', 'plan', 'status', 'start_date',
        'trial_end_date', 'next_billing_date', 'auto_renew'
    ]
    list_filter = ['status', 'auto_renew', 'cancel_at_period_end']
    search_fields = ['tenant__name', 'plan__name', 'stripe_subscription_id']
    readonly_fields = ['start_date', 'cancelled_at', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Subscription Details', {
            'fields': ('tenant', 'plan', 'status')
        }),
        ('Dates', {
            'fields': (
                'start_date', 'end_date', 'trial_end_date',
                'next_billing_date', 'cancelled_at'
            )
        }),
        ('Billing', {
            'fields': ('auto_renew', 'cancel_at_period_end')
        }),
        ('Cancellation', {
            'fields': ('cancellation_reason',),
            'classes': ('collapse',)
        }),
        ('Stripe Integration', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'tenant', 'amount_display',
        'status', 'payment_method', 'payment_date', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = [
        'transaction_id', 'tenant__name',
        'stripe_payment_intent_id', 'stripe_charge_id'
    ]
    readonly_fields = [
        'transaction_id', 'payment_date', 'created_at',
        'updated_at', 'stripe_payment_intent_id', 'stripe_charge_id'
    ]
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Payment Details', {
            'fields': (
                'tenant', 'subscription', 'amount', 'currency',
                'status', 'payment_method'
            )
        }),
        ('Transaction', {
            'fields': ('transaction_id', 'payment_date', 'description', 'receipt_url')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id'),
            'classes': ('collapse',)
        }),
        ('Failure Information', {
            'fields': ('failure_reason', 'failure_code'),
            'classes': ('collapse',)
        }),
        ('Refund Information', {
            'fields': ('refund_amount', 'refund_date', 'refund_reason'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def amount_display(self, obj):
        return f"${obj.amount} {obj.currency}"
    amount_display.short_description = 'Amount'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'tenant', 'total_display',
        'status', 'issue_date', 'due_date', 'paid_date'
    ]
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = ['invoice_number', 'tenant__name', 'billing_email']
    readonly_fields = [
        'invoice_number', 'issue_date', 'paid_date',
        'created_at', 'updated_at'
    ]
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Invoice Details', {
            'fields': ('invoice_number', 'tenant', 'subscription', 'payment', 'status')
        }),
        ('Amounts', {
            'fields': (
                'subtotal', 'tax_rate', 'tax_amount',
                'discount_amount', 'total', 'currency'
            )
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'paid_date')
        }),
        ('Billing Information', {
            'fields': ('billing_name', 'billing_email', 'billing_address')
        }),
        ('Line Items', {
            'fields': ('line_items',),
            'classes': ('collapse',)
        }),
        ('Stripe Integration', {
            'fields': ('stripe_invoice_id',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_display(self, obj):
        if obj.is_overdue():
            return format_html(
                '<span style="color: red; font-weight: bold;">${} {} (OVERDUE)</span>',
                obj.total, obj.currency
            )
        return f"${obj.total} {obj.currency}"
    total_display.short_description = 'Total'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [
        'tenant', 'card_display', 'expiry_display',
        'is_default', 'is_active'
    ]
    list_filter = ['card_type', 'is_default', 'is_active']
    search_fields = ['tenant__name', 'last_four', 'stripe_payment_method_id']
    readonly_fields = ['stripe_payment_method_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Payment Method Details', {
            'fields': ('tenant', 'card_type', 'last_four', 'exp_month', 'exp_year')
        }),
        ('Status', {
            'fields': ('is_default', 'is_active')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_payment_method_id',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def card_display(self, obj):
        return f"{obj.card_type} •••• {obj.last_four}"
    card_display.short_description = 'Card'
    
    def expiry_display(self, obj):
        if obj.is_expired():
            return format_html(
                '<span style="color: red;">Expired ({}/{})</span>',
                obj.exp_month, obj.exp_year
            )
        return f"{obj.exp_month}/{obj.exp_year}"
    expiry_display.short_description = 'Expiry'


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'discount_display', 'times_used',
        'max_uses', 'valid_from', 'valid_until', 'is_active'
    ]
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['times_used', 'created_at', 'updated_at']
    filter_horizontal = ['applicable_plans']
    
    fieldsets = (
        ('Coupon Details', {
            'fields': ('code', 'name', 'description')
        }),
        ('Discount', {
            'fields': ('discount_type', 'discount_value', 'min_purchase_amount')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'times_used', 'max_uses_per_tenant')
        }),
        ('Restrictions', {
            'fields': ('applicable_plans',),
            'classes': ('collapse',)
        }),
        ('Stripe Integration', {
            'fields': ('stripe_coupon_id',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return f"{obj.discount_value}% off"
        return f"${obj.discount_value} off"
    discount_display.short_description = 'Discount'


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'tenant', 'subscription', 'discount_amount', 'used_at']
    list_filter = ['used_at']
    search_fields = ['coupon__code', 'tenant__name']
    readonly_fields = ['used_at', 'created_at', 'updated_at']
    date_hierarchy = 'used_at'
    
    fieldsets = (
        ('Usage Details', {
            'fields': ('coupon', 'tenant', 'subscription', 'discount_amount', 'used_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
