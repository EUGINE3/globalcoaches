from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import Module, Week
from courses.utils import ProgressiveAccessManager
from students.models import StudentEnrollment


class Command(BaseCommand):
    help = 'Verify progressive access is working correctly'

    def handle(self, *args, **options):
        # Test with the fresh student
        try:
            user = User.objects.get(username='freshstudent')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Fresh student not found. Run create_fresh_test_student first.'))
            return

        # Get enrollment
        enrollment = StudentEnrollment.objects.filter(student=user, status='active').first()
        if not enrollment:
            self.stdout.write(self.style.ERROR('No active enrollment found for test student'))
            return

        self.stdout.write(f'Testing progressive access for: {user.username}')
        self.stdout.write(f'Enrolled in: {enrollment.faculty_program}')

        # Get modules in order
        modules = Module.objects.filter(
            faculty_program=enrollment.faculty_program,
            is_active=True
        ).order_by('month_number')

        self.stdout.write(f'\nFound {modules.count()} modules')

        for module in modules:
            can_access = ProgressiveAccessManager.can_access_module(user, module)
            self.stdout.write(f'\nModule: {module.course_code} - {module.name}')
            self.stdout.write(f'  Access: {"✓ ALLOWED" if can_access else "✗ BLOCKED"}')

            if can_access:
                # Check weeks in this module
                weeks = module.weeks.all().order_by('week_number')
                for week in weeks:
                    week_access = ProgressiveAccessManager.can_access_week(user, week)
                    week_progress = week.get_or_create_progress(user)
                    
                    status = "COMPLETED" if week_progress.is_completed else "AVAILABLE" if week_access else "LOCKED"
                    icon = "✓" if week_progress.is_completed else "○" if week_access else "✗"
                    
                    self.stdout.write(f'    Week {week.week_number}: {week.theme} - {icon} {status}')

        # Test specific scenarios
        self.stdout.write('\n=== Specific Tests ===')
        
        # Test 1: First module should be accessible
        first_module = modules.first()
        if first_module:
            access = ProgressiveAccessManager.can_access_module(user, first_module)
            self.stdout.write(f'Test 1 - First module access: {"PASS" if access else "FAIL"}')
            
            # Test 2: First week should be accessible
            first_week = first_module.weeks.filter(week_number=1).first()
            if first_week:
                week_access = ProgressiveAccessManager.can_access_week(user, first_week)
                self.stdout.write(f'Test 2 - First week access: {"PASS" if week_access else "FAIL"}')
                
                # Test 3: Second week should be locked initially
                second_week = first_module.weeks.filter(week_number=2).first()
                if second_week:
                    second_access = ProgressiveAccessManager.can_access_week(user, second_week)
                    self.stdout.write(f'Test 3 - Second week locked: {"PASS" if not second_access else "FAIL"}')

        # Test 4: Second module should be locked initially
        if modules.count() > 1:
            second_module = modules[1]
            second_module_access = ProgressiveAccessManager.can_access_module(user, second_module)
            self.stdout.write(f'Test 4 - Second module locked: {"PASS" if not second_module_access else "FAIL"}')

        self.stdout.write('\n=== Progressive Access Verification Complete ===')
        self.stdout.write('✓ Week 1 should be accessible to all enrolled students')
        self.stdout.write('✓ Subsequent weeks require previous week completion')
        self.stdout.write('✓ Subsequent modules require previous module completion')
