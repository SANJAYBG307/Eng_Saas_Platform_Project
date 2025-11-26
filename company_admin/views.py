"""
Views for company_admin app
Super admin interface for system management
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta

from core.models import Tenant, UserAccount, AuditLog
from core.decorators import role_required
from tenant_subscription.models import (
    TenantSubscription as Subscription,
    Payment,
    Invoice,
    SubscriptionPlan
)
from .models import (
    SupportTicket, TicketComment, SystemSettings,
    SystemMetrics, AnnouncementGlobal
)


@login_required
@role_required(['super_admin'])
def dashboard(request):
    """
    Super admin dashboard with system overview
    """
    # Get key metrics
    total_tenants = Tenant.objects.filter(is_deleted=False).count()
    active_tenants = Tenant.objects.filter(
        is_active=True,
        is_deleted=False
    ).count()
    
    total_users = UserAccount.objects.filter(is_deleted=False).count()
    active_users = UserAccount.objects.filter(
        is_active=True,
        is_deleted=False
    ).count()
    
    # Subscription stats
    active_subscriptions = Subscription.objects.filter(
        status='active'
    ).count()
    trial_subscriptions = Subscription.objects.filter(
        status='trial'
    ).count()
    
    # Revenue (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_revenue = Payment.objects.filter(
        status='succeeded',
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Open support tickets
    open_tickets = SupportTicket.objects.filter(
        status__in=['open', 'in_progress']
    ).count()
    
    # Recent activity
    recent_tenants = Tenant.objects.filter(
        is_deleted=False
    ).order_by('-created_at')[:5]
    
    recent_tickets = SupportTicket.objects.all().order_by('-created_at')[:5]
    
    # Chart data - last 7 days
    chart_data = []
    for i in range(6, -1, -1):
        date = timezone.now().date() - timedelta(days=i)
        metrics = SystemMetrics.objects.filter(metric_date=date).first()
        chart_data.append({
            'date': date.strftime('%m/%d'),
            'tenants': metrics.active_tenants if metrics else 0,
            'users': metrics.active_users if metrics else 0,
            'revenue': float(metrics.daily_revenue) if metrics else 0
        })
    
    context = {
        'total_tenants': total_tenants,
        'active_tenants': active_tenants,
        'total_users': total_users,
        'active_users': active_users,
        'active_subscriptions': active_subscriptions,
        'trial_subscriptions': trial_subscriptions,
        'recent_revenue': recent_revenue,
        'open_tickets': open_tickets,
        'recent_tenants': recent_tenants,
        'recent_tickets': recent_tickets,
        'chart_data': chart_data,
    }
    
    return render(request, 'company_admin/dashboard.html', context)


@login_required
@role_required(['super_admin'])
def tenant_list(request):
    """
    List all tenants with filtering
    """
    tenants = Tenant.objects.filter(is_deleted=False)
    
    # Filters
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    if status_filter == 'active':
        tenants = tenants.filter(is_active=True)
    elif status_filter == 'inactive':
        tenants = tenants.filter(is_active=False)
    
    if search:
        tenants = tenants.filter(
            Q(name__icontains=search) |
            Q(subdomain__icontains=search) |
            Q(contact_email__icontains=search)
        )
    
    tenants = tenants.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(tenants, 20)
    page = request.GET.get('page', 1)
    tenants_page = paginator.get_page(page)
    
    context = {
        'tenants': tenants_page,
        'status_filter': status_filter,
        'search': search,
    }
    
    return render(request, 'company_admin/tenant_list.html', context)


@login_required
@role_required(['super_admin'])
def tenant_detail(request, tenant_id):
    """
    Detailed view of a specific tenant
    """
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # Users
    users = UserAccount.objects.filter(
        tenant=tenant,
        is_deleted=False
    ).order_by('-created_at')[:10]
    
    # Subscription
    subscription = Subscription.objects.filter(tenant=tenant).first()
    
    # Recent payments
    payments = Payment.objects.filter(
        subscription__tenant=tenant
    ).order_by('-created_at')[:5]
    
    # Support tickets
    tickets = SupportTicket.objects.filter(
        tenant=tenant
    ).order_by('-created_at')[:5]
    
    # Recent audit logs
    audit_logs = AuditLog.objects.filter(
        tenant=tenant
    ).order_by('-created_at')[:10]
    
    context = {
        'tenant': tenant,
        'users': users,
        'subscription': subscription,
        'payments': payments,
        'tickets': tickets,
        'audit_logs': audit_logs,
    }
    
    return render(request, 'company_admin/tenant_detail.html', context)


@login_required
@role_required(['super_admin'])
def subscription_oversight(request):
    """
    Monitor all subscriptions
    """
    subscriptions = Subscription.objects.select_related(
        'tenant', 'plan'
    ).all()
    
    # Filters
    status_filter = request.GET.get('status', '')
    plan_filter = request.GET.get('plan', '')
    
    if status_filter:
        subscriptions = subscriptions.filter(status=status_filter)
    
    if plan_filter:
        subscriptions = subscriptions.filter(plan__name=plan_filter)
    
    # Get expiring trials (next 7 days)
    seven_days = timezone.now() + timedelta(days=7)
    expiring_trials = Subscription.objects.filter(
        status='trialing',
        trial_end__lte=seven_days,
        trial_end__gte=timezone.now()
    ).count()
    
    # Past due
    past_due = Subscription.objects.filter(status='past_due').count()
    
    # Pagination
    paginator = Paginator(subscriptions, 20)
    page = request.GET.get('page', 1)
    subscriptions_page = paginator.get_page(page)
    
    # Plans for filter
    plans = SubscriptionPlan.objects.filter(is_active=True)
    
    context = {
        'subscriptions': subscriptions_page,
        'status_filter': status_filter,
        'plan_filter': plan_filter,
        'plans': plans,
        'expiring_trials': expiring_trials,
        'past_due': past_due,
    }
    
    return render(request, 'company_admin/subscription_oversight.html', context)


@login_required
@role_required(['super_admin'])
def user_management(request):
    """
    Global user management
    """
    users = UserAccount.objects.filter(is_deleted=False).select_related(
        'tenant', 'role'
    )
    
    # Filters
    role_filter = request.GET.get('role', '')
    tenant_filter = request.GET.get('tenant', '')
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    if role_filter:
        users = users.filter(role__name=role_filter)
    
    if tenant_filter:
        users = users.filter(tenant_id=tenant_filter)
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    users = users.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    users_page = paginator.get_page(page)
    
    # For filters
    tenants = Tenant.objects.filter(is_deleted=False, is_active=True)
    
    context = {
        'users': users_page,
        'role_filter': role_filter,
        'tenant_filter': tenant_filter,
        'status_filter': status_filter,
        'search': search,
        'tenants': tenants,
    }
    
    return render(request, 'company_admin/user_management.html', context)


@login_required
@role_required(['super_admin'])
def analytics_reporting(request):
    """
    Analytics and reporting dashboard
    """
    # Last 30 days metrics
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    metrics = SystemMetrics.objects.filter(
        metric_date__gte=thirty_days_ago
    ).order_by('metric_date')
    
    # Revenue by plan
    revenue_by_plan = Payment.objects.filter(
        status='succeeded',
        created_at__gte=timezone.now() - timedelta(days=30)
    ).values(
        'subscription__plan__name'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Tenant growth
    tenant_growth = []
    for metric in metrics:
        tenant_growth.append({
            'date': metric.metric_date.strftime('%m/%d'),
            'total': metric.total_tenants,
            'active': metric.active_tenants
        })
    
    # Revenue trend
    revenue_trend = []
    for metric in metrics:
        revenue_trend.append({
            'date': metric.metric_date.strftime('%m/%d'),
            'revenue': float(metric.daily_revenue)
        })
    
    # Plan distribution
    plan_distribution = Subscription.objects.filter(
        status='active'
    ).values(
        'plan__name'
    ).annotate(
        count=Count('id')
    )
    
    context = {
        'tenant_growth': tenant_growth,
        'revenue_trend': revenue_trend,
        'revenue_by_plan': revenue_by_plan,
        'plan_distribution': plan_distribution,
    }
    
    return render(request, 'company_admin/analytics.html', context)


@login_required
@role_required(['super_admin'])
def system_settings(request):
    """
    Manage system settings
    """
    if request.method == 'POST':
        key = request.POST.get('key')
        value = request.POST.get('value')
        description = request.POST.get('description', '')
        data_type = request.POST.get('data_type', 'string')
        is_public = request.POST.get('is_public') == 'on'
        
        SystemSettings.objects.update_or_create(
            key=key,
            defaults={
                'value': value,
                'description': description,
                'data_type': data_type,
                'is_public': is_public
            }
        )
        
        messages.success(request, f'Setting "{key}" updated successfully.')
        return redirect('company_admin:system_settings')
    
    settings = SystemSettings.objects.all().order_by('key')
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'company_admin/system_settings.html', context)


@login_required
@role_required(['super_admin'])
def support_tickets(request):
    """
    List and manage support tickets
    """
    tickets = SupportTicket.objects.select_related(
        'tenant', 'created_by', 'assigned_to'
    ).all()
    
    # Filters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    
    if category_filter:
        tickets = tickets.filter(category=category_filter)
    
    if search:
        tickets = tickets.filter(
            Q(ticket_number__icontains=search) |
            Q(subject__icontains=search) |
            Q(tenant__name__icontains=search)
        )
    
    tickets = tickets.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(tickets, 20)
    page = request.GET.get('page', 1)
    tickets_page = paginator.get_page(page)
    
    context = {
        'tickets': tickets_page,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'search': search,
    }
    
    return render(request, 'company_admin/support_tickets.html', context)


@login_required
@role_required(['super_admin'])
def ticket_detail(request, ticket_id):
    """
    View and manage a specific ticket
    """
    ticket = get_object_or_404(
        SupportTicket.objects.select_related(
            'tenant', 'created_by', 'assigned_to'
        ),
        id=ticket_id
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'comment':
            comment_text = request.POST.get('comment')
            is_internal = request.POST.get('is_internal') == 'on'
            
            TicketComment.objects.create(
                ticket=ticket,
                author=request.user,
                comment=comment_text,
                is_internal=is_internal
            )
            
            messages.success(request, 'Comment added successfully.')
        
        elif action == 'update_status':
            new_status = request.POST.get('status')
            ticket.status = new_status
            
            if new_status == 'resolved':
                ticket.resolved_at = timezone.now()
            elif new_status == 'closed':
                ticket.closed_at = timezone.now()
            
            ticket.save()
            messages.success(request, f'Ticket status updated to {new_status}.')
        
        elif action == 'assign':
            assigned_to_id = request.POST.get('assigned_to')
            if assigned_to_id:
                ticket.assigned_to_id = assigned_to_id
                ticket.save()
                messages.success(request, 'Ticket assigned successfully.')
        
        return redirect('company_admin:ticket_detail', ticket_id=ticket.id)
    
    comments = ticket.comments.all().order_by('created_at')
    
    # Get super admins for assignment
    super_admins = UserAccount.objects.filter(
        role__name='super_admin',
        is_active=True,
        is_deleted=False
    )
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'super_admins': super_admins,
    }
    
    return render(request, 'company_admin/ticket_detail.html', context)


@login_required
@role_required(['super_admin'])
def billing_management(request):
    """
    Manage payments and invoices
    """
    # Recent payments
    payments = Payment.objects.select_related(
        'subscription__tenant'
    ).order_by('-created_at')
    
    # Filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(payments, 20)
    page = request.GET.get('page', 1)
    payments_page = paginator.get_page(page)
    
    # Summary stats
    total_revenue = Payment.objects.filter(
        status='succeeded'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_revenue = Payment.objects.filter(
        status='succeeded',
        created_at__gte=timezone.now() - timedelta(days=30)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'payments': payments_page,
        'status_filter': status_filter,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
    }
    
    return render(request, 'company_admin/billing_management.html', context)


@login_required
@role_required(['super_admin'])
def audit_trail(request):
    """
    View system-wide audit logs
    """
    logs = AuditLog.objects.select_related(
        'user', 'tenant'
    ).all()
    
    # Filters
    action_filter = request.GET.get('action', '')
    tenant_filter = request.GET.get('tenant', '')
    user_filter = request.GET.get('user', '')
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if tenant_filter:
        logs = logs.filter(tenant_id=tenant_filter)
    
    if user_filter:
        logs = logs.filter(user_id=user_filter)
    
    logs = logs.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    logs_page = paginator.get_page(page)
    
    # For filters
    tenants = Tenant.objects.filter(is_deleted=False, is_active=True)
    
    context = {
        'logs': logs_page,
        'action_filter': action_filter,
        'tenant_filter': tenant_filter,
        'user_filter': user_filter,
        'tenants': tenants,
    }
    
    return render(request, 'company_admin/audit_trail.html', context)


@login_required
@role_required(['super_admin'])
def system_health(request):
    """
    System health and monitoring
    """
    import psutil
    from django.db import connection
    
    # CPU and Memory
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Database
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()")
        table_count = cursor.fetchone()[0]
    
    # Recent metrics
    latest_metrics = SystemMetrics.objects.order_by('-metric_date').first()
    
    context = {
        'cpu_percent': cpu_percent,
        'memory_total': round(memory.total / (1024**3), 2),
        'memory_used': round(memory.used / (1024**3), 2),
        'memory_percent': memory.percent,
        'disk_total': round(disk.total / (1024**3), 2),
        'disk_used': round(disk.used / (1024**3), 2),
        'disk_percent': disk.percent,
        'table_count': table_count,
        'latest_metrics': latest_metrics,
    }
    
    return render(request, 'company_admin/system_health.html', context)
