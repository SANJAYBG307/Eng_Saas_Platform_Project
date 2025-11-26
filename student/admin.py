"""
Student App Admin - Multi-Tenant SaaS Platform
Admin interface for student models
"""

from django.contrib import admin
from .models import StudentNote, StudentResource, LibraryTransaction, FeePayment


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'subject', 'note_date', 'is_important', 'created_at']
    list_filter = ['is_important', 'note_date', 'subject']
    search_fields = ['title', 'content', 'student__first_name', 'student__last_name', 'tags']
    date_hierarchy = 'note_date'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('student', 'subject', 'title', 'note_date')
        }),
        ('Content', {
            'fields': ('content', 'tags', 'is_important')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StudentResource)
class StudentResourceAdmin(admin.ModelAdmin):
    list_display = ['resource_title', 'student', 'resource_type', 'subject', 'accessed_date', 'download_count', 'is_bookmarked']
    list_filter = ['resource_type', 'is_bookmarked', 'accessed_date', 'subject']
    search_fields = ['resource_title', 'student__first_name', 'student__last_name']
    date_hierarchy = 'accessed_date'
    readonly_fields = ['accessed_date', 'download_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('student', 'resource_title', 'resource_type', 'subject')
        }),
        ('Resource Details', {
            'fields': ('file', 'url', 'is_bookmarked')
        }),
        ('Statistics', {
            'fields': ('accessed_date', 'download_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LibraryTransaction)
class LibraryTransactionAdmin(admin.ModelAdmin):
    list_display = ['book_title', 'student', 'issue_date', 'due_date', 'return_date', 'status', 'fine_amount']
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = ['book_title', 'book_isbn', 'author', 'student__first_name', 'student__last_name']
    date_hierarchy = 'issue_date'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Student Information', {
            'fields': ('student',)
        }),
        ('Book Details', {
            'fields': ('book_title', 'book_isbn', 'author')
        }),
        ('Transaction Details', {
            'fields': ('issue_date', 'due_date', 'return_date', 'status')
        }),
        ('Financial', {
            'fields': ('fine_amount', 'remarks')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'student', 'fee_type', 'amount', 'payment_date', 'due_date', 'status', 'payment_method']
    list_filter = ['status', 'fee_type', 'payment_method', 'payment_date']
    search_fields = ['receipt_number', 'transaction_id', 'student__first_name', 'student__last_name']
    date_hierarchy = 'payment_date'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Student Information', {
            'fields': ('student', 'section')
        }),
        ('Fee Details', {
            'fields': ('fee_type', 'amount', 'payment_date', 'due_date', 'status')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'transaction_id', 'receipt_number')
        }),
        ('Additional', {
            'fields': ('remarks',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
