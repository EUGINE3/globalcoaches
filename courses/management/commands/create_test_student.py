from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import StudentEnrollment
from faculties.models import FacultyProgram
from courses.utils import ProgressiveAccessManager
from core.models import UserProfile


class Command(BaseCommand):
    help = 'Create a test student for progressive learning testing'

    def handle(self, *args, **options):
        # Create test user
        username = 'teststudent'
        email = 'test@example.com'
        password = 'testpass123'
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))
            user = User.objects.get(username=username)
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Test',
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

        # Create enrollment if it doesn't exist
        enrollment, created = StudentEnrollment.objects.get_or_create(
            student=user,
            faculty_program=faculty_program,
            defaults={
                'status': 'active',
                'total_credits_earned': 0
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created enrollment for {faculty_program}'))
        else:
            self.stdout.write(self.style.WARNING('Enrollment already exists'))

        # Initialize progressive learning
        ProgressiveAccessManager.initialize_student_progress(user, faculty_program)
        self.stdout.write(self.style.SUCCESS('Initialized progressive learning'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTest student created successfully!\n'
                f'Username: {username}\n'
                f'Password: {password}\n'
                f'Email: {email}\n'
                f'Enrolled in: {faculty_program}'
            )
        )
