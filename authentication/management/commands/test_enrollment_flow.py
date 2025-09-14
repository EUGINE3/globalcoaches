from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faculties.models import Faculty, AcademicLevel, FacultyProgram
from students.models import StudentEnrollment
from courses.models import Module, ModuleProgress
from courses.utils import ProgressiveAccessManager


class Command(BaseCommand):
    help = 'Test the enrollment and progressive access flow'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Testing Enrollment Flow ==='))
        
        # Create or get test user
        test_user, created = User.objects.get_or_create(
            username='enrolltest',
            defaults={
                'email': 'enrolltest@example.com',
                'first_name': 'Enroll',
                'last_name': 'Test',
                'is_active': True,
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Created test user'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Using existing test user'))
        
        # Get first faculty
        faculty = Faculty.objects.first()
        if not faculty:
            self.stdout.write(self.style.ERROR('✗ No faculties found'))
            return
        
        self.stdout.write(f'📚 Testing with faculty: {faculty.name}')
        
        # Get academic level
        academic_level = AcademicLevel.objects.filter(level_type='masterclass').first()
        if not academic_level:
            self.stdout.write(self.style.ERROR('✗ No masterclass academic level found'))
            return
        
        # Get or create faculty program
        faculty_program, created = FacultyProgram.objects.get_or_create(
            faculty=faculty,
            academic_level=academic_level,
            defaults={
                'program_structure': f'Test program for {faculty.name}',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created faculty program'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Using existing faculty program'))
        
        # Clean up existing enrollment
        StudentEnrollment.objects.filter(
            student=test_user,
            faculty_program=faculty_program
        ).delete()
        
        # Create enrollment
        enrollment = StudentEnrollment.objects.create(
            student=test_user,
            faculty_program=faculty_program,
            status='active',
            notes='Test enrollment'
        )
        self.stdout.write(self.style.SUCCESS('✓ Created active enrollment'))
        
        # Test progressive access initialization
        try:
            access_manager = ProgressiveAccessManager()
            access_manager.initialize_student_progress(test_user)
            self.stdout.write(self.style.SUCCESS('✓ Initialized progressive access'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Progressive access initialization failed: {e}'))
        
        # Check module access
        modules = Module.objects.filter(faculty_program=faculty_program)
        self.stdout.write(f'\n📖 Found {modules.count()} modules for this program:')
        
        for module in modules:
            progress = ModuleProgress.objects.filter(
                student=test_user,
                module=module
            ).first()
            
            if progress:
                status = "✓ ACCESSIBLE" if progress.is_unlocked else "🔒 LOCKED"
                self.stdout.write(f'   {module.title}: {status}')
            else:
                self.stdout.write(f'   {module.title}: ❌ NO PROGRESS RECORD')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Enrollment flow test completed!'))
        self.stdout.write(f'Test user: {test_user.username}')
        self.stdout.write(f'Password: testpass123')
        self.stdout.write(f'Faculty: {faculty.name}')
        self.stdout.write(f'Program: {faculty_program}')
        self.stdout.write(f'Enrollment Status: {enrollment.status}')
        
        # Login instructions
        self.stdout.write('\n📝 To test manually:')
        self.stdout.write('1. Login with the test user credentials above')
        self.stdout.write('2. Visit /dashboard/ to see enrolled courses')
        self.stdout.write('3. Check module access and progressive unlocking')
