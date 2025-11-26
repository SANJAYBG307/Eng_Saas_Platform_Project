"""
Parent App Models - Multi-Tenant SaaS Platform
Parent-specific models for communication (ParentStudentLink is in core.models)
"""

from django.db import models
from django.core.validators import MinValueValidator
from core.models import BaseModel, Tenant, UserAccount, Section, Subject


class ParentCommunication(BaseModel):
    """Communication between parents and teachers"""
    parent = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='parent_communications_sent',
        limit_choices_to={'role__name': 'parent'}
    )
    student = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='parent_communications_about',
        limit_choices_to={'role__name': 'student'}
    )
    teacher = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='parent_communications_received',
        limit_choices_to={'role__name': 'teacher'},
        null=True,
        blank=True
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    message_type = models.CharField(
        max_length=50,
        choices=[
            ('inquiry', 'Inquiry'),
            ('concern', 'Concern'),
            ('request', 'Request'),
            ('feedback', 'Feedback'),
            ('complaint', 'Complaint'),
            ('appreciation', 'Appreciation'),
        ],
        default='inquiry'
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        default='medium'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('sent', 'Sent'),
            ('read', 'Read'),
            ('replied', 'Replied'),
            ('resolved', 'Resolved'),
            ('closed', 'Closed'),
        ],
        default='sent'
    )
    reply = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    replied_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parent_communication_replies'
    )
    
    class Meta:
        db_table = 'parent_communications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['parent', 'status']),
            models.Index(fields=['teacher', 'status']),
            models.Index(fields=['student', 'created_at']),
            models.Index(fields=['priority', 'status']),
        ]
        verbose_name = 'Parent Communication'
        verbose_name_plural = 'Parent Communications'
    
    def __str__(self):
        return f"{self.subject} - {self.parent.get_full_name()} ({self.get_status_display()})"
