from django.core.management.base import BaseCommand
from students.models import StudentEnrollment
from courses.models import Module, Week, ModuleProgress, WeekProgress


class Command(BaseCommand):
    help = 'Ensure all enrolled students have access to Week 1 of their first module'

    def handle(self, *args, **options):
        # Get all active student enrollments
        enrollments = StudentEnrollment.objects.filter(status='active')
        
        self.stdout.write(f'Found {enrollments.count()} active enrollments')
        
        for enrollment in enrollments:
            student = enrollment.student
            faculty_program = enrollment.faculty_program
            
            # Get first module in the program
            first_module = Module.objects.filter(
                faculty_program=faculty_program,
                is_active=True
            ).order_by('month_number').first()
            
            if not first_module:
                self.stdout.write(
                    self.style.WARNING(f'No modules found for {faculty_program}')
                )
                continue
            
            # Ensure module progress exists and is unlocked
            module_progress, created = ModuleProgress.objects.get_or_create(
                student=student,
                module=first_module
            )
            
            if not module_progress.is_unlocked:
                module_progress.is_unlocked = True
                module_progress.save()
                self.stdout.write(f'  ✓ Unlocked module {first_module.course_code} for {student.username}')
            
            # Get first week of first module
            first_week = first_module.weeks.filter(week_number=1).first()
            
            if first_week:
                # Ensure week progress exists and is unlocked
                week_progress, created = WeekProgress.objects.get_or_create(
                    student=student,
                    week=first_week
                )
                
                if not week_progress.is_unlocked:
                    week_progress.is_unlocked = True
                    week_progress.save()
                    self.stdout.write(f'  ✓ Unlocked Week 1 for {student.username}')
                
                self.stdout.write(f'✓ {student.username} can access {first_module.course_code} Week 1')
            else:
                self.stdout.write(
                    self.style.WARNING(f'No Week 1 found in {first_module.course_code}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully ensured Week 1 access for all enrolled students')
        )
