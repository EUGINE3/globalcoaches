from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from programs.models import ProgramLevel, ProgramModule, Module
from courses.models import ModuleTopic, Lesson, LessonResource, Assignment
from students.models import StudentEnrollment
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Create comprehensive demo content for the learning management system'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='demo_student', help='Username for demo student')

    def handle(self, *args, **options):
        username = options['username']
        
        self.stdout.write(self.style.SUCCESS('Creating comprehensive demo content...'))
        
        # 1. Create Modules
        self.stdout.write('Creating modules...')
        modules = self.create_modules()
        
        # 2. Get Program Levels
        program_levels = list(ProgramLevel.objects.all())
        if not program_levels:
            self.stdout.write(self.style.ERROR('No program levels found. Please create program levels first.'))
            return
        
        # 3. Create Program Modules (modules at different levels)
        self.stdout.write('Creating program modules...')
        program_modules = self.create_program_modules(modules, program_levels)
        
        # 4. Create Topics for each Program Module
        self.stdout.write('Creating module topics...')
        topics = self.create_topics(program_modules)
        
        # 5. Create Lessons for each Topic
        self.stdout.write('Creating lessons...')
        lessons = self.create_lessons(topics)
        
        # 6. Create Resources for Lessons
        self.stdout.write('Creating lesson resources...')
        self.create_resources(lessons)
        
        # 7. Create Assignments
        self.stdout.write('Creating assignments...')
        self.create_assignments(topics)
        
        # 8. Create demo student and enrollment
        self.stdout.write('Creating demo student enrollment...')
        self.create_demo_student(username, program_levels[0])
        
        self.stdout.write(self.style.SUCCESS('✅ Comprehensive demo content created successfully!'))
        self.stdout.write(f'Demo student: {username}')
        self.stdout.write('Password: demo123')

    def create_modules(self):
        modules_data = [
            {
                'name': 'Module 1: Young Theologians and Gospel Advancing',
                'module_type': 'young_theologians',
                'description': 'Foundational theological education and gospel advancement strategies',
                'learning_objectives': 'Understand core theological principles, develop gospel presentation skills, learn evangelism strategies'
            },
            {
                'name': 'Module 2: Missional Leadership',
                'module_type': 'missional_leadership',
                'description': 'Leadership development for missional contexts',
                'learning_objectives': 'Develop leadership skills, understand missional principles, learn team management'
            },
            {
                'name': 'Module 3: Church Planting and Growth',
                'module_type': 'church_planting',
                'description': 'Practical church planting and growth strategies',
                'learning_objectives': 'Learn church planting methodologies, understand growth principles, develop ministry skills'
            }
        ]
        
        modules = []
        for data in modules_data:
            module, created = Module.objects.get_or_create(
                module_type=data['module_type'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'learning_objectives': data['learning_objectives'],
                    'is_active': True
                }
            )
            modules.append(module)
            if created:
                self.stdout.write(f'  ✓ Created module: {module.name}')
        
        return modules

    def create_program_modules(self, modules, program_levels):
        program_modules = []
        
        for program_level in program_levels:
            for i, module in enumerate(modules):
                # Determine depth level based on program level
                if program_level.level_type == 'certificate':
                    depth_level = 'foundational'
                elif program_level.level_type == 'diploma':
                    depth_level = 'intermediate'
                else:
                    depth_level = 'advanced'
                
                program_module, created = ProgramModule.objects.get_or_create(
                    program_level=program_level,
                    module=module,
                    defaults={
                        'depth_level': depth_level,
                        'credits': 15 + (i * 5),  # 15, 20, 25 credits
                        'description': f'This module is taught at {depth_level} level for {program_level.name}',
                        'is_active': True
                    }
                )
                program_modules.append(program_module)
                if created:
                    self.stdout.write(f'  ✓ Created program module: {program_module}')
        
        return program_modules

    def create_topics(self, program_modules):
        topics = []
        
        topics_data = {
            'young_theologians': [
                {
                    'title': 'Introduction to Theology',
                    'description': 'Basic theological concepts and foundations',
                    'learning_objectives': 'Understand what theology is, learn basic theological terms, explore the relationship between faith and reason',
                    'total_credits': 5,
                    'total_hours': 75,
                    'theory_hours': 45,
                    'practical_hours': 30
                },
                {
                    'title': 'Scripture and Interpretation',
                    'description': 'Biblical hermeneutics and interpretation methods',
                    'learning_objectives': 'Learn biblical interpretation principles, understand different hermeneutical approaches, practice exegetical methods',
                    'total_credits': 5,
                    'total_hours': 75,
                    'theory_hours': 40,
                    'practical_hours': 35
                },
                {
                    'title': 'Gospel Presentation Skills',
                    'description': 'Practical skills for sharing the gospel effectively',
                    'learning_objectives': 'Develop personal testimony, learn various gospel presentation methods, practice evangelistic conversations',
                    'total_credits': 5,
                    'total_hours': 75,
                    'theory_hours': 25,
                    'practical_hours': 50
                }
            ],
            'missional_leadership': [
                {
                    'title': 'Leadership Foundations',
                    'description': 'Core principles of Christian leadership',
                    'learning_objectives': 'Understand biblical leadership models, develop personal leadership philosophy, learn servant leadership principles',
                    'total_credits': 7,
                    'total_hours': 105,
                    'theory_hours': 60,
                    'practical_hours': 45
                },
                {
                    'title': 'Team Building and Management',
                    'description': 'Building and managing effective ministry teams',
                    'learning_objectives': 'Learn team dynamics, develop conflict resolution skills, understand team motivation strategies',
                    'total_credits': 6,
                    'total_hours': 90,
                    'theory_hours': 45,
                    'practical_hours': 45
                },
                {
                    'title': 'Missional Strategy Development',
                    'description': 'Creating and implementing missional strategies',
                    'learning_objectives': 'Understand missional principles, learn strategic planning, develop context-specific strategies',
                    'total_credits': 7,
                    'total_hours': 105,
                    'theory_hours': 50,
                    'practical_hours': 55
                }
            ],
            'church_planting': [
                {
                    'title': 'Church Planting Foundations',
                    'description': 'Biblical and practical foundations for church planting',
                    'learning_objectives': 'Understand biblical basis for church planting, learn different church planting models, assess personal calling',
                    'total_credits': 8,
                    'total_hours': 120,
                    'theory_hours': 70,
                    'practical_hours': 50
                },
                {
                    'title': 'Community Engagement',
                    'description': 'Engaging with local communities for church planting',
                    'learning_objectives': 'Learn community analysis methods, develop relationship building skills, understand cultural sensitivity',
                    'total_credits': 8,
                    'total_hours': 120,
                    'theory_hours': 50,
                    'practical_hours': 70
                },
                {
                    'title': 'Church Growth Principles',
                    'description': 'Strategies for healthy church growth',
                    'learning_objectives': 'Understand growth principles, learn discipleship strategies, develop multiplication mindset',
                    'total_credits': 9,
                    'total_hours': 135,
                    'theory_hours': 60,
                    'practical_hours': 75
                }
            ]
        }
        
        for program_module in program_modules:
            module_type = program_module.module.module_type
            if module_type in topics_data:
                for i, topic_data in enumerate(topics_data[module_type]):
                    topic, created = ModuleTopic.objects.get_or_create(
                        program_module=program_module,
                        topic_number=i + 1,
                        defaults={
                            'title': topic_data['title'],
                            'description': topic_data['description'],
                            'learning_objectives': topic_data['learning_objectives'],
                            'total_credits': topic_data['total_credits'],
                            'total_hours': topic_data['total_hours'],
                            'theory_hours': topic_data['theory_hours'],
                            'practical_hours': topic_data['practical_hours'],
                            'theory_content': f"Theory content for {topic_data['title']}",
                            'theory_resources': f"Required readings and resources for {topic_data['title']}",
                            'practical_activities': f"Practical exercises and activities for {topic_data['title']}",
                            'practical_deliverables': f"Assignments and deliverables for {topic_data['title']}",
                            'assessment_criteria': f"Assessment criteria for {topic_data['title']}",
                            'is_active': True,
                            'order': i + 1
                        }
                    )
                    topics.append(topic)
                    if created:
                        self.stdout.write(f'    ✓ Created topic: {topic.title}')
        
        return topics

    def create_lessons(self, topics):
        lessons = []

        lesson_templates = [
            {
                'title': 'Introduction and Overview',
                'lesson_type': 'theory',
                'duration_minutes': 90,
                'content': 'Introduction to the topic with key concepts and learning objectives.'
            },
            {
                'title': 'Core Concepts',
                'lesson_type': 'theory',
                'duration_minutes': 120,
                'content': 'Deep dive into the fundamental concepts and principles.'
            },
            {
                'title': 'Practical Application',
                'lesson_type': 'practical',
                'duration_minutes': 150,
                'content': 'Hands-on exercises and real-world application of concepts.'
            },
            {
                'title': 'Case Studies',
                'lesson_type': 'mixed',
                'duration_minutes': 120,
                'content': 'Analysis of real-world case studies and examples.'
            },
            {
                'title': 'Assessment and Review',
                'lesson_type': 'assessment',
                'duration_minutes': 90,
                'content': 'Review of key concepts and assessment activities.'
            }
        ]

        for topic in topics:
            for i, lesson_template in enumerate(lesson_templates):
                lesson, created = Lesson.objects.get_or_create(
                    topic=topic,
                    lesson_number=i + 1,
                    defaults={
                        'title': f"{lesson_template['title']} - {topic.title}",
                        'lesson_type': lesson_template['lesson_type'],
                        'duration_minutes': lesson_template['duration_minutes'],
                        'content': f"{lesson_template['content']} This lesson covers {topic.title.lower()}.",
                        'instructor_notes': f"Instructor notes for {lesson_template['title']} in {topic.title}",
                        'sequence_order': i + 1,
                        'is_active': True
                    }
                )
                lessons.append(lesson)
                if created:
                    self.stdout.write(f'      ✓ Created lesson: {lesson.title}')

        return lessons

    def create_resources(self, lessons):
        resource_types = ['video', 'reading', 'document', 'link']

        for lesson in lessons:
            for i, resource_type in enumerate(resource_types[:2]):  # Create 2 resources per lesson
                resource, created = LessonResource.objects.get_or_create(
                    lesson=lesson,
                    title=f"{resource_type.title()} Resource {i+1} - {lesson.title}",
                    defaults={
                        'resource_type': resource_type,
                        'description': f"A {resource_type} resource for {lesson.title}",
                        'url': f"https://example.com/{resource_type}-{lesson.id}-{i+1}",
                        'is_required': i == 0,  # First resource is required
                        'order': i + 1,
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f'        ✓ Created resource: {resource.title}')

    def create_assignments(self, topics):
        assignment_types = ['essay', 'project', 'presentation', 'quiz']

        for topic in topics:
            # Create 1-2 assignments per topic
            for i in range(2):
                assignment_type = assignment_types[i % len(assignment_types)]

                assignment, created = Assignment.objects.get_or_create(
                    topic=topic,
                    title=f"{assignment_type.title()} Assignment - {topic.title}",
                    defaults={
                        'assignment_type': assignment_type,
                        'description': f"A {assignment_type} assignment for {topic.title}. Students will demonstrate their understanding of the key concepts.",
                        'instructions': f"Complete this {assignment_type} assignment by following the guidelines provided in class.",
                        'max_points': 100,
                        'due_date': datetime.now() + timedelta(days=14 + (i * 7)),
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f'      ✓ Created assignment: {assignment.title}')

    def create_demo_student(self, username, program_level):
        # Create or get demo student
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': 'Demo',
                'last_name': 'Student',
                'email': f'{username}@example.com',
                'is_active': True
            }
        )

        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(f'  ✓ Created demo user: {username}')

        # Create enrollment
        enrollment, created = StudentEnrollment.objects.get_or_create(
            student=user,
            program_level=program_level,
            defaults={
                'status': 'active',
                'notes': 'Demo student enrollment for testing purposes'
            }
        )

        if created:
            self.stdout.write(f'  ✓ Created enrollment: {user.username} -> {program_level.name}')
