"""
Extended Models for Academic Features
Attendance, Assignments, Assessments, Grades, Messages, Notifications
"""

from django.db import models
from django.utils import timezone
from core.models import BaseModel, Tenant, UserAccount, Subject, Section, AcademicYear


class Attendance(BaseModel):
    """Daily attendance record"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendances')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='attendances')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='attendances')
    
    date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=[
            ('present', 'Present'),
            ('absent', 'Absent'),
            ('late', 'Late'),
            ('excused', 'Excused'),
        ],
        default='present'
    )
    
    marked_by = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, related_name='attendances_marked')
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'attendances'
        unique_together = ['tenant', 'student', 'subject', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['tenant', 'student', 'date']),
            models.Index(fields=['tenant', 'section', 'date']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} - {self.status}"


class Assignment(BaseModel):
    """Assignment/Homework"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='assignments_created')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='assignments')
    
    due_date = models.DateTimeField()
    total_marks = models.IntegerField(default=100)
    
    attachment = models.FileField(upload_to='assignments/', null=True, blank=True)
    
    allow_late_submission = models.BooleanField(default=False)
    late_submission_penalty = models.IntegerField(default=0, help_text="Percentage penalty for late submission")
    
    class Meta:
        db_table = 'assignments'
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['tenant', 'section']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.section.name}"


class AssignmentSubmission(BaseModel):
    """Student assignment submission"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='assignment_submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='assignment_submissions')
    
    submission_date = models.DateTimeField(default=timezone.now)
    content = models.TextField(null=True, blank=True)
    attachment = models.FileField(upload_to='submissions/', null=True, blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('submitted', 'Submitted'),
            ('graded', 'Graded'),
            ('returned', 'Returned'),
            ('resubmit', 'Resubmit Required'),
        ],
        default='submitted'
    )
    
    marks_obtained = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    graded_by = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, related_name='submissions_graded')
    graded_date = models.DateTimeField(null=True, blank=True)
    
    is_late = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'assignment_submissions'
        unique_together = ['assignment', 'student']
        ordering = ['-submission_date']
        indexes = [
            models.Index(fields=['tenant', 'student']),
            models.Index(fields=['assignment', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.assignment.title}"


class Assessment(BaseModel):
    """Exam/Test/Quiz"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
    assessment_type = models.CharField(
        max_length=20,
        choices=[
            ('quiz', 'Quiz'),
            ('test', 'Test'),
            ('midterm', 'Midterm'),
            ('final', 'Final Exam'),
            ('practical', 'Practical'),
        ]
    )
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assessments')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='assessments')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='assessments')
    
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    total_marks = models.IntegerField(default=100)
    passing_marks = models.IntegerField(default=40)
    
    created_by = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='assessments_created')
    
    class Meta:
        db_table = 'assessments'
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['tenant', 'section']),
            models.Index(fields=['scheduled_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.section.name}"


class Grade(BaseModel):
    """Student grades/marks"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='grades')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='grades')
    
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(null=True, blank=True)
    
    graded_by = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, related_name='grades_given')
    graded_date = models.DateTimeField(default=timezone.now)
    
    is_published = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'grades'
        unique_together = ['assessment', 'student']
        ordering = ['-graded_date']
        indexes = [
            models.Index(fields=['tenant', 'student']),
            models.Index(fields=['assessment']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.assessment.title} - {self.marks_obtained}"
    
    def get_percentage(self):
        return (self.marks_obtained / self.assessment.total_marks) * 100
    
    def get_grade_letter(self):
        percentage = self.get_percentage()
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B'
        elif percentage >= 60:
            return 'C'
        elif percentage >= 50:
            return 'D'
        else:
            return 'F'


class Message(BaseModel):
    """Internal messaging system"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='messages')
    
    sender = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='messages_sent')
    recipient = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='messages_received')
    
    subject = models.CharField(max_length=200)
    body = models.TextField()
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'recipient', 'is_read']),
            models.Index(fields=['sender']),
        ]
    
    def __str__(self):
        return f"{self.sender.get_full_name()} to {self.recipient.get_full_name()} - {self.subject}"


class Notification(BaseModel):
    """System notifications"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    notification_type = models.CharField(
        max_length=20,
        choices=[
            ('info', 'Information'),
            ('success', 'Success'),
            ('warning', 'Warning'),
            ('error', 'Error'),
            ('announcement', 'Announcement'),
        ],
        default='info'
    )
    
    link = models.CharField(max_length=500, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['tenant', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"


class Announcement(BaseModel):
    """Announcements/Notices"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='announcements')
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    posted_by = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='announcements_posted')
    
    target_audience = models.CharField(
        max_length=20,
        choices=[
            ('all', 'All Users'),
            ('students', 'Students Only'),
            ('teachers', 'Teachers Only'),
            ('parents', 'Parents Only'),
        ],
        default='all'
    )
    
    department = models.ForeignKey('core.Department', on_delete=models.CASCADE, null=True, blank=True, related_name='announcements')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True, related_name='announcements')
    
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
    
    attachment = models.FileField(upload_to='announcements/', null=True, blank=True)
    
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'target_audience']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.tenant.name}"
    
    def is_active(self):
        if self.expires_at:
            return timezone.now() < self.expires_at
        return True


class Timetable(BaseModel):
    """Class timetable/schedule"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='timetables')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='timetables')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='timetables')
    
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
        ]
    )
    
    period_number = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetables')
    teacher = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='timetables')
    
    room_number = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        db_table = 'timetables'
        unique_together = ['tenant', 'section', 'day_of_week', 'period_number']
        ordering = ['day_of_week', 'start_time']
        indexes = [
            models.Index(fields=['tenant', 'section']),
            models.Index(fields=['teacher']),
        ]
    
    def __str__(self):
        return f"{self.section.name} - {self.day_of_week} - {self.subject.name}"


class LearningResource(BaseModel):
    """Learning materials/resources"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='learning_resources')
    
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
    resource_type = models.CharField(
        max_length=20,
        choices=[
            ('pdf', 'PDF Document'),
            ('video', 'Video'),
            ('link', 'External Link'),
            ('slides', 'Presentation'),
            ('notes', 'Notes'),
        ]
    )
    
    file = models.FileField(upload_to='resources/', null=True, blank=True)
    external_link = models.URLField(null=True, blank=True)
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='resources')
    uploaded_by = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='resources_uploaded')
    
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='resources')
    
    download_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'learning_resources'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'subject']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"
