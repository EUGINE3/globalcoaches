from django.contrib import admin
from .models import EmailVerificationToken, PasswordResetToken, LoginAttempt, EmailChangeRequest


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_used', 'is_expired')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email', 'token')
    readonly_fields = ('token', 'created_at', 'expires_at', 'is_expired')

    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_used', 'is_expired', 'ip_address')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email', 'token', 'ip_address')
    readonly_fields = ('token', 'created_at', 'expires_at', 'is_expired')

    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('username', 'success', 'ip_address', 'timestamp')
    list_filter = ('success', 'timestamp')
    search_fields = ('username', 'ip_address')
    readonly_fields = ('username', 'ip_address', 'user_agent', 'success', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(EmailChangeRequest)
class EmailChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'new_email', 'created_at', 'expires_at', 'is_used', 'is_expired')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email', 'new_email', 'token')
    readonly_fields = ('token', 'created_at', 'expires_at', 'is_expired')

    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
