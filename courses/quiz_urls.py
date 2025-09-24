from django.urls import path
from . import views, views_discussions
from . import quiz_views

app_name = 'courses'

urlpatterns = [
    # ... existing URL patterns ...
    
    # Quiz URLs
    path('quiz/<int:assignment_id>/', quiz_views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:assignment_id>/start/', quiz_views.start_quiz, name='start_quiz'),
    path('quiz/<int:assignment_id>/take/', quiz_views.take_quiz, name='take_quiz'),
    path('quiz/submission/<int:submission_id>/results/', quiz_views.quiz_results, name='quiz_results'),
    path('quiz/submission/<int:submission_id>/check-time/', quiz_views.check_quiz_time, name='check_quiz_time'),
]
