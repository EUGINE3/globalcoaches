from django.core.management.base import BaseCommand
from authentication.utils import cleanup_expired_tokens


class Command(BaseCommand):
    help = 'Clean up expired authentication tokens and old login attempts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be deleted'))
            
            from django.utils import timezone
            from authentication.models import EmailVerificationToken, PasswordResetToken, LoginAttempt
            
            # Count expired tokens
            expired_email_tokens = EmailVerificationToken.objects.filter(
                expires_at__lt=timezone.now()
            ).count()
            
            expired_password_tokens = PasswordResetToken.objects.filter(
                expires_at__lt=timezone.now()
            ).count()
            
            old_attempts = LoginAttempt.objects.filter(
                timestamp__lt=timezone.now() - timezone.timedelta(days=30)
            ).count()
            
            self.stdout.write(f'Would delete:')
            self.stdout.write(f'  - {expired_email_tokens} expired email verification tokens')
            self.stdout.write(f'  - {expired_password_tokens} expired password reset tokens')
            self.stdout.write(f'  - {old_attempts} old login attempts (>30 days)')
            
        else:
            if cleanup_expired_tokens():
                self.stdout.write(
                    self.style.SUCCESS('Successfully cleaned up expired tokens')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to clean up expired tokens')
                )
