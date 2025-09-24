from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.utils import timezone
from .models import EmailVerificationToken, PasswordResetToken, EmailChangeRequest
from .utils import (
    send_verification_email, send_password_reset_email,
    send_password_changed_notification, send_welcome_email,
    log_login_attempt, is_rate_limited
)
from core.models import UserProfile
import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def register_view(request):
    """User registration with email verification"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        # Validation
        errors = []

        if not username:
            errors.append('Username is required.')
        elif User.objects.filter(username=username).exists():
            errors.append('Username already exists.')

        if not email:
            errors.append('Email is required.')
        elif User.objects.filter(email=email).exists():
            errors.append('Email already registered.')

        if not password1:
            errors.append('Password is required.')
        elif password1 != password2:
            errors.append('Passwords do not match.')
        else:
            try:
                validate_password(password1)
            except ValidationError as e:
                errors.extend(e.messages)

        if not first_name:
            errors.append('First name is required.')

        if not last_name:
            errors.append('Last name is required.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'authentication/register.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            })

        try:
            # Create user (active immediately - no email verification required)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                is_active=True  # Active immediately
            )

            # Create user profile
            UserProfile.objects.create(user=user)

            # Send welcome email (optional)
            send_welcome_email(user)

            messages.success(
                request,
                f'Registration successful! You can now log in with your credentials.'
            )
            return redirect('authentication:login')

        except Exception as e:
            logger.error(f"Registration error: {e}")
            messages.error(request, 'Registration failed. Please try again.')

    return render(request, 'authentication/register.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login with rate limiting"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    # Check rate limiting
    if is_rate_limited(request, 'login'):
        messages.error(request, 'Too many failed login attempts. Please try again later.')
        return render(request, 'authentication/login.html')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'authentication/login.html', {'username': username})

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                log_login_attempt(username, request, success=True)

                # Redirect to next page or dashboard
                next_url = request.GET.get('next', 'core:dashboard')
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect(next_url)
            else:
                log_login_attempt(username, request, success=False)
                messages.error(request, 'Your account has been deactivated. Please contact support.')
        else:
            log_login_attempt(username, request, success=False)
            messages.error(request, 'Invalid username or password.')

        return render(request, 'authentication/login.html', {'username': username})

    return render(request, 'authentication/login.html')


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:landing_page')


def verify_email(request, token):
    """Verify email address using token"""
    try:
        verification_token = get_object_or_404(EmailVerificationToken, token=token)

        if not verification_token.is_valid:
            if verification_token.is_used:
                messages.info(request, 'This verification link has already been used.')
            else:
                messages.error(request, 'This verification link has expired. Please request a new one.')
            return redirect('authentication:login')

        # Activate user account
        user = verification_token.user
        user.is_active = True
        user.save()

        # Mark token as used
        verification_token.mark_as_used()

        # Send welcome email
        send_welcome_email(user)

        messages.success(request, 'Your email has been verified successfully! You can now log in.')
        return redirect('authentication:login')

    except Exception as e:
        logger.error(f"Email verification error: {e}")
        messages.error(request, 'Invalid verification link.')
        return redirect('authentication:login')


def verification_sent(request):
    """Show verification sent page"""
    return render(request, 'authentication/verification_sent.html')


@require_http_methods(["GET", "POST"])
def forgot_password(request):
    """Forgot password - send reset email"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'authentication/forgot_password.html')

        try:
            user = User.objects.get(email=email, is_active=True)

            # Send password reset email
            if send_password_reset_email(user, request):
                messages.success(request, 'Password reset instructions have been sent to your email.')
                return redirect('authentication:password_reset_sent')
            else:
                messages.error(request, 'Failed to send password reset email. Please try again.')

        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(request, 'If an account with this email exists, password reset instructions have been sent.')
            return redirect('authentication:password_reset_sent')

        except Exception as e:
            logger.error(f"Password reset error: {e}")
            messages.error(request, 'An error occurred. Please try again.')

    return render(request, 'authentication/forgot_password.html')


def password_reset_sent(request):
    """Show password reset sent page"""
    return render(request, 'authentication/password_reset_sent.html')


@require_http_methods(["GET", "POST"])
def reset_password(request, token):
    """Reset password using token"""
    try:
        reset_token = get_object_or_404(PasswordResetToken, token=token)

        if not reset_token.is_valid:
            if reset_token.is_used:
                messages.error(request, 'This password reset link has already been used.')
            else:
                messages.error(request, 'This password reset link has expired. Please request a new one.')
            return redirect('authentication:forgot_password')

        if request.method == 'POST':
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')

            if not password1:
                messages.error(request, 'Password is required.')
            elif password1 != password2:
                messages.error(request, 'Passwords do not match.')
            else:
                try:
                    validate_password(password1, reset_token.user)

                    # Set new password
                    user = reset_token.user
                    user.set_password(password1)
                    user.save()

                    # Mark token as used
                    reset_token.mark_as_used()

                    # Send notification email
                    send_password_changed_notification(user)

                    messages.success(request, 'Your password has been reset successfully. You can now log in.')
                    return redirect('authentication:login')

                except ValidationError as e:
                    for error in e.messages:
                        messages.error(request, error)

        return render(request, 'authentication/reset_password.html', {'token': token})

    except Exception as e:
        logger.error(f"Password reset error: {e}")
        messages.error(request, 'Invalid password reset link.')
        return redirect('authentication:forgot_password')


@login_required
@require_http_methods(["GET", "POST"])
def change_password(request):
    """Change password for authenticated users"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password1 = request.POST.get('new_password1', '')
        new_password2 = request.POST.get('new_password2', '')

        # Validation
        if not current_password:
            messages.error(request, 'Current password is required.')
        elif not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        elif not new_password1:
            messages.error(request, 'New password is required.')
        elif new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
        else:
            try:
                validate_password(new_password1, request.user)

                # Set new password
                request.user.set_password(new_password1)
                request.user.save()

                # Update session to prevent logout
                update_session_auth_hash(request, request.user)

                # Send notification email
                send_password_changed_notification(request.user)

                messages.success(request, 'Your password has been changed successfully.')
                return redirect('core:dashboard')

            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)

    return render(request, 'authentication/change_password.html')


@login_required
@require_POST
def resend_verification(request):
    """Resend email verification for inactive users"""
    if request.user.is_active:
        messages.info(request, 'Your account is already verified.')
        return redirect('core:dashboard')

    if send_verification_email(request.user, request):
        messages.success(request, 'Verification email has been resent. Please check your inbox.')
    else:
        messages.error(request, 'Failed to send verification email. Please try again.')

    return redirect('authentication:verification_sent')


@require_POST
def check_username_availability(request):
    """AJAX endpoint to check username availability"""
    username = request.POST.get('username', '').strip()

    if not username:
        return JsonResponse({'available': False, 'message': 'Username is required.'})

    if len(username) < 3:
        return JsonResponse({'available': False, 'message': 'Username must be at least 3 characters long.'})

    if User.objects.filter(username=username).exists():
        return JsonResponse({'available': False, 'message': 'Username is already taken.'})

    return JsonResponse({'available': True, 'message': 'Username is available.'})


@require_POST
def check_email_availability(request):
    """AJAX endpoint to check email availability"""
    email = request.POST.get('email', '').strip().lower()

    if not email:
        return JsonResponse({'available': False, 'message': 'Email is required.'})

    if User.objects.filter(email=email).exists():
        return JsonResponse({'available': False, 'message': 'Email is already registered.'})

    return JsonResponse({'available': True, 'message': 'Email is available.'})
