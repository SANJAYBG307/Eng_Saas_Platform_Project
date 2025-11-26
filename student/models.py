"""
Student App Models - Multi-Tenant SaaS Platform
Student-specific models for managing student notes, resources, library, and fees
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel, Tenant, UserAccount, Section, Subject


class StudentNote(BaseModel):
    """Personal notes created by students"""
    student = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='student_notes',
        limit_choices_to={'role__name': 'student'}
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_notes'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    note_date = models.DateField()
    is_important = models.BooleanField(default=False)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    
    class Meta:
        db_table = 'student_notes'
        ordering = ['-note_date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'note_date']),
            models.Index(fields=['subject', 'note_date']),
            models.Index(fields=['is_important']),
        ]
        verbose_name = 'Student Note'
        verbose_name_plural = 'Student Notes'
    
    def __str__(self):
        return f"{self.title} - {self.student.get_full_name()}"


class StudentResource(BaseModel):
    """Resources accessed/downloaded by students"""
    student = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='student_resources_accessed',
        limit_choices_to={'role__name': 'student'}
    )
    resource_title = models.CharField(max_length=200)
    resource_type = models.CharField(
        max_length=50,
        choices=[
            ('notes', 'Notes'),
            ('presentation', 'Presentation'),
            ('video', 'Video'),
            ('reference', 'Reference Material'),
            ('worksheet', 'Worksheet'),
            ('assignment', 'Assignment'),
            ('other', 'Other'),
        ],
        default='notes'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_resources'
    )
    file = models.FileField(upload_to='student_resources/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    accessed_date = models.DateTimeField(auto_now_add=True)
    download_count = models.PositiveIntegerField(default=0)
    is_bookmarked = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'student_resources'
        ordering = ['-accessed_date']
        indexes = [
            models.Index(fields=['student', 'accessed_date']),
            models.Index(fields=['resource_type']),
            models.Index(fields=['is_bookmarked']),
        ]
        verbose_name = 'Student Resource'
        verbose_name_plural = 'Student Resources'
    
    def __str__(self):
        return f"{self.resource_title} - {self.student.get_full_name()}"


class LibraryTransaction(BaseModel):
    """Library book issue and return transactions"""
    student = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='library_transactions',
        limit_choices_to={'role__name': 'student'}
    )
    book_title = models.CharField(max_length=300)
    book_isbn = models.CharField(max_length=20, blank=True)
    author = models.CharField(max_length=200, blank=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('issued', 'Issued'),
            ('returned', 'Returned'),
            ('overdue', 'Overdue'),
            ('lost', 'Lost'),
        ],
        default='issued'
    )
    fine_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    remarks = models.TextField(blank=True)
    
    class Meta:
        db_table = 'library_transactions'
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['issue_date', 'due_date']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'Library Transaction'
        verbose_name_plural = 'Library Transactions'
    
    def __str__(self):
        return f"{self.book_title} - {self.student.get_full_name()} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Auto-update status based on dates"""
        if self.return_date:
            self.status = 'returned'
        elif self.status != 'lost':
            from django.utils import timezone
            if self.due_date < timezone.now().date() and not self.return_date:
                self.status = 'overdue'
        super().save(*args, **kwargs)


class FeePayment(BaseModel):
    """Student fee payment records"""
    student = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='fee_payments',
        limit_choices_to={'role__name': 'student'}
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='fee_payments'
    )
    fee_type = models.CharField(
        max_length=50,
        choices=[
            ('tuition', 'Tuition Fee'),
            ('exam', 'Exam Fee'),
            ('library', 'Library Fee'),
            ('laboratory', 'Laboratory Fee'),
            ('sports', 'Sports Fee'),
            ('transport', 'Transport Fee'),
            ('hostel', 'Hostel Fee'),
            ('miscellaneous', 'Miscellaneous'),
        ],
        default='tuition'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    payment_date = models.DateField()
    due_date = models.DateField()
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('cash', 'Cash'),
            ('cheque', 'Cheque'),
            ('online', 'Online'),
            ('card', 'Card'),
            ('upi', 'UPI'),
        ],
        default='online'
    )
    transaction_id = models.CharField(max_length=100, blank=True)
    receipt_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('overdue', 'Overdue'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    remarks = models.TextField(blank=True)
    
    class Meta:
        db_table = 'fee_payments'
        ordering = ['-payment_date', '-due_date']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['fee_type', 'payment_date']),
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['receipt_number']),
        ]
        verbose_name = 'Fee Payment'
        verbose_name_plural = 'Fee Payments'
    
    def __str__(self):
        return f"{self.get_fee_type_display()} - {self.student.get_full_name()} - {self.amount}"
