from django.urls import path
from . import views, views_discussions, quiz_views

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

    # Quiz URLs
    path('quiz/<int:assignment_id>/', quiz_views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:assignment_id>/start/', quiz_views.start_quiz, name='start_quiz'),
    path('quiz/<int:assignment_id>/take/', quiz_views.take_quiz, name='take_quiz'),
    path('quiz/submission/<int:submission_id>/results/', quiz_views.quiz_results, name='quiz_results'),
    path('quiz/submission/<int:submission_id>/check-time/', quiz_views.check_quiz_time, name='check_quiz_time'),

    # Discussion URLs
    path('module/<int:module_id>/discussion/', views_discussions.module_discussion, name='module_discussion'),
    path('topic/<int:topic_id>/discussion/', views_discussions.topic_discussion, name='topic_discussion'),
    path('discussion/post/<int:post_id>/', views_discussions.discussion_post_detail, name='discussion_post_detail'),
    path('api/discussion/post/<int:post_id>/like/', views_discussions.like_post, name='like_post'),
    path('api/discussion/post/<int:post_id>/delete/', views_discussions.delete_post, name='delete_post'),
]

