from django.urls import path
from . import views

app_name = 'faculties'

urlpatterns = [
    path('', views.faculty_overview, name='faculty_overview'),
    path('<int:faculty_id>/', views.faculty_detail, name='faculty_detail'),
    path('<int:faculty_id>/apply/', views.apply_to_faculty, name='apply_to_faculty'),
]

