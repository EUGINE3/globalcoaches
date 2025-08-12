from django.core.management.base import BaseCommand
from django.utils import timezone
from faculties.models import FacultyProgram
from courses.models import Module, Week, WeeklyResource, Assignment


class Command(BaseCommand):
    help = 'Create a sample module with weeks and resources for testing'

    def handle(self, *args, **options):
        # Get the first faculty program
        faculty_program = FacultyProgram.objects.first()
        if not faculty_program:
            self.stdout.write(self.style.ERROR('No faculty programs found. Please create one first.'))
            return

        # Create a sample module
        module, created = Module.objects.get_or_create(
            course_code='GCA-SAMPLE-101',
            defaults={
                'faculty_program': faculty_program,
                'name': 'Sample Leadership Module',
                'credits': 3,
                'month_number': 1,
                'description': 'A sample module to demonstrate the weekly resources functionality.',
                'learning_objectives': 'Students will learn about leadership fundamentals and resource management.',
                'is_active': True,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created module: {module.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Module already exists: {module.name}'))

        # Create sample weeks
        weeks_data = [
            {
                'week_number': 1,
                'theme': 'Leadership Foundations',
                'value': 'Integrity & Character',
                'scripture_quote': 'Leadership is not about being in charge. It is about taking care of those in your charge. - Simon Sinek',
                'content': 'This week introduces the foundational concepts of leadership, focusing on character development and integrity as the cornerstone of effective leadership.',
            },
            {
                'week_number': 2,
                'theme': 'Vision & Purpose',
                'value': 'Clarity & Direction',
                'thought_quote': 'Where there is no vision, the people perish. - Proverbs 29:18',
                'content': 'Explore the critical role of vision in leadership and learn how to develop, communicate, and implement a compelling vision.',
            },
            {
                'week_number': 3,
                'theme': 'Team Building',
                'value': 'Collaboration & Unity',
                'content': 'Learn effective strategies for building high-performing teams and fostering collaboration.',
            },
            {
                'week_number': 4,
                'theme': 'Impact Measurement',
                'value': 'Results & Accountability',
                'content': 'Understand how to measure leadership impact and maintain accountability in your leadership journey.',
            },
        ]

        for week_data in weeks_data:
            week, created = Week.objects.get_or_create(
                module=module,
                week_number=week_data['week_number'],
                defaults=week_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created week {week.week_number}: {week.theme}'))
                
                # Create sample resources for each week
                resources_data = [
                    {
                        'title': f'Introduction to {week.theme}',
                        'description': f'A comprehensive overview of {week.theme.lower()} concepts.',
                        'resource_type': 'pdf',
                        'external_url': 'https://example.com/sample-pdf',
                        'is_required': True,
                        'order': 1,
                    },
                    {
                        'title': f'{week.theme} Video Lecture',
                        'description': f'Video lecture covering key aspects of {week.theme.lower()}.',
                        'resource_type': 'video',
                        'external_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                        'is_required': True,
                        'order': 2,
                    },
                    {
                        'title': f'Additional Reading: {week.theme}',
                        'description': 'Supplementary reading material for deeper understanding.',
                        'resource_type': 'link',
                        'external_url': 'https://example.com/additional-reading',
                        'is_required': False,
                        'order': 3,
                    },
                ]
                
                for resource_data in resources_data:
                    resource, res_created = WeeklyResource.objects.get_or_create(
                        week=week,
                        title=resource_data['title'],
                        defaults=resource_data
                    )
                    if res_created:
                        self.stdout.write(f'  - Created resource: {resource.title}')
                
                # Create sample assignment
                assignment, assign_created = Assignment.objects.get_or_create(
                    week=week,
                    defaults={
                        'title': f'Week {week.week_number} Assignment: {week.theme}',
                        'description': f'Complete a practical exercise related to {week.theme.lower()}.',
                        'instructions': f'1. Review all learning materials for {week.theme}\n2. Complete the reflection questions\n3. Submit your response as a PDF or Word document',
                        'max_points': 100,
                        'due_date_offset': 7,
                        'submission_format': 'PDF/Word Document',
                        'is_required': True,
                    }
                )
                if assign_created:
                    self.stdout.write(f'  - Created assignment: {assignment.title}')
            else:
                self.stdout.write(self.style.WARNING(f'Week {week.week_number} already exists'))

        self.stdout.write(self.style.SUCCESS(f'Sample module setup complete! Module ID: {module.id}'))
        self.stdout.write(f'You can view it at: /courses/module/{module.id}/')
