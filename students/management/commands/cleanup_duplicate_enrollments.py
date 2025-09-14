from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import StudentEnrollment
from django.db.models import Count


class Command(BaseCommand):
    help = 'Clean up duplicate student enrollments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('Checking for duplicate enrollments...'))
        
        # Find users with multiple enrollments
        users_with_duplicates = User.objects.annotate(
            enrollment_count=Count('enrollments')
        ).filter(enrollment_count__gt=1)
        
        if not users_with_duplicates.exists():
            self.stdout.write(self.style.SUCCESS('No duplicate enrollments found!'))
            return
        
        total_duplicates_removed = 0
        
        for user in users_with_duplicates:
            enrollments = StudentEnrollment.objects.filter(student=user).order_by('-enrollment_date')
            
            self.stdout.write(f'\nUser: {user.username} has {enrollments.count()} enrollments:')
            
            for i, enrollment in enumerate(enrollments):
                status_indicator = "✓ KEEP" if i == 0 else "✗ REMOVE"
                self.stdout.write(f'  {status_indicator} - {enrollment.program_level.name} ({enrollment.status}) - {enrollment.enrollment_date}')
            
            # Keep the most recent enrollment (first in the ordered queryset)
            if not dry_run:
                duplicates_to_remove = enrollments[1:]  # All except the first (most recent)
                for duplicate in duplicates_to_remove:
                    duplicate.delete()
                    total_duplicates_removed += 1
                    self.stdout.write(f'    Removed: {duplicate.program_level.name}')
            else:
                total_duplicates_removed += enrollments.count() - 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\nDRY RUN: Would remove {total_duplicates_removed} duplicate enrollments')
            )
            self.stdout.write('Run without --dry-run to actually remove duplicates')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Removed {total_duplicates_removed} duplicate enrollments')
            )
            
        self.stdout.write('\nFinal enrollment counts:')
        for user in User.objects.annotate(enrollment_count=Count('enrollments')).filter(enrollment_count__gt=0):
            self.stdout.write(f'  {user.username}: {user.enrollment_count} enrollment(s)')
