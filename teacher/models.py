"""
Teacher App Models
Teacher portal functionality for attendance, assignments, grades, etc.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import BaseModel, Tenant, UserAccount, Section, Subject, AcademicYear


class Attendance(BaseModel):
    """
    Daily attendance records marked by teachers
    """
    ATTENDANCE_STATUS = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='attendances')
    teacher = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='attendances_marked')
    student = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='attendances')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendances', null=True, blank=True)
    
    date = models.DateField()
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS)
    remarks = models.TextField(blank=True)
    
    class Meta:
        db_table = 'attendances'
        ordering = ['-date']
        unique_together = ['student', 'section', 'subject', 'date']
        indexes = [
            models.Index(fields=['date', 'section']),
            models.Index(fields=['student', 'date']),
            models.Index(fields=['teacher', 'date']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} - {self.status}"


class Assignment(BaseModel):
    """
    Assignments created by teachers
    """
    ASSIGNMENT_STATUS = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='assignments_created')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='assignments')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    attachment = models.FileField(upload_to='assignments/%Y/%m/', null=True, blank=True)
    
    due_date = models.DateTimeField()
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    
    status = models.CharField(max_length=10, choices=ASSIGNMENT_STATUS, default='draft')
    allow_late_submission = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'assignments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['section', 'subject']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.section.name}"


class AssignmentSubmission(BaseModel):
    """
    Student submissions for assignments
    """
    SUBMISSION_STATUS = [
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('returned', 'Returned'),
    ]
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='assignment_submissions')
    
    submission_date = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='submissions/%Y/%m/')
    comments = models.TextField(blank=True)
    
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions')
    graded_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=10, choices=SUBMISSION_STATUS, default='submitted')
    is_late = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'assignment_submissions'
        ordering = ['-submission_date']
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f"{self.assignment.title} - {self.student.get_full_name()}"


class Grade(BaseModel):
    """
    Grades/marks given by teachers for exams
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    teacher = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='grades_given')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='grades')
    
    exam_name = models.CharField(max_length=100)
    exam_date = models.DateField()
    
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    
    grade = models.CharField(max_length=5, blank=True)  # A+, A, B+, etc.
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)
    
    is_published = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'grades'
        ordering = ['-exam_date']
        indexes = [
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['subject', 'exam_date']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject.name} - {self.exam_name}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate percentage
        if self.marks_obtained and self.max_marks:
            self.percentage = (self.marks_obtained / self.max_marks) * 100
        super().save(*args, **kwargs)


class TeacherResource(BaseModel):
    """
    Teaching resources uploaded by teachers
    """
    RESOURCE_TYPES = [
        ('notes', 'Notes'),
        ('presentation', 'Presentation'),
        ('video', 'Video Link'),
        ('reference', 'Reference Material'),
        ('worksheet', 'Worksheet'),
        ('other', 'Other'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='teacher_resources')
    teacher = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='teacher_resources_uploaded')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teacher_resources')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='teacher_resources', null=True, blank=True)
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='teacher_resources/%Y/%m/', null=True, blank=True)
    url = models.URLField(blank=True, help_text='For video links or external resources')
    
    is_public = models.BooleanField(default=True, help_text='Visible to students')
    
    class Meta:
        db_table = 'teacher_resources'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subject', 'section']),
            models.Index(fields=['teacher', 'resource_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"


class TeacherNote(BaseModel):
    """
    Private notes by teachers about students
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='teacher_notes')
    teacher = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='notes_created')
    student = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='teacher_notes')
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teacher_notes', null=True, blank=True)
    note_date = models.DateField(default=timezone.now)
    note = models.TextField()
    
    is_important = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'teacher_notes'
        ordering = ['-note_date']
        indexes = [
            models.Index(fields=['student', 'teacher']),
            models.Index(fields=['note_date']),
        ]
    
    def __str__(self):
        return f"Note about {self.student.get_full_name()} by {self.teacher.get_full_name()}"
