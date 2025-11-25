"""
Admin configurations for company_admin app
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SupportTicket, TicketComment, SystemSettings,
    SystemMetrics, AnnouncementGlobal
)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_number', 'subject', 'tenant', 'category',
        'priority_badge', 'status_badge', 'assigned_to', 'created_at'
    ]
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['ticket_number', 'subject', 'description', 'tenant__name']
    readonly_fields = ['ticket_number', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'created_by', 'assigned_to']
    
    fieldsets = [
        ('Ticket Information', {
            'fields': ['ticket_number', 'subject', 'description', 'category']
        }),
        ('Related', {
            'fields': ['tenant', 'created_by', 'assigned_to']
        }),
        ('Status', {
            'fields': ['priority', 'status', 'resolved_at', 'closed_at']
        }),
        ('Attachments', {
            'fields': ['attachments'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def priority_badge(self, obj):
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.priority, '#6c757d'),
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def status_badge(self, obj):
        colors = {
            'open': '#007bff',
            'in_progress': '#ffc107',
            'waiting_customer': '#17a2b8',
            'resolved': '#28a745',
            'closed': '#6c757d'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'author', 'comment_preview', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['comment', 'ticket__ticket_number']
    raw_id_fields = ['ticket', 'author']
    
    def comment_preview(self, obj):
        return obj.comment[:100] + '...' if len(obj.comment) > 100 else obj.comment
    comment_preview.short_description = 'Comment'


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_preview', 'data_type', 'is_public', 'updated_at']
    list_filter = ['data_type', 'is_public']
    search_fields = ['key', 'value', 'description']
    
    fieldsets = [
        ('Setting', {
            'fields': ['key', 'value', 'data_type']
        }),
        ('Details', {
            'fields': ['description', 'is_public']
        }),
    ]
    
    def value_preview(self, obj):
        return obj.value[:100] + '...' if len(obj.value) > 100 else obj.value
    value_preview.short_description = 'Value'


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'metric_date', 'total_tenants', 'active_tenants',
        'total_users', 'daily_revenue', 'monthly_revenue'
    ]
    list_filter = ['metric_date']
    date_hierarchy = 'metric_date'
    
    fieldsets = [
        ('Date', {
            'fields': ['metric_date']
        }),
        ('Tenant Metrics', {
            'fields': [
                'total_tenants', 'active_tenants',
                'trial_tenants', 'paid_tenants'
            ]
        }),
        ('User Metrics', {
            'fields': ['total_users', 'active_users']
        }),
        ('Revenue', {
            'fields': ['daily_revenue', 'monthly_revenue']
        }),
        ('System', {
            'fields': ['storage_used_gb', 'api_calls']
        }),
    ]


@admin.register(AnnouncementGlobal)
class AnnouncementGlobalAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'announcement_type', 'is_active',
        'show_on_login', 'start_date', 'end_date'
    ]
    list_filter = ['announcement_type', 'is_active', 'show_on_login', 'start_date']
    search_fields = ['title', 'message']
    filter_horizontal = ['target_tenants']
    
    fieldsets = [
        ('Announcement', {
            'fields': ['title', 'message', 'announcement_type']
        }),
        ('Schedule', {
            'fields': ['start_date', 'end_date', 'is_active']
        }),
        ('Display Options', {
            'fields': ['show_on_login']
        }),
        ('Targeting', {
            'fields': ['target_all_tenants', 'target_tenants']
        }),
    ]
