"""
Views for tenant subscription app
Handles all subscription-related pages and workflows
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from datetime import timedelta
import stripe
import json
import csv
import io

from .models import (
    SubscriptionPlan, TenantSubscription, Payment,
    Invoice, PaymentMethod, Coupon, CouponUsage
)
from .forms import (
    TenantSignupForm, CouponForm, CancelSubscriptionForm,
    ContactSalesForm, ImportUsersForm
)
from .stripe_utils import StripeService
from core.models import Tenant, UserAccount, Role
from core.utils import send_email_notification


def pricing_page(request):
    """
    Landing/Pricing Page
    Display all subscription plans
    """
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('display_order')
    
    context = {
        'plans': plans,
        'page_title': 'Pricing Plans',
    }
    return render(request, 'subscription/pricing.html', context)


def signup_page(request):
    """
    Signup Page
    New tenant registration
    """
    plan_id = request.GET.get('plan')
    plan = None
    
    if plan_id:
        plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    if request.method == 'POST':
        form = TenantSignupForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create tenant
                    tenant = Tenant.objects.create(
                        name=form.cleaned_data['institution_name'],
                        slug=form.cleaned_data['subdomain'],
                        subdomain=form.cleaned_data['subdomain'],
                        email=form.cleaned_data['email'],
                        phone=form.cleaned_data['phone'],
                        address_line1=form.cleaned_data['address_line1'],
                        address_line2=form.cleaned_data['address_line2'],
                        city=form.cleaned_data['city'],
                        state=form.cleaned_data['state'],
                        postal_code=form.cleaned_data['postal_code'],
                        country=form.cleaned_data['country'],
                        subscription_status='trial',
                        is_active=True
                    )
                    
                    # Get tenant_admin role
                    tenant_admin_role = Role.objects.get(name='tenant_admin')
                    
                    # Create admin user
                    admin_user = UserAccount.objects.create_user(
                        email=form.cleaned_data['admin_email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        tenant=tenant,
                        role=tenant_admin_role,
                        is_active=True,
                        email_verified=False
                    )
                    
                    # Store tenant and plan in session
                    request.session['signup_tenant_id'] = str(tenant.id)
                    if plan:
                        request.session['signup_plan_id'] = str(plan.id)
                    
                    messages.success(request, 'Account created successfully! Please complete payment.')
                    return redirect('subscription:checkout')
                    
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
    else:
        form = TenantSignupForm()
    
    context = {
        'form': form,
        'plan': plan,
        'page_title': 'Sign Up',
    }
    return render(request, 'subscription/signup.html', context)


def checkout_page(request):
    """
    Payment Checkout Page
    Stripe payment integration
    """
    tenant_id = request.session.get('signup_tenant_id')
    plan_id = request.session.get('signup_plan_id')
    
    if not tenant_id:
        messages.error(request, 'Please sign up first.')
        return redirect('subscription:signup')
    
    tenant = get_object_or_404(Tenant, id=tenant_id)
    plan = None
    if plan_id:
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    else:
        # Default to free trial
        plan = SubscriptionPlan.objects.filter(plan_type='free').first()
    
    if request.method == 'POST':
        coupon_form = CouponForm(request.POST)
        if coupon_form.is_valid():
            coupon = coupon_form.cleaned_data['coupon_code']
            request.session['coupon_id'] = str(coupon.id)
            messages.success(request, f'Coupon {coupon.code} applied!')
            return redirect('subscription:checkout')
    else:
        coupon_form = CouponForm()
    
    # Calculate pricing
    subtotal = plan.price
    discount = 0
    coupon = None
    
    coupon_id = request.session.get('coupon_id')
    if coupon_id:
        coupon = Coupon.objects.filter(id=coupon_id).first()
        if coupon and coupon.is_valid():
            discount = coupon.calculate_discount(subtotal)
    
    total = subtotal - discount
    
    # Initialize Stripe
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    
    context = {
        'tenant': tenant,
        'plan': plan,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'coupon': coupon,
        'coupon_form': coupon_form,
        'stripe_public_key': stripe_public_key,
        'page_title': 'Checkout',
    }
    return render(request, 'subscription/checkout.html', context)


@require_http_methods(["POST"])
def create_payment_intent(request):
    """
    API endpoint to create Stripe payment intent
    """
    try:
        data = json.loads(request.body)
        plan_id = data.get('plan_id')
        tenant_id = data.get('tenant_id')
        
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        tenant = get_object_or_404(Tenant, id=tenant_id)
        
        # Calculate amount
        amount = plan.price
        coupon_id = request.session.get('coupon_id')
        if coupon_id:
            coupon = Coupon.objects.filter(id=coupon_id).first()
            if coupon and coupon.is_valid():
                discount = coupon.calculate_discount(amount)
                amount -= discount
        
        # Create or get Stripe customer
        if not tenant.subscription or not tenant.subscription.stripe_customer_id:
            customer = StripeService.create_customer(tenant, tenant.email)
            stripe_customer_id = customer.id
        else:
            stripe_customer_id = tenant.subscription.stripe_customer_id
        
        # Create payment intent
        payment_intent = StripeService.create_payment_intent(
            amount=float(amount),
            currency='usd',
            customer_id=stripe_customer_id,
            metadata={
                'tenant_id': str(tenant.id),
                'plan_id': str(plan.id),
            }
        )
        
        return JsonResponse({
            'clientSecret': payment_intent.client_secret,
            'customer_id': stripe_customer_id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
def confirm_payment(request):
    """
    Confirm payment and create subscription
    """
    try:
        data = json.loads(request.body)
        payment_intent_id = data.get('payment_intent_id')
        tenant_id = data.get('tenant_id')
        plan_id = data.get('plan_id')
        
        tenant = get_object_or_404(Tenant, id=tenant_id)
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        
        with transaction.atomic():
            # Create subscription
            trial_end = timezone.now() + timedelta(days=plan.trial_days)
            subscription = TenantSubscription.objects.create(
                tenant=tenant,
                plan=plan,
                status='trial' if plan.trial_days > 0 else 'active',
                trial_end_date=trial_end if plan.trial_days > 0 else None,
                stripe_subscription_id=payment_intent_id,
            )
            
            # Create payment record
            payment = Payment.objects.create(
                tenant=tenant,
                subscription=subscription,
                amount=plan.price,
                currency='USD',
                status='succeeded',
                payment_method='stripe',
                stripe_payment_intent_id=payment_intent_id,
                transaction_id=f'TXN-{timezone.now().strftime("%Y%m%d")}-{payment_intent_id[:8]}',
                payment_date=timezone.now()
            )
            
            # Apply coupon if exists
            coupon_id = request.session.get('coupon_id')
            if coupon_id:
                coupon = Coupon.objects.filter(id=coupon_id).first()
                if coupon:
                    discount = coupon.calculate_discount(plan.price)
                    CouponUsage.objects.create(
                        coupon=coupon,
                        tenant=tenant,
                        subscription=subscription,
                        discount_amount=discount
                    )
                    coupon.times_used += 1
                    coupon.save()
            
            # Clear session
            if 'signup_tenant_id' in request.session:
                del request.session['signup_tenant_id']
            if 'signup_plan_id' in request.session:
                del request.session['signup_plan_id']
            if 'coupon_id' in request.session:
                del request.session['coupon_id']
        
        return JsonResponse({'success': True, 'redirect_url': '/subscription/onboarding/'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def onboarding_wizard(request):
    """
    Onboarding Wizard Page
    Step-by-step setup guide
    """
    if request.user.role.name != 'tenant_admin':
        messages.error(request, 'Access denied. Only tenant admins can access onboarding.')
        return redirect('core:dashboard')
    
    tenant = request.user.tenant
    
    # Check onboarding steps completion
    onboarding_steps = {
        'profile_complete': bool(tenant.logo and tenant.primary_color),
        'departments_added': tenant.departments.count() > 0,
        'teachers_added': UserAccount.objects.filter(tenant=tenant, role__name='teacher').count() > 0,
        'students_added': UserAccount.objects.filter(tenant=tenant, role__name='student').count() > 0,
    }
    
    progress = sum(onboarding_steps.values()) / len(onboarding_steps) * 100
    
    context = {
        'tenant': tenant,
        'onboarding_steps': onboarding_steps,
        'progress': progress,
        'page_title': 'Onboarding Wizard',
    }
    return render(request, 'subscription/onboarding.html', context)


@login_required
def import_users_page(request):
    """
    Import Users Page
    Bulk import teachers/students from CSV
    """
    if request.user.role.name != 'tenant_admin':
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = ImportUsersForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            user_type = form.cleaned_data['user_type']
            send_welcome = form.cleaned_data['send_welcome_email']
            
            try:
                # Read CSV
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                
                imported_count = 0
                errors = []
                
                # Get role
                role = Role.objects.get(name=user_type)
                
                for row in reader:
                    try:
                        # Create user
                        user = UserAccount.objects.create_user(
                            email=row['email'],
                            password=row.get('password', 'TempPass123!'),
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            tenant=request.user.tenant,
                            role=role,
                            phone=row.get('phone', ''),
                            is_active=True
                        )
                        
                        if send_welcome:
                            send_email_notification(
                                to_email=user.email,
                                subject='Welcome to our platform',
                                message=f'Your account has been created. Email: {user.email}'
                            )
                        
                        imported_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {reader.line_num}: {str(e)}")
                
                if imported_count > 0:
                    messages.success(request, f'Successfully imported {imported_count} users!')
                if errors:
                    messages.warning(request, f'Errors: {", ".join(errors[:5])}')
                
                return redirect('subscription:import_users')
                
            except Exception as e:
                messages.error(request, f'Error processing CSV: {str(e)}')
    else:
        form = ImportUsersForm()
    
    context = {
        'form': form,
        'page_title': 'Import Users',
    }
    return render(request, 'subscription/import_users.html', context)


@login_required
def welcome_page(request):
    """
    Welcome Page
    Post-onboarding welcome screen
    """
    tenant = request.user.tenant
    subscription = tenant.subscription if hasattr(tenant, 'subscription') else None
    
    context = {
        'tenant': tenant,
        'subscription': subscription,
        'page_title': 'Welcome',
    }
    return render(request, 'subscription/welcome.html', context)


def contact_sales_page(request):
    """
    Contact Sales Page
    Enterprise inquiries
    """
    if request.method == 'POST':
        form = ContactSalesForm(request.POST)
        if form.is_valid():
            # Send email to sales team
            send_email_notification(
                to_email=settings.SALES_EMAIL if hasattr(settings, 'SALES_EMAIL') else settings.DEFAULT_FROM_EMAIL,
                subject=f'Sales Inquiry from {form.cleaned_data["institution_name"]}',
                message=f"""
                New sales inquiry:
                
                Name: {form.cleaned_data['name']}
                Email: {form.cleaned_data['email']}
                Phone: {form.cleaned_data['phone']}
                Institution: {form.cleaned_data['institution_name']}
                Students: {form.cleaned_data['number_of_students']}
                
                Message:
                {form.cleaned_data['message']}
                """
            )
            
            messages.success(request, 'Thank you! Our sales team will contact you shortly.')
            return redirect('subscription:contact_sales')
    else:
        form = ContactSalesForm()
    
    context = {
        'form': form,
        'page_title': 'Contact Sales',
    }
    return render(request, 'subscription/contact_sales.html', context)


@login_required
def manage_subscription(request):
    """
    Subscription management dashboard
    """
    tenant = request.user.tenant
    subscription = get_object_or_404(TenantSubscription, tenant=tenant)
    
    # Get recent payments
    payments = Payment.objects.filter(tenant=tenant).order_by('-created_at')[:5]
    
    # Get recent invoices
    invoices = Invoice.objects.filter(tenant=tenant).order_by('-issue_date')[:5]
    
    context = {
        'subscription': subscription,
        'payments': payments,
        'invoices': invoices,
        'page_title': 'Manage Subscription',
    }
    return render(request, 'subscription/manage.html', context)


@login_required
@require_http_methods(["POST"])
def cancel_subscription(request):
    """
    Cancel subscription
    """
    tenant = request.user.tenant
    subscription = get_object_or_404(TenantSubscription, tenant=tenant)
    
    form = CancelSubscriptionForm(request.POST)
    if form.is_valid():
        cancel_immediately = form.cleaned_data['cancel_immediately']
        
        try:
            if subscription.stripe_subscription_id:
                StripeService.cancel_subscription(
                    subscription.stripe_subscription_id,
                    at_period_end=not cancel_immediately
                )
            
            if cancel_immediately:
                subscription.status = 'cancelled'
                subscription.cancelled_at = timezone.now()
            else:
                subscription.cancel_at_period_end = True
            
            subscription.cancellation_reason = dict(form.fields['reason'].choices)[form.cleaned_data['reason']]
            if form.cleaned_data['feedback']:
                subscription.cancellation_reason += f" - {form.cleaned_data['feedback']}"
            
            subscription.save()
            
            messages.success(request, 'Subscription cancelled successfully.')
            
        except Exception as e:
            messages.error(request, f'Error cancelling subscription: {str(e)}')
    
    return redirect('subscription:manage')


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Stripe webhook handler
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle event
    try:
        from .stripe_utils import handle_stripe_webhook
        handle_stripe_webhook(event['type'], event['data']['object'])
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return HttpResponse(status=500)
    
    return HttpResponse(status=200)
