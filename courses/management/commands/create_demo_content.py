"""
Simple demo content creation command
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from courses.models import (
    ProgramLevel, Module, ProgramModule, ModuleTopic, Lesson, LessonResource, Assignment
)
from students.models import StudentEnrollment


class Command(BaseCommand):
    help = 'Create simple demo content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='demo_student',
            help='Username for the demo student',
        )

    def handle(self, *args, **options):
        username = options['username']
        
        self.stdout.write(self.style.SUCCESS('Creating demo content...'))

        # Get or create demo student
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

        # Create program level using courses model
        program_level, created = ProgramLevel.objects.get_or_create(
            level_type='certificate',
            defaults={
                'name': 'Young Theologians Certificate',
                'description': 'Foundation level program for young theological leaders',
                'duration_months': 12,
                'focus_areas': 'Theology, Leadership, Ministry',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'Created program level: {program_level.name}')

        # Create enrollment (without signals)
        enrollment, created = StudentEnrollment.objects.get_or_create(
            student=student,
            program_level_id=program_level.id,  # Use ID to avoid model conflicts
            defaults={
                'status': 'active',
                'enrollment_date': timezone.now()
            }
        )

        # Create modules
        self.create_demo_modules(program_level)
        
        self.stdout.write(self.style.SUCCESS('Demo content created successfully!'))
        self.stdout.write(f'🎓 Student: {username} (password: demo123)')
        self.stdout.write(f'📚 Program: {program_level.name}')
        self.stdout.write(f'🔗 Admin: http://127.0.0.1:8001/admin/')

    def create_demo_modules(self, program_level):
        """Create demo modules with topics and lessons"""
        
        # Module 1: Young Theologians
        module1, created = Module.objects.get_or_create(
            module_type='young_theologians',
            defaults={
                'name': 'Young Theologians and Gospel Advancing',
                'description': 'Building strong theological foundations for young leaders',
                'learning_objectives': 'Develop theological understanding and gospel advancement skills',
                'is_active': True
            }
        )
        
        program_module1, created = ProgramModule.objects.get_or_create(
            program_level=program_level,
            module=module1,
            defaults={
                'depth_level': 1,
                'learning_outcomes': 'Understand theological foundations',
                'assessment_criteria': 'Comprehension and application',
                'sequence_order': 1,
                'total_credits': 12,
                'minimum_completion_percentage': 80,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'Created module: {module1.name}')
            
        # Create topics for Module 1
        self.create_topic_with_lessons(
            program_module1, 1, 
            'Introduction to Theology',
            'Understanding the nature and scope of theological study'
        )
        
        self.create_topic_with_lessons(
            program_module1, 2,
            'Scripture and Interpretation', 
            'Learning to read and interpret Scripture effectively'
        )

        # Module 2: Missional Leadership
        module2, created = Module.objects.get_or_create(
            module_type='missional_leadership',
            defaults={
                'name': 'Missional Leadership',
                'description': 'Developing leadership skills for missional ministry',
                'learning_objectives': 'Develop leadership competencies for missional contexts',
                'is_active': True
            }
        )
        
        program_module2, created = ProgramModule.objects.get_or_create(
            program_level=program_level,
            module=module2,
            defaults={
                'depth_level': 2,
                'learning_outcomes': 'Develop leadership skills',
                'assessment_criteria': 'Leadership competency demonstration',
                'sequence_order': 2,
                'total_credits': 10,
                'minimum_completion_percentage': 80,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'Created module: {module2.name}')
            
        # Set prerequisites
        program_module2.prerequisites.add(program_module1)
        
        # Create topics for Module 2
        self.create_topic_with_lessons(
            program_module2, 1,
            'Biblical Leadership',
            'Leadership principles from Scripture'
        )

    def create_topic_with_lessons(self, program_module, topic_number, title, description):
        """Create a topic with sample lessons"""
        
        topic, created = ModuleTopic.objects.get_or_create(
            program_module=program_module,
            topic_number=topic_number,
            defaults={
                'title': title,
                'description': description,
                'learning_objectives': f'Master the concepts of {title}',
                'total_credits': 4,
                'total_hours': 60,
                'theory_hours': 30,
                'practical_hours': 30,
                'theory_content': f'Theoretical foundations of {title}',
                'practical_activities': f'Practical exercises for {title}',
                'practical_deliverables': f'Projects for {title}',
                'assessment_criteria': 'Understanding and application',
                'order': topic_number,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'  Created topic: {topic.title}')
            
            # Create sample lessons
            lessons_data = [
                {'title': f'Introduction to {title}', 'type': 'theory', 'duration': 90},
                {'title': f'Key Concepts', 'type': 'theory', 'duration': 90},
                {'title': f'Practical Application', 'type': 'practical', 'duration': 120},
                {'title': f'Assessment', 'type': 'assessment', 'duration': 60}
            ]
            
            for i, lesson_data in enumerate(lessons_data, 1):
                lesson, created = Lesson.objects.get_or_create(
                    topic=topic,
                    lesson_number=i,
                    defaults={
                        'title': lesson_data['title'],
                        'description': f'Lesson on {lesson_data["title"]}',
                        'learning_objectives': f'Understand {lesson_data["title"]}',
                        'lesson_type': lesson_data['type'],
                        'duration_minutes': lesson_data['duration'],
                        'content': f'Content for {lesson_data["title"]}...',
                        'sequence_order': i,
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f'    Created lesson: {lesson.title}')
                    
                    # Create sample resources
                    self.create_sample_resources(lesson)
                    
                    # Create assignment for assessment lessons
                    if lesson_data['type'] == 'assessment':
                        self.create_sample_assignment(lesson)

    def create_sample_resources(self, lesson):
        """Create sample resources for a lesson"""
        
        resources = [
            {
                'title': f'{lesson.title} - Study Guide',
                'type': 'reading',
                'description': 'Study guide for this lesson',
                'required': True,
                'duration': 30
            },
            {
                'title': f'{lesson.title} - Video',
                'type': 'video',
                'description': 'Video content for this lesson',
                'required': True,
                'duration': lesson.duration_minutes
            }
        ]
        
        for i, resource_data in enumerate(resources, 1):
            resource, created = LessonResource.objects.get_or_create(
                lesson=lesson,
                title=resource_data['title'],
                defaults={
                    'resource_type': resource_data['type'],
                    'description': resource_data['description'],
                    'content': f'Content for {resource_data["title"]}',
                    'is_required': resource_data['required'],
                    'estimated_duration_minutes': resource_data['duration'],
                    'order': i,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'      Created resource: {resource.title}')

    def create_sample_assignment(self, lesson):
        """Create a sample assignment"""
        
        assignment, created = Assignment.objects.get_or_create(
            lesson=lesson,
            title=f'{lesson.topic.title} - Assessment',
            defaults={
                'description': f'Assessment for {lesson.topic.title}',
                'instructions': f'Complete the assessment for {lesson.topic.title}',
                'assignment_type': 'essay',
                'max_points': 100,
                'due_date': timezone.now() + timedelta(days=14),
                'late_submission_penalty': 10,
                'allow_late_submission': True,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'      Created assignment: {assignment.title}')
