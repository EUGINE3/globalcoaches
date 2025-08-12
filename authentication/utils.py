"""
Utility functions for authentication, email verification, and password reset
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from .models import EmailVerificationToken, PasswordResetToken, LoginAttempt
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Get user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')


def log_login_attempt(username, request, success=False):
    """Log login attempt for security tracking"""
    try:
        LoginAttempt.objects.create(
            username=username,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            success=success
        )
    except Exception as e:
        logger.error(f"Failed to log login attempt: {e}")


def send_verification_email(user, request=None):
    """Send email verification email to user"""
    try:
        # Create or get existing token
        token, created = EmailVerificationToken.objects.get_or_create(
            user=user,
            defaults={'is_used': False}
        )
        
        # If token exists but is expired or used, create a new one
        if not token.is_valid:
            token.delete()
            token = EmailVerificationToken.objects.create(user=user)
        
        # Build verification URL
        verification_url = f"{settings.SITE_URL}/auth/verify-email/{token.token}/"
        
        # Prepare email context
        context = {
            'user': user,
            'verification_url': verification_url,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
            'expiry_hours': settings.EMAIL_VERIFICATION_TOKEN_EXPIRY // 3600,
        }
        
        # Render email templates
        html_message = render_to_string('authentication/emails/verify_email.html', context)
        plain_message = render_to_string('authentication/emails/verify_email.txt', context)
        
        # Send email
        send_mail(
            subject=f'Verify your email address - {settings.SITE_NAME}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
        return False


def send_password_reset_email(user, request):
    """Send password reset email to user"""
    try:
        # Create password reset token
        token = PasswordResetToken.objects.create(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        # Build reset URL
        reset_url = f"{settings.SITE_URL}/auth/reset-password/{token.token}/"
        
        # Prepare email context
        context = {
            'user': user,
            'reset_url': reset_url,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
            'expiry_hours': settings.PASSWORD_RESET_TOKEN_EXPIRY // 3600,
            'ip_address': get_client_ip(request),
        }
        
        # Render email templates
        html_message = render_to_string('authentication/emails/password_reset.html', context)
        plain_message = render_to_string('authentication/emails/password_reset.txt', context)
        
        # Send email
        send_mail(
            subject=f'Password Reset Request - {settings.SITE_NAME}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {e}")
        return False


def send_password_changed_notification(user):
    """Send notification when password is successfully changed"""
    try:
        context = {
            'user': user,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
            'timestamp': timezone.now(),
        }
        
        # Render email templates
        html_message = render_to_string('authentication/emails/password_changed.html', context)
        plain_message = render_to_string('authentication/emails/password_changed.txt', context)
        
        # Send email
        send_mail(
            subject=f'Password Changed - {settings.SITE_NAME}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password changed notification sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password changed notification to {user.email}: {e}")
        return False


def send_welcome_email(user):
    """Send welcome email after successful email verification"""
    try:
        context = {
            'user': user,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
            'dashboard_url': f"{settings.SITE_URL}/dashboard/",
        }
        
        # Render email templates
        html_message = render_to_string('authentication/emails/welcome.html', context)
        plain_message = render_to_string('authentication/emails/welcome.txt', context)
        
        # Send email
        send_mail(
            subject=f'Welcome to {settings.SITE_NAME}!',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")
        return False


def is_rate_limited(request, action='login', limit=5, window=300):
    """Check if user is rate limited for specific action"""
    ip_address = get_client_ip(request)
    
    if action == 'login':
        # Check failed login attempts in the last window (5 minutes)
        recent_attempts = LoginAttempt.objects.filter(
            ip_address=ip_address,
            success=False,
            timestamp__gte=timezone.now() - timezone.timedelta(seconds=window)
        ).count()
        
        return recent_attempts >= limit
    
    return False


def cleanup_expired_tokens():
    """Clean up expired tokens (can be run as a periodic task)"""
    try:
        # Delete expired email verification tokens
        expired_email_tokens = EmailVerificationToken.objects.filter(
            expires_at__lt=timezone.now()
        )
        email_count = expired_email_tokens.count()
        expired_email_tokens.delete()
        
        # Delete expired password reset tokens
        expired_password_tokens = PasswordResetToken.objects.filter(
            expires_at__lt=timezone.now()
        )
        password_count = expired_password_tokens.count()
        expired_password_tokens.delete()
        
        # Delete old login attempts (older than 30 days)
        old_attempts = LoginAttempt.objects.filter(
            timestamp__lt=timezone.now() - timezone.timedelta(days=30)
        )
        attempts_count = old_attempts.count()
        old_attempts.delete()
        
        logger.info(f"Cleaned up {email_count} email tokens, {password_count} password tokens, {attempts_count} login attempts")
        return True
        
    except Exception as e:
        logger.error(f"Failed to cleanup expired tokens: {e}")
        return False
