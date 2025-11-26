"""
Student App URLs - Multi-Tenant SaaS Platform
URL patterns for student portal
"""

from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('grades/', views.grades, name='grades'),
    path('assignments/', views.assignments, name='assignments'),
    path('assignments/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('exam-schedule/', views.exam_schedule, name='exam_schedule'),
    path('timetable/', views.timetable, name='timetable'),
    path('announcements/', views.announcements, name='announcements'),
    path('resources/', views.resources, name='resources'),
    path('communication/', views.communication, name='communication'),
    path('profile/', views.profile, name='profile'),
    path('fees/', views.fees, name='fees'),
]
