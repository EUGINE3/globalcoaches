from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import StudentEnrollment
from courses.utils import ProgressiveAccessManager


class Command(BaseCommand):
    help = 'Initialize progressive learning for existing students'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all existing progress (use with caution)',
        )

    def handle(self, *args, **options):
        reset = options['reset']
        
        if reset:
            self.stdout.write(self.style.WARNING('Resetting all existing progress...'))
            from courses.models import ModuleProgress, WeekProgress, ResourceView
            ModuleProgress.objects.all().delete()
            WeekProgress.objects.all().delete()
            ResourceView.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All progress reset.'))

        # Get all active student enrollments
        enrollments = StudentEnrollment.objects.filter(status='active')
        
        self.stdout.write(f'Found {enrollments.count()} active enrollments')
        
        for enrollment in enrollments:
            self.stdout.write(f'Initializing progress for {enrollment.student.username} in {enrollment.faculty_program}')
            
            # Initialize progressive access for this student
            ProgressiveAccessManager.initialize_student_progress(
                enrollment.student,
                enrollment.faculty_program
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Initialized progress for {enrollment.student.username}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully initialized progressive learning for {enrollments.count()} students')
        )
