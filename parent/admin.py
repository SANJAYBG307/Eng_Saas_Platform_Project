"""
Parent App Admin - Multi-Tenant SaaS Platform
Admin interface for parent models (ParentStudentLink is registered in core admin)
"""

from django.contrib import admin
from .models import ParentCommunication


@admin.register(ParentCommunication)
class ParentCommunicationAdmin(admin.ModelAdmin):
    list_display = ['subject', 'parent', 'student', 'teacher', 'message_type', 'priority', 'status', 'created_at']
    list_filter = ['message_type', 'priority', 'status', 'created_at']
    search_fields = ['subject', 'message', 'parent__first_name', 'parent__last_name', 'student__first_name', 'student__last_name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'replied_at', 'replied_by']
    fieldsets = (
        ('Communication Details', {
            'fields': ('parent', 'student', 'teacher', 'subject', 'message')
        }),
        ('Classification', {
            'fields': ('message_type', 'priority', 'status')
        }),
        ('Reply', {
            'fields': ('reply', 'replied_at', 'replied_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
