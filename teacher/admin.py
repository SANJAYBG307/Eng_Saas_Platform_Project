from django.contrib import admin
from .models import Attendance, Assignment, AssignmentSubmission, Grade, TeacherResource, TeacherNote


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'section', 'subject', 'date', 'status', 'teacher')
    list_filter = ('status', 'date', 'section', 'subject')
    search_fields = ('student__first_name', 'student__last_name', 'student__email')
    date_hierarchy = 'date'
    raw_id_fields = ('tenant', 'teacher', 'student', 'section', 'subject')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'subject', 'teacher', 'due_date', 'status', 'max_marks')
    list_filter = ('status', 'section', 'subject', 'academic_year')
    search_fields = ('title', 'description')
    date_hierarchy = 'due_date'
    raw_id_fields = ('tenant', 'teacher', 'section', 'subject', 'academic_year')


class AssignmentSubmissionInline(admin.TabularInline):
    model = AssignmentSubmission
    extra = 0
    raw_id_fields = ('student', 'graded_by')


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submission_date', 'status', 'marks_obtained', 'is_late')
    list_filter = ('status', 'is_late', 'submission_date')
    search_fields = ('assignment__title', 'student__first_name', 'student__last_name')
    date_hierarchy = 'submission_date'
    raw_id_fields = ('assignment', 'student', 'graded_by')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'exam_name', 'marks_obtained', 'max_marks', 'percentage', 'grade', 'is_published')
    list_filter = ('is_published', 'exam_date', 'subject', 'academic_year')
    search_fields = ('student__first_name', 'student__last_name', 'exam_name')
    date_hierarchy = 'exam_date'
    raw_id_fields = ('tenant', 'student', 'subject', 'teacher', 'academic_year')


@admin.register(TeacherResource)
class TeacherResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'section', 'teacher', 'resource_type', 'is_public', 'created_at')
    list_filter = ('resource_type', 'is_public', 'subject', 'section')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    raw_id_fields = ('tenant', 'teacher', 'subject', 'section')


@admin.register(TeacherNote)
class TeacherNoteAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'subject', 'note_date', 'is_important')
    list_filter = ('is_important', 'note_date', 'subject')
    search_fields = ('student__first_name', 'student__last_name', 'note')
    date_hierarchy = 'note_date'
    raw_id_fields = ('tenant', 'teacher', 'student', 'subject')
