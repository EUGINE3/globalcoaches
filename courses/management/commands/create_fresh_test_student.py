from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import StudentEnrollment
from faculties.models import FacultyProgram
from courses.models import ModuleProgress, WeekProgress, ResourceView
from courses.utils import ProgressiveAccessManager
from core.models import UserProfile


class Command(BaseCommand):
    help = 'Create a fresh test student with no progress for testing'

    def handle(self, *args, **options):
        # Create fresh test user
        username = 'freshstudent'
        email = 'fresh@example.com'
        password = 'testpass123'
        
        # Delete existing user if exists
        if User.objects.filter(username=username).exists():
            old_user = User.objects.get(username=username)
            # Clean up all progress
            ModuleProgress.objects.filter(student=old_user).delete()
            WeekProgress.objects.filter(student=old_user).delete()
            ResourceView.objects.filter(student=old_user).delete()
            StudentEnrollment.objects.filter(student=old_user).delete()
            UserProfile.objects.filter(user=old_user).delete()
            old_user.delete()
            self.stdout.write(self.style.WARNING(f'Deleted existing user: {username}'))

        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Fresh',
            last_name='Student'
        )
        self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            country='US',
            town='Test City',
            institution='Test University'
        )
        self.stdout.write(self.style.SUCCESS('Created user profile'))

        # Get first faculty program
        faculty_program = FacultyProgram.objects.first()
        if not faculty_program:
            self.stdout.write(self.style.ERROR('No faculty programs found'))
            return

        # Create enrollment
        enrollment = StudentEnrollment.objects.create(
            student=user,
            faculty_program=faculty_program,
            status='active',
            total_credits_earned=0
        )
        self.stdout.write(self.style.SUCCESS(f'Created enrollment for {faculty_program}'))

        # DO NOT initialize progressive learning - let it happen naturally
        self.stdout.write(self.style.SUCCESS('Fresh student created without any progress'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nFresh test student created successfully!\n'
                f'Username: {username}\n'
                f'Password: {password}\n'
                f'Email: {email}\n'
                f'Enrolled in: {faculty_program}\n'
                f'Progress: NONE (fresh start)'
            )
        )
