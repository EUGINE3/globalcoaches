from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.program_overview, name='program_overview'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('my-learning-path/', views.progressive_modules, name='progressive_modules'),
    path('module/<int:module_id>/', views.module_detail, name='module_detail'),
    path('module/<int:module_id>/week/<int:week_number>/', views.week_detail, name='week_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('progress/', views.student_progress_overview, name='progress_overview'),
    path('api/resource/<int:resource_id>/viewed/', views.mark_resource_viewed, name='mark_resource_viewed'),
    path('api/resource/<int:resource_id>/completed/', views.mark_resource_completed, name='mark_resource_completed'),
    path('api/lesson/<int:lesson_id>/completed/', views.mark_lesson_completed, name='mark_lesson_completed'),
]

