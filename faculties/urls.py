from django.urls import path
from . import views

app_name = 'faculties'

urlpatterns = [
    path('', views.program_overview, name='program_overview'),
    path('level/<int:level_id>/', views.program_level_detail, name='program_level_detail'),
    path('module/<int:module_id>/', views.module_detail, name='module_detail'),
    path('level/<int:level_id>/apply/', views.apply_to_program, name='apply_to_program'),
]

