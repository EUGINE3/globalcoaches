from django.urls import path
from . import views

app_name = 'mentorship'

urlpatterns = [
    path('', views.mentorship_portal, name='mentorship_portal'),
    path('pairing/', views.mentor_pairing, name='mentor_pairing'),
    path('checkin/', views.weekly_checkin, name='weekly_checkin'),
    path('peer-review/<int:assignment_id>/', views.peer_review, name='peer_review'),
]

