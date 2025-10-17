from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.redirect_to_auth_login, name='login'),
    path('logout/', views.redirect_to_auth_logout, name='logout'),
    path('register/', views.redirect_to_auth_register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/trainer/', views.trainer_dashboard, name='trainer_dashboard'),
    path('profile/update/', views.profile_update, name='profile_update'),
]

