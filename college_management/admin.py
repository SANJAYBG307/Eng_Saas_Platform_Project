"""
Admin configurations for college_management app
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CollegeSettings,
    Holiday,
    Announcement,
    Timetable,
    ExamSchedule,
    ExamSlot
)


@admin.register(CollegeSettings)
class CollegeSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'tenant',
        'semester_system',
        'grading_system',
        'minimum_attendance_percentage',
        'sms_notifications_enabled',
        'email_notifications_enabled'
    ]
    list_filter = ['semester_system', 'grading_system']
    search_fields = ['tenant__name']
    
    fieldsets = [
        ('Tenant', {
            'fields': ['tenant']
        }),
        ('Academic Settings', {
            'fields': [
                'academic_year_start_month',
                'semester_system',
                'grading_system',
                'passing_marks'
            ]
        }),
        ('Attendance Settings', {
            'fields': [
                'attendance_grace_minutes',
                'minimum_attendance_percentage'
            ]
        }),
        ('Communication', {
            'fields': [
                'sms_notifications_enabled',
                'email_notifications_enabled',
                'parent_portal_enabled'
            ]
        }),
        ('Branding', {
            'fields': ['logo', 'primary_color', 'secondary_color'],
            'classes': ['collapse']
        }),
    ]


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'date', 'end_date', 'is_recurring']
    list_filter = ['is_recurring', 'date', 'tenant']
    search_fields = ['name', 'description', 'tenant__name']
    date_hierarchy = 'date'
    
    fieldsets = [
        ('Basic Info', {
            'fields': ['tenant', 'name', 'description']
        }),
        ('Dates', {
            'fields': ['date', 'end_date', 'is_recurring']
        }),
    ]


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'tenant',
        'announcement_type',
        'target_audience',
        'is_active_badge',
        'created_at'
    ]
    list_filter = ['announcement_type', 'target_audience', 'is_active', 'created_at']
    search_fields = ['title', 'content', 'tenant__name']
    raw_id_fields = ['created_by', 'target_department', 'target_section']
    
    fieldsets = [
        ('Basic Info', {
            'fields': ['tenant', 'created_by', 'title', 'content', 'announcement_type']
        }),
        ('Targeting', {
            'fields': [
                'target_audience',
                'target_department',
                'target_section'
            ]
        }),
        ('Schedule', {
            'fields': ['is_active', 'start_date', 'end_date']
        }),
        ('Attachments', {
            'fields': ['attachments'],
            'classes': ['collapse']
        }),
    ]
    
    def is_active_badge(self, obj):
        color = 'green' if obj.is_active else 'red'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            'Active' if obj.is_active else 'Inactive'
        )
    is_active_badge.short_description = 'Status'


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = [
        'section',
        'day_of_week',
        'period_number',
        'subject',
        'teacher',
        'start_time',
        'end_time',
        'room_number'
    ]
    list_filter = ['day_of_week', 'academic_year', 'section__department']
    search_fields = [
        'section__name',
        'subject__name',
        'teacher__first_name',
        'teacher__last_name'
    ]
    raw_id_fields = ['section', 'academic_year', 'subject', 'teacher']
    
    fieldsets = [
        ('Schedule Info', {
            'fields': [
                'tenant',
                'section',
                'academic_year',
                'day_of_week',
                'period_number'
            ]
        }),
        ('Class Details', {
            'fields': [
                'subject',
                'teacher',
                'start_time',
                'end_time',
                'room_number'
            ]
        }),
    ]


class ExamSlotInline(admin.TabularInline):
    model = ExamSlot
    extra = 1
    raw_id_fields = ['subject', 'section']


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'exam_name',
        'exam_type',
        'tenant',
        'department',
        'start_date',
        'end_date',
        'is_published'
    ]
    list_filter = ['exam_type', 'is_published', 'start_date', 'academic_year']
    search_fields = ['exam_name', 'tenant__name', 'department__name']
    raw_id_fields = ['academic_year', 'department']
    inlines = [ExamSlotInline]
    
    fieldsets = [
        ('Basic Info', {
            'fields': [
                'tenant',
                'academic_year',
                'exam_name',
                'exam_type',
                'department'
            ]
        }),
        ('Schedule', {
            'fields': ['start_date', 'end_date']
        }),
        ('Details', {
            'fields': ['instructions', 'is_published']
        }),
    ]


@admin.register(ExamSlot)
class ExamSlotAdmin(admin.ModelAdmin):
    list_display = [
        'exam_schedule',
        'subject',
        'section',
        'exam_date',
        'start_time',
        'end_time',
        'max_marks'
    ]
    list_filter = ['exam_date', 'exam_schedule__exam_type']
    search_fields = ['subject__name', 'section__name', 'exam_schedule__exam_name']
    raw_id_fields = ['exam_schedule', 'subject', 'section']
