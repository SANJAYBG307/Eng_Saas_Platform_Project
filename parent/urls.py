"""
Parent App URLs - Multi-Tenant SaaS Platform
URL patterns for parent portal
"""

from django.urls import path
from . import views

app_name = 'parent'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('child/<int:student_id>/performance/', views.child_performance, name='child_performance'),
    path('child/<int:student_id>/attendance/', views.attendance_tracking, name='attendance_tracking'),
    path('child/<int:student_id>/grades/', views.grades_view, name='grades_view'),
    path('child/<int:student_id>/fees/', views.fee_payments, name='fee_payments'),
    path('child/<int:student_id>/exam-schedule/', views.exam_schedules, name='exam_schedules'),
    path('child/<int:student_id>/timetable/', views.timetable, name='timetable'),
    path('announcements/', views.announcements, name='announcements'),
    path('communication/', views.communication, name='communication'),
    path('reports/', views.reports, name='reports'),
]
