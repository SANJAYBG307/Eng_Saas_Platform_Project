"""
Department Management Models
HOD (Head of Department) specific functionality
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel, Tenant, Department, UserAccount, Subject, Section


class DepartmentAnnouncement(BaseModel):
    """
    Department-specific announcements by HOD
    """
    ANNOUNCEMENT_TYPES = [
        ('general', 'General'),
        ('academic', 'Academic'),
        ('meeting', 'Meeting'),
        ('event', 'Event'),
        ('urgent', 'Urgent'),
    ]
    
    TARGET_AUDIENCE = [
        ('all', 'All Department Members'),
        ('faculty', 'Faculty Only'),
        ('students', 'Students Only'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='dept_announcements')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='dept_announcements')
    created_by = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='dept_announcements_created')
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES, default='general')
    target_audience = models.CharField(max_length=20, choices=TARGET_AUDIENCE, default='all')
    
    is_pinned = models.BooleanField(default=False)
    priority = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='1=Low, 3=Normal, 5=High'
    )
    
    class Meta:
        db_table = 'department_announcements'
        ordering = ['-is_pinned', '-priority', '-created_at']
        indexes = [
            models.Index(fields=['department', 'created_at']),
            models.Index(fields=['is_pinned', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.department.name}"


class FacultyMeeting(BaseModel):
    """
    Department faculty meetings scheduled by HOD
    """
    MEETING_STATUS = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='faculty_meetings')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='faculty_meetings')
    organized_by = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='meetings_organized')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    meeting_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=200)
    
    attendees = models.ManyToManyField(UserAccount, related_name='faculty_meetings_attended', blank=True)
    agenda = models.TextField()
    minutes = models.TextField(blank=True, help_text='Meeting minutes/notes')
    
    status = models.CharField(max_length=20, choices=MEETING_STATUS, default='scheduled')
    
    class Meta:
        db_table = 'faculty_meetings'
        ordering = ['-meeting_date', '-start_time']
        indexes = [
            models.Index(fields=['department', 'meeting_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.meeting_date}"


class DepartmentResource(BaseModel):
    """
    Department resources (documents, materials) managed by HOD
    """
    RESOURCE_TYPES = [
        ('syllabus', 'Syllabus'),
        ('notes', 'Notes'),
        ('question_paper', 'Question Paper'),
        ('guideline', 'Guideline'),
        ('form', 'Form'),
        ('policy', 'Policy'),
        ('other', 'Other'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='dept_resources')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='resources')
    uploaded_by = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='resources_uploaded')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='department_resources/%Y/%m/')
    
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='resources')
    is_public = models.BooleanField(default=True, help_text='Visible to all department members')
    
    download_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'department_resources'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['department', 'resource_type']),
            models.Index(fields=['subject']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.department.name}"


class DepartmentSettings(BaseModel):
    """
    Department-specific settings configured by HOD
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='dept_settings')
    department = models.OneToOneField(Department, on_delete=models.CASCADE, related_name='settings')
    
    # Attendance policies
    minimum_attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=75.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    attendance_grace_period = models.IntegerField(
        default=15,
        help_text='Grace period in minutes'
    )
    
    # Grading policies
    passing_marks_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Class management
    max_lectures_per_day = models.IntegerField(default=8)
    class_duration_minutes = models.IntegerField(default=50)
    break_duration_minutes = models.IntegerField(default=10)
    
    # Notifications
    enable_absence_alerts = models.BooleanField(default=True)
    enable_low_performance_alerts = models.BooleanField(default=True)
    performance_alert_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00
    )
    
    class Meta:
        db_table = 'department_settings'
    
    def __str__(self):
        return f"Settings - {self.department.name}"
