from django.contrib import admin
from .models import DepartmentAnnouncement, FacultyMeeting, DepartmentResource, DepartmentSettings


@admin.register(DepartmentAnnouncement)
class DepartmentAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'announcement_type', 'target_audience', 'is_pinned', 'priority', 'created_at')
    list_filter = ('announcement_type', 'target_audience', 'is_pinned', 'priority', 'department')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    raw_id_fields = ('tenant', 'department', 'created_by')


@admin.register(FacultyMeeting)
class FacultyMeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'meeting_date', 'start_time', 'end_time', 'status', 'venue')
    list_filter = ('status', 'meeting_date', 'department')
    search_fields = ('title', 'description', 'agenda')
    date_hierarchy = 'meeting_date'
    raw_id_fields = ('tenant', 'department', 'organized_by')
    filter_horizontal = ('attendees',)


@admin.register(DepartmentResource)
class DepartmentResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'resource_type', 'subject', 'is_public', 'download_count', 'created_at')
    list_filter = ('resource_type', 'is_public', 'department', 'subject')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    raw_id_fields = ('tenant', 'department', 'uploaded_by', 'subject')


@admin.register(DepartmentSettings)
class DepartmentSettingsAdmin(admin.ModelAdmin):
    list_display = ('department', 'minimum_attendance_percentage', 'passing_marks_percentage', 'max_lectures_per_day')
    list_filter = ('department',)
    raw_id_fields = ('tenant', 'department')
