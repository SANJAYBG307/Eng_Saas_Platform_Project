"""
Teacher App URLs
Teacher portal routes
"""
from django.urls import path
from . import views

app_name = 'teacher'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Classes
    path('classes/', views.my_classes, name='my_classes'),
    
    # Attendance
    path('attendance/', views.attendance_marking, name='attendance_marking'),
    
    # Grades
    path('grades/', views.grade_management, name='grade_management'),
    
    # Assignments
    path('assignments/', views.assignments, name='assignments'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/<uuid:assignment_id>/submissions/', views.assignment_submissions, name='assignment_submissions'),
    
    # Student Performance
    path('performance/', views.student_performance, name='student_performance'),
    
    # Timetable
    path('timetable/', views.my_timetable, name='timetable'),
    
    # Exams
    path('exams/', views.exam_schedules, name='exam_schedules'),
    
    # Resources
    path('resources/', views.resources, name='resources'),
    
    # Communication
    path('communication/', views.communication, name='communication'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
]
