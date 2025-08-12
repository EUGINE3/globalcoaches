from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication views
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Email verification
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('verification-sent/', views.verification_sent, name='verification_sent'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    
    # Password reset
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('password-reset-sent/', views.password_reset_sent, name='password_reset_sent'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    
    # Password change
    path('change-password/', views.change_password, name='change_password'),
    
    # AJAX endpoints
    path('api/check-username/', views.check_username_availability, name='check_username'),
    path('api/check-email/', views.check_email_availability, name='check_email'),
]
