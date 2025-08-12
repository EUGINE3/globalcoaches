from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import Module, Week, WeeklyResource, ModuleProgress, WeekProgress, ResourceView
from courses.utils import ProgressiveAccessManager, CompletionTracker
from students.models import StudentEnrollment


class Command(BaseCommand):
    help = 'Test the progressive learning system'

    def handle(self, *args, **options):
        # Get test student
        try:
            user = User.objects.get(username='teststudent')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Test student not found. Run create_test_student first.'))
            return

        # Get sample module
        module = Module.objects.filter(course_code='GCA-SAMPLE-101').first()
        if not module:
            self.stdout.write(self.style.ERROR('Sample module not found. Run create_sample_module first.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Testing progressive system for user: {user.username}'))
        self.stdout.write(f'Module: {module.name}')

        # Test 1: Check initial access
        self.stdout.write('\n=== Test 1: Initial Access ===')
        
        # Check module access
        can_access_module = ProgressiveAccessManager.can_access_module(user, module)
        self.stdout.write(f'Can access module: {can_access_module}')
        
        # Check week access
        weeks = module.weeks.all().order_by('week_number')
        for week in weeks:
            can_access = ProgressiveAccessManager.can_access_week(user, week)
            self.stdout.write(f'Can access Week {week.week_number}: {can_access}')

        # Test 2: Complete first week resources and assignment
        self.stdout.write('\n=== Test 2: Complete Week 1 Resources and Assignment ===')

        week1 = weeks.filter(week_number=1).first()
        if week1:
            resources = week1.learning_resources.filter(is_required=True)
            self.stdout.write(f'Found {resources.count()} required resources in Week 1')

            for resource in resources:
                # Mark resource as viewed and completed
                resource_view = CompletionTracker.mark_resource_completed(user, resource)
                self.stdout.write(f'  ✓ Completed: {resource.title}')

            # Submit assignment if it exists and is required
            if hasattr(week1, 'assignment') and week1.assignment.is_required:
                from courses.models import AssignmentSubmission
                submission, created = AssignmentSubmission.objects.get_or_create(
                    assignment=week1.assignment,
                    student=user,
                    defaults={
                        'text_submission': 'Test submission for progressive learning test',
                    }
                )
                if created:
                    self.stdout.write(f'  ✓ Submitted assignment: {week1.assignment.title}')
                else:
                    self.stdout.write(f'  ✓ Assignment already submitted: {week1.assignment.title}')

            # Check if week is completed
            week_progress = week1.get_or_create_progress(user)
            week_progress.mark_completed()
            self.stdout.write(f'Week 1 completed: {week_progress.is_completed}')

        # Test 3: Check access after completion
        self.stdout.write('\n=== Test 3: Access After Week 1 Completion ===')
        
        for week in weeks:
            can_access = ProgressiveAccessManager.can_access_week(user, week)
            week_progress = week.get_or_create_progress(user)
            self.stdout.write(f'Week {week.week_number}: Access={can_access}, Completed={week_progress.is_completed}')

        # Test 4: Complete all weeks
        self.stdout.write('\n=== Test 4: Complete All Weeks ===')

        for week in weeks[1:]:  # Skip week 1 as it's already completed
            # Complete all required resources
            resources = week.learning_resources.filter(is_required=True)
            for resource in resources:
                CompletionTracker.mark_resource_completed(user, resource)

            # Submit assignment if it exists and is required
            if hasattr(week, 'assignment') and week.assignment.is_required:
                from courses.models import AssignmentSubmission
                submission, created = AssignmentSubmission.objects.get_or_create(
                    assignment=week.assignment,
                    student=user,
                    defaults={
                        'text_submission': f'Test submission for Week {week.week_number}',
                    }
                )

            # Mark week as completed
            week_progress = week.get_or_create_progress(user)
            week_progress.mark_completed()
            self.stdout.write(f'  ✓ Completed Week {week.week_number}')

        # Test 5: Check module completion
        self.stdout.write('\n=== Test 5: Module Completion ===')
        
        module_progress = module.get_or_create_progress(user)
        module_progress.check_completion()
        self.stdout.write(f'Module completed: {module_progress.is_completed}')
        self.stdout.write(f'Module completion percentage: {module_progress.completion_percentage}%')

        # Test 6: Check next action
        self.stdout.write('\n=== Test 6: Next Required Action ===')
        
        enrollment = StudentEnrollment.objects.filter(student=user).first()
        if enrollment:
            next_action = ProgressiveAccessManager.get_next_required_action(
                user, enrollment.faculty_program
            )
            self.stdout.write(f'Next action type: {next_action["type"]}')
            self.stdout.write(f'Next action message: {next_action["message"]}')

        # Test 7: Progress Statistics
        self.stdout.write('\n=== Test 7: Progress Statistics ===')
        
        total_modules = Module.objects.filter(
            faculty_program=enrollment.faculty_program,
            is_active=True
        ).count()
        
        completed_modules = ModuleProgress.objects.filter(
            student=user,
            module__faculty_program=enrollment.faculty_program,
            completed_at__isnull=False
        ).count()
        
        total_weeks = Week.objects.filter(
            module__faculty_program=enrollment.faculty_program,
            module__is_active=True
        ).count()
        
        completed_weeks = WeekProgress.objects.filter(
            student=user,
            week__module__faculty_program=enrollment.faculty_program,
            completed_at__isnull=False
        ).count()
        
        total_resources = WeeklyResource.objects.filter(
            week__module__faculty_program=enrollment.faculty_program,
            week__module__is_active=True,
            is_active=True
        ).count()
        
        completed_resources = ResourceView.objects.filter(
            student=user,
            resource__week__module__faculty_program=enrollment.faculty_program,
            completed=True
        ).count()
        
        self.stdout.write(f'Modules: {completed_modules}/{total_modules}')
        self.stdout.write(f'Weeks: {completed_weeks}/{total_weeks}')
        self.stdout.write(f'Resources: {completed_resources}/{total_resources}')

        self.stdout.write(self.style.SUCCESS('\n=== Progressive Learning Test Complete ==='))
        self.stdout.write('You can now test the UI by visiting:')
        self.stdout.write('- Module detail: /courses/module/1/')
        self.stdout.write('- Progress overview: /courses/progress/')
        self.stdout.write(f'- Login with: teststudent / testpass123')
