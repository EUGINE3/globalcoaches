"""
Management command to create demo data for the progressive learning system
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from programs.models import ProgramLevel
from courses.models import Module, ProgramModule, ModuleProgress
from courses.utils import ProgressiveAccessManager
from students.models import StudentEnrollment


class Command(BaseCommand):
    help = 'Create demo data to test the progressive learning system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='demo_student',
            help='Username for the demo student',
        )

    def handle(self, *args, **options):
        username = options['username']
        
        self.stdout.write(self.style.SUCCESS(f'Creating demo data for progressive learning system...'))

        # Create or get demo student
        student, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': 'Demo',
                'last_name': 'Student',
                'email': f'{username}@example.com',
                'is_active': True
            }
        )
        
        if created:
            student.set_password('demo123')
            student.save()
            self.stdout.write(f'Created demo student: {username}')
        else:
            self.stdout.write(f'Using existing student: {username}')

        # Get or create program level
        program_level = ProgramLevel.objects.filter(is_active=True).first()
        if not program_level:
            self.stdout.write(self.style.ERROR('No active program levels found. Please create one first.'))
            return

        # Create enrollment
        enrollment, created = StudentEnrollment.objects.get_or_create(
            student=student,
            program_level=program_level,
            defaults={
                'status': 'active',
                'enrollment_date': timezone.now()
            }
        )
        
        if created:
            self.stdout.write(f'Created enrollment for {username} in {program_level.name}')
        else:
            self.stdout.write(f'Using existing enrollment for {username} in {program_level.name}')

        # Initialize progressive access
        result = ProgressiveAccessManager.initialize_student_progress(student)
        self.stdout.write(f'Initialization result: {result}')

        # Display current progression
        self.stdout.write('\n=== Current Module Progression ===')
        progression = ProgressiveAccessManager.get_student_module_progression(student, program_level)
        
        for item in progression:
            module = item['module']
            status = item['status']
            progress = item['progress']
            
            status_icon = {
                'locked': '🔒',
                'unlocked': '🔓',
                'completed': '✅'
            }.get(status, '❓')
            
            progress_pct = progress.progress_percentage if progress else 0
            
            self.stdout.write(
                f'{status_icon} Module {module.sequence_order}: {module.module.name} '
                f'({status.upper()}) - {progress_pct}%'
            )
            
            if item['prerequisites']:
                prereq_names = [p['module'].module.name for p in item['prerequisites']]
                self.stdout.write(f'   Prerequisites: {", ".join(prereq_names)}')

        # Show next available module
        next_module = ProgressiveAccessManager.get_next_available_module(student, program_level)
        if next_module:
            self.stdout.write(f'\n🎯 Next module to work on: {next_module.module.name}')
        else:
            self.stdout.write('\n🎉 All modules completed or no modules available!')

        # Simulate some progress
        self.stdout.write('\n=== Simulating Progress ===')
        
        # Find the first unlocked module and simulate completion
        for item in progression:
            if item['status'] == 'unlocked' and item['progress']:
                module_progress = item['progress']
                
                # Simulate 100% completion
                module_progress.progress_percentage = 100
                module_progress.is_completed = True
                module_progress.completed_at = timezone.now()
                module_progress.save()
                
                self.stdout.write(f'✅ Completed: {item["module"].module.name}')
                
                # Unlock next modules
                unlocked = ProgressiveAccessManager.unlock_next_modules(student, item['module'])
                for unlocked_module in unlocked:
                    self.stdout.write(f'🔓 Unlocked: {unlocked_module.module.name}')
                
                break

        # Display updated progression
        self.stdout.write('\n=== Updated Module Progression ===')
        updated_progression = ProgressiveAccessManager.get_student_module_progression(student, program_level)
        
        for item in updated_progression:
            module = item['module']
            status = item['status']
            progress = item['progress']
            
            status_icon = {
                'locked': '🔒',
                'unlocked': '🔓',
                'completed': '✅'
            }.get(status, '❓')
            
            progress_pct = progress.progress_percentage if progress else 0
            
            self.stdout.write(
                f'{status_icon} Module {module.sequence_order}: {module.module.name} '
                f'({status.upper()}) - {progress_pct}%'
            )

        self.stdout.write(f'\n🌟 Demo data created successfully!')
        self.stdout.write(f'📚 Student: {username}')
        self.stdout.write(f'🎓 Program: {program_level.name}')
        self.stdout.write(f'🔗 Access the learning path at: http://127.0.0.1:8001/programs/my-learning-path/')
        
        if created:
            self.stdout.write(f'🔑 Login credentials: {username} / demo123')
