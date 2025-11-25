"""
Models for company_admin app
Super admin specific models for system management
"""
from django.db import models
from django.utils import timezone
from core.models import BaseModel, Tenant, UserAccount


class SupportTicket(BaseModel):
    """
    Support tickets from tenants
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_customer', 'Waiting on Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    CATEGORY_CHOICES = [
        ('technical', 'Technical Issue'),
        ('billing', 'Billing'),
        ('feature_request', 'Feature Request'),
        ('bug_report', 'Bug Report'),
        ('general', 'General Inquiry'),
    ]
    
    ticket_number = models.CharField(max_length=20, unique=True, db_index=True)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='support_tickets'
    )
    created_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tickets'
    )
    assigned_to = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        limit_choices_to={'role__name': 'super_admin'}
    )
    
    subject = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    attachments = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_number']),
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to']),
        ]
    
    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"
    
    def is_open(self):
        return self.status in ['open', 'in_progress', 'waiting_customer']


class TicketComment(BaseModel):
    """
    Comments on support tickets
    """
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        null=True
    )
    comment = models.TextField()
    is_internal = models.BooleanField(default=False, help_text="Internal notes not visible to customer")
    
    class Meta:
        db_table = 'ticket_comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.ticket.ticket_number} by {self.author}"


class SystemSettings(BaseModel):
    """
    Global system settings
    """
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('string', 'String'),
            ('integer', 'Integer'),
            ('boolean', 'Boolean'),
            ('json', 'JSON'),
        ],
        default='string'
    )
    is_public = models.BooleanField(default=False, help_text="Can tenants see this setting?")
    
    class Meta:
        db_table = 'system_settings'
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"
    
    def get_value(self):
        """Parse value based on data type"""
        if self.data_type == 'integer':
            return int(self.value)
        elif self.data_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes']
        elif self.data_type == 'json':
            import json
            return json.loads(self.value)
        return self.value


class SystemMetrics(BaseModel):
    """
    System-wide metrics and statistics
    """
    metric_date = models.DateField(default=timezone.now)
    
    total_tenants = models.IntegerField(default=0)
    active_tenants = models.IntegerField(default=0)
    trial_tenants = models.IntegerField(default=0)
    paid_tenants = models.IntegerField(default=0)
    
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    
    daily_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    storage_used_gb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    api_calls = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'system_metrics'
        ordering = ['-metric_date']
        unique_together = [['metric_date']]
    
    def __str__(self):
        return f"Metrics for {self.metric_date}"


class AnnouncementGlobal(BaseModel):
    """
    System-wide announcements for all tenants
    """
    title = models.CharField(max_length=200)
    message = models.TextField()
    announcement_type = models.CharField(
        max_length=20,
        choices=[
            ('info', 'Information'),
            ('warning', 'Warning'),
            ('maintenance', 'Maintenance'),
            ('update', 'Update'),
        ],
        default='info'
    )
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    show_on_login = models.BooleanField(default=False)
    
    target_all_tenants = models.BooleanField(default=True)
    target_tenants = models.ManyToManyField(
        Tenant,
        blank=True,
        related_name='global_announcements'
    )
    
    class Meta:
        db_table = 'announcements_global'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def is_visible(self):
        """Check if announcement should be visible now"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True
