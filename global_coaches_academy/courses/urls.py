from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('module/<int:module_id>/', views.module_detail, name='module_detail'),
    path('module/<int:module_id>/week/<int:week_number>/', views.week_detail, name='week_detail'),
    path('assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
]

