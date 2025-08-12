from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import uuid
import secrets
from datetime import timedelta


class EmailVerificationToken(models.Model):
    """Token for email verification during user registration"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification_token')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(seconds=settings.EMAIL_VERIFICATION_TOKEN_EXPIRY)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired

    def mark_as_used(self):
        self.is_used = True
        self.save()

    def __str__(self):
        return f"Email verification token for {self.user.username}"


class PasswordResetToken(models.Model):
    """Token for password reset functionality"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(seconds=settings.PASSWORD_RESET_TOKEN_EXPIRY)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired

    def mark_as_used(self):
        self.is_used = True
        self.save()

    def __str__(self):
        return f"Password reset token for {self.user.username}"


class LoginAttempt(models.Model):
    """Track login attempts for security"""
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{status} login attempt for {self.username} at {self.timestamp}"


class EmailChangeRequest(models.Model):
    """Handle email change requests with verification"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_change_requests')
    new_email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(seconds=settings.EMAIL_VERIFICATION_TOKEN_EXPIRY)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired

    def mark_as_used(self):
        self.is_used = True
        self.save()

    def __str__(self):
        return f"Email change request for {self.user.username} to {self.new_email}"
