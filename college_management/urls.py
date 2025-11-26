"""
URL Configuration for college_management app
Tenant admin interface
"""
from django.urls import path
from . import views

app_name = 'college_management'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Department Management
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:dept_id>/', views.department_detail, name='department_detail'),
    path('departments/<int:dept_id>/edit/', views.department_edit, name='department_edit'),
    
    # Section Management
    path('sections/', views.section_list, name='section_list'),
    path('sections/create/', views.section_create, name='section_create'),
    path('sections/<int:section_id>/', views.section_detail, name='section_detail'),
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    
    # Timetable
    path('timetable/', views.timetable_view, name='timetable'),
    path('timetable/create/', views.timetable_create, name='timetable_create'),
    
    # Exams
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/create/', views.exam_create, name='exam_create'),
    path('exams/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    
    # Announcements
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    path('announcements/<int:announcement_id>/edit/', views.announcement_edit, name='announcement_edit'),
    
    # Reports
    path('reports/', views.reports_dashboard, name='reports'),
    path('reports/attendance/', views.attendance_report, name='attendance_report'),
    path('reports/academic/', views.academic_report, name='academic_report'),
    
    # Settings
    path('settings/', views.college_settings, name='settings'),
    
    # Holidays
    path('holidays/', views.holiday_list, name='holiday_list'),
]
