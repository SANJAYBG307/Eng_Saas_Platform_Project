"""
Department Management URLs
HOD Interface Routes
"""
from django.urls import path
from . import views

app_name = 'department_management'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Faculty Management
    path('faculty/', views.faculty_list, name='faculty_list'),
    
    # Student Management
    path('students/', views.students_list, name='students_list'),
    
    # Attendance
    path('attendance/', views.attendance_overview, name='attendance_overview'),
    
    # Exams
    path('exams/', views.exam_results, name='exam_results'),
    
    # Timetable
    path('timetable/', views.timetable, name='timetable'),
    
    # Subjects
    path('subjects/', views.subject_management, name='subject_management'),
    
    # Announcements
    path('announcements/', views.announcements, name='announcements'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # Settings
    path('settings/', views.settings, name='settings'),
]
