from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from authentication.utils import (
    send_verification_email, send_password_reset_email,
    send_password_changed_notification, send_welcome_email
)
from authentication.models import EmailVerificationToken, PasswordResetToken
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test the email system functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test emails to',
            default='test@example.com'
        )
        parser.add_argument(
            '--test-smtp',
            action='store_true',
            help='Test SMTP connection',
        )

    def handle(self, *args, **options):
        test_email = options['email']
        test_smtp = options['test_smtp']
        
        self.stdout.write(self.style.SUCCESS('=== Email System Test ==='))
        
        # Test 1: SMTP Connection
        if test_smtp:
            self.stdout.write('\n1. Testing SMTP Connection...')
            try:
                send_mail(
                    subject='Test Email - Global Coaches Academy',
                    message='This is a test email to verify SMTP configuration.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[test_email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS('   ✓ SMTP connection successful'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ✗ SMTP connection failed: {e}'))
                return
        
        # Create or get test user
        self.stdout.write('\n2. Creating test user...')
        test_user, created = User.objects.get_or_create(
            username='emailtest',
            defaults={
                'email': test_email,
                'first_name': 'Email',
                'last_name': 'Test',
                'is_active': False,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('   ✓ Test user created'))
        else:
            test_user.email = test_email
            test_user.save()
            self.stdout.write(self.style.WARNING('   ⚠ Using existing test user'))
        
        # Test 2: Email Verification
        self.stdout.write('\n3. Testing email verification...')
        try:
            if send_verification_email(test_user):
                self.stdout.write(self.style.SUCCESS('   ✓ Verification email sent'))
                
                # Show token info
                token = EmailVerificationToken.objects.filter(user=test_user).first()
                if token:
                    verification_url = f"{settings.SITE_URL}/auth/verify-email/{token.token}/"
                    self.stdout.write(f'   📧 Verification URL: {verification_url}')
            else:
                self.stdout.write(self.style.ERROR('   ✗ Failed to send verification email'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Verification email error: {e}'))
        
        # Test 3: Password Reset
        self.stdout.write('\n4. Testing password reset...')
        try:
            # Create a mock request object
            class MockRequest:
                META = {'REMOTE_ADDR': '127.0.0.1', 'HTTP_USER_AGENT': 'Test Command'}
            
            mock_request = MockRequest()
            
            if send_password_reset_email(test_user, mock_request):
                self.stdout.write(self.style.SUCCESS('   ✓ Password reset email sent'))
                
                # Show token info
                token = PasswordResetToken.objects.filter(user=test_user).first()
                if token:
                    reset_url = f"{settings.SITE_URL}/auth/reset-password/{token.token}/"
                    self.stdout.write(f'   📧 Reset URL: {reset_url}')
            else:
                self.stdout.write(self.style.ERROR('   ✗ Failed to send password reset email'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Password reset email error: {e}'))
        
        # Test 4: Password Changed Notification
        self.stdout.write('\n5. Testing password changed notification...')
        try:
            if send_password_changed_notification(test_user):
                self.stdout.write(self.style.SUCCESS('   ✓ Password changed notification sent'))
            else:
                self.stdout.write(self.style.ERROR('   ✗ Failed to send password changed notification'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Password changed notification error: {e}'))
        
        # Test 5: Welcome Email
        self.stdout.write('\n6. Testing welcome email...')
        try:
            if send_welcome_email(test_user):
                self.stdout.write(self.style.SUCCESS('   ✓ Welcome email sent'))
            else:
                self.stdout.write(self.style.ERROR('   ✗ Failed to send welcome email'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Welcome email error: {e}'))
        
        # Test 6: Email Settings Check
        self.stdout.write('\n7. Email configuration check...')
        self.stdout.write(f'   📧 Email Backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'   📧 Email Host: {settings.EMAIL_HOST}')
        self.stdout.write(f'   📧 Email Port: {settings.EMAIL_PORT}')
        self.stdout.write(f'   📧 Use TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'   📧 Default From: {settings.DEFAULT_FROM_EMAIL}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Email system test completed!'))
        self.stdout.write(f'Test emails sent to: {test_email}')
        
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            self.stdout.write(self.style.WARNING(
                'Note: Using console email backend. Check terminal output for email content.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                'Using SMTP backend. Check your email inbox for test messages.'
            ))
        
        # Cleanup
        self.stdout.write('\n8. Cleaning up test data...')
        EmailVerificationToken.objects.filter(user=test_user).delete()
        PasswordResetToken.objects.filter(user=test_user).delete()
        self.stdout.write(self.style.SUCCESS('   ✓ Test tokens cleaned up'))
