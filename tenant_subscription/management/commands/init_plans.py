"""
Management command to initialize subscription plans
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from tenant_subscription.models import SubscriptionPlan
from decimal import Decimal


class Command(BaseCommand):
    help = 'Initialize subscription plans with default values'

    def handle(self, *args, **options):
        plans_data = [
            {
                'name': 'Free Trial',
                'slug': 'free-trial',
                'plan_type': 'free',
                'description': 'Try our platform free for 14 days with basic features',
                'price': Decimal('0.00'),
                'billing_period': 'monthly',
                'max_students': 50,
                'max_teachers': 5,
                'max_departments': 2,
                'max_storage_gb': 5,
                'enable_sms': False,
                'enable_email': True,
                'enable_api_access': False,
                'enable_custom_domain': False,
                'enable_white_label': False,
                'enable_analytics': False,
                'enable_advanced_reports': False,
                'enable_parent_portal': False,
                'trial_days': 14,
                'is_popular': False,
                'is_active': True,
                'display_order': 1,
            },
            {
                'name': 'Basic Plan',
                'slug': 'basic',
                'plan_type': 'basic',
                'description': 'Perfect for small institutions getting started',
                'price': Decimal('49.99'),
                'billing_period': 'monthly',
                'max_students': 100,
                'max_teachers': 10,
                'max_departments': 3,
                'max_storage_gb': 10,
                'enable_sms': False,
                'enable_email': True,
                'enable_api_access': False,
                'enable_custom_domain': False,
                'enable_white_label': False,
                'enable_analytics': True,
                'enable_advanced_reports': False,
                'enable_parent_portal': True,
                'trial_days': 14,
                'is_popular': False,
                'is_active': True,
                'display_order': 2,
            },
            {
                'name': 'Standard Plan',
                'slug': 'standard',
                'plan_type': 'standard',
                'description': 'Most popular plan for growing institutions',
                'price': Decimal('99.99'),
                'billing_period': 'monthly',
                'max_students': 500,
                'max_teachers': 50,
                'max_departments': 10,
                'max_storage_gb': 50,
                'enable_sms': True,
                'enable_email': True,
                'enable_api_access': True,
                'enable_custom_domain': False,
                'enable_white_label': False,
                'enable_analytics': True,
                'enable_advanced_reports': True,
                'enable_parent_portal': True,
                'trial_days': 14,
                'is_popular': True,
                'is_active': True,
                'display_order': 3,
            },
            {
                'name': 'Premium Plan',
                'slug': 'premium',
                'plan_type': 'premium',
                'description': 'Advanced features for large institutions',
                'price': Decimal('199.99'),
                'billing_period': 'monthly',
                'max_students': 2000,
                'max_teachers': 200,
                'max_departments': 25,
                'max_storage_gb': 200,
                'enable_sms': True,
                'enable_email': True,
                'enable_api_access': True,
                'enable_custom_domain': True,
                'enable_white_label': True,
                'enable_analytics': True,
                'enable_advanced_reports': True,
                'enable_parent_portal': True,
                'trial_days': 14,
                'is_popular': False,
                'is_active': True,
                'display_order': 4,
            },
            {
                'name': 'Enterprise Plan',
                'slug': 'enterprise',
                'plan_type': 'enterprise',
                'description': 'Unlimited features with dedicated support',
                'price': Decimal('499.99'),
                'billing_period': 'monthly',
                'max_students': 10000,
                'max_teachers': 1000,
                'max_departments': 100,
                'max_storage_gb': 1000,
                'enable_sms': True,
                'enable_email': True,
                'enable_api_access': True,
                'enable_custom_domain': True,
                'enable_white_label': True,
                'enable_analytics': True,
                'enable_advanced_reports': True,
                'enable_parent_portal': True,
                'trial_days': 30,
                'is_popular': False,
                'is_active': True,
                'display_order': 5,
            },
        ]

        created_count = 0
        updated_count = 0

        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.update_or_create(
                slug=plan_data['slug'],
                defaults=plan_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created plan: {plan.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⟳ Updated plan: {plan.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSubscription plans initialization complete!\n'
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )
