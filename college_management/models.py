"""
Models for college_management app
Tenant admin specific models and configurations
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import BaseModel, Tenant, UserAccount, Department, Section, AcademicYear


class CollegeSettings(BaseModel):
    """
    College-specific settings and configurations
    Each tenant has their own settings
    """
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='college_settings'
    )
    
    # Academic Settings
    academic_year_start_month = models.IntegerField(
        default=6,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="Month when academic year starts (1-12)"
    )
    semester_system = models.BooleanField(
        default=True,
        help_text="True for semester system, False for annual system"
    )
    
    # Attendance Settings
    attendance_grace_minutes = models.IntegerField(
        default=10,
        help_text="Grace period for late arrival (in minutes)"
    )
    minimum_attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=75.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Grading Settings
    grading_system = models.CharField(
        max_length=20,
        choices=[
            ('percentage', 'Percentage'),
            ('gpa', 'GPA (4.0 scale)'),
            ('cgpa', 'CGPA (10.0 scale)'),
            ('letter', 'Letter Grade'),
        ],
        default='percentage'
    )
    passing_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00
    )
    
    # Communication Settings
    sms_notifications_enabled = models.BooleanField(default=False)
    email_notifications_enabled = models.BooleanField(default=True)
    parent_portal_enabled = models.BooleanField(default=True)
    
    # Branding
    logo = models.ImageField(upload_to='college_logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#667eea', help_text="Hex color code")
    secondary_color = models.CharField(max_length=7, default='#764ba2', help_text="Hex color code")
    
    class Meta:
        db_table = 'college_settings'
    
    def __str__(self):
        return f"Settings for {self.tenant.name}"


class Holiday(BaseModel):
    """
    College holidays and non-working days
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='holidays'
    )
    
    name = models.CharField(max_length=200)
    date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="For multi-day holidays")
    description = models.TextField(blank=True)
    
    is_recurring = models.BooleanField(
        default=False,
        help_text="Does this holiday repeat every year?"
    )
    
    class Meta:
        db_table = 'holidays'
        ordering = ['date']
        indexes = [
            models.Index(fields=['tenant', 'date']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.date}"


class Announcement(BaseModel):
    """
    College announcements for students/teachers
    """
    ANNOUNCEMENT_TYPES = [
        ('general', 'General'),
        ('academic', 'Academic'),
        ('event', 'Event'),
        ('exam', 'Examination'),
        ('holiday', 'Holiday'),
        ('urgent', 'Urgent'),
    ]
    
    TARGET_AUDIENCE = [
        ('all', 'All Users'),
        ('students', 'Students Only'),
        ('teachers', 'Teachers Only'),
        ('parents', 'Parents Only'),
        ('department', 'Specific Department'),
        ('section', 'Specific Section'),
    ]
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='announcements'
    )
    created_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_announcements'
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES)
    
    target_audience = models.CharField(max_length=20, choices=TARGET_AUDIENCE, default='all')
    target_department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='announcements'
    )
    target_section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='announcements'
    )
    
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    
    attachments = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['target_audience']),
        ]
    
    def __str__(self):
        return self.title


class Timetable(BaseModel):
    """
    Class timetable/schedule
    """
    WEEKDAYS = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='timetables'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='timetables'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='timetables'
    )
    
    day_of_week = models.CharField(max_length=10, choices=WEEKDAYS)
    period_number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    subject = models.ForeignKey(
        'core.Subject',
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    teacher = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        null=True,
        related_name='teaching_schedule',
        limit_choices_to={'role__name': 'teacher'}
    )
    
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'timetables'
        ordering = ['day_of_week', 'period_number']
        unique_together = [['section', 'day_of_week', 'period_number', 'academic_year']]
        indexes = [
            models.Index(fields=['tenant', 'section', 'day_of_week']),
            models.Index(fields=['teacher', 'day_of_week']),
        ]
    
    def __str__(self):
        return f"{self.section} - {self.day_of_week} - Period {self.period_number}"


class ExamSchedule(BaseModel):
    """
    Examination schedule
    """
    EXAM_TYPES = [
        ('mid_term', 'Mid Term'),
        ('final', 'Final Exam'),
        ('unit_test', 'Unit Test'),
        ('practical', 'Practical'),
        ('viva', 'Viva/Oral'),
    ]
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='exam_schedules'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='exam_schedules'
    )
    
    exam_name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='exam_schedules',
        null=True,
        blank=True
    )
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    instructions = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'exam_schedules'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['tenant', 'academic_year']),
            models.Index(fields=['department', 'start_date']),
        ]
    
    def __str__(self):
        return f"{self.exam_name} - {self.start_date}"


class ExamSlot(BaseModel):
    """
    Individual exam slots within a schedule
    """
    exam_schedule = models.ForeignKey(
        ExamSchedule,
        on_delete=models.CASCADE,
        related_name='exam_slots'
    )
    
    subject = models.ForeignKey(
        'core.Subject',
        on_delete=models.CASCADE,
        related_name='exam_slots'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='exam_slots'
    )
    
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    room_number = models.CharField(max_length=50, blank=True)
    
    instructions = models.TextField(blank=True)
    
    class Meta:
        db_table = 'exam_slots'
        ordering = ['exam_date', 'start_time']
        indexes = [
            models.Index(fields=['exam_schedule', 'exam_date']),
            models.Index(fields=['section', 'exam_date']),
        ]
    
    def __str__(self):
        return f"{self.subject.name} - {self.section} - {self.exam_date}"
