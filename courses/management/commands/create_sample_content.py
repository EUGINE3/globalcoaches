"""
Management command to create sample content for the enhanced learning system
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from programs.models import ProgramLevel
from courses.models import (
    Module, ProgramModule, ModuleTopic, Lesson, LessonResource, 
    Assignment, ModuleProgress
)
from courses.utils import ProgressiveAccessManager
from students.models import StudentEnrollment


class Command(BaseCommand):
    help = 'Create sample content for the enhanced learning system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='demo_student',
            help='Username for the demo student',
        )

    def handle(self, *args, **options):
        username = options['username']

        self.stdout.write(self.style.SUCCESS('Creating comprehensive demo content...'))

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

        # Create or get program level
        program_level, created = ProgramLevel.objects.get_or_create(
            level_type='certificate',
            defaults={
                'name': 'Young Theologians Certificate Program',
                'description': 'A comprehensive program for developing young theological leaders',
                'duration_months': 12,
                'focus_areas': 'Theology, Leadership, Ministry, Gospel Advancement',
                'is_active': True
            }
        )

        # Create enrollment
        enrollment, created = StudentEnrollment.objects.get_or_create(
            student=student,
            program_level=program_level,
            defaults={
                'status': 'active',
                'enrollment_date': timezone.now()
            }
        )

        # Create comprehensive module structure
        self.create_comprehensive_modules(program_level)

        self.stdout.write(self.style.SUCCESS('Demo content created successfully!'))
        self.stdout.write(f'🎓 Student: {username} (password: demo123)')
        self.stdout.write(f'📚 Program: {program_level.name}')
        self.stdout.write(f'🔗 Student Dashboard: http://127.0.0.1:8001/programs/dashboard/')
        self.stdout.write(f'🔗 Admin Interface: http://127.0.0.1:8001/admin/')
        self.stdout.write(f'🔗 Learning Path: http://127.0.0.1:8001/programs/my-learning-path/')

    def create_comprehensive_modules(self, program_level):
        """Create a comprehensive set of modules with realistic content"""

        modules_data = [
            {
                'name': 'Foundations of Faith',
                'description': 'Building strong theological foundations for young leaders',
                'sequence': 1,
                'credits': 12,
                'topics': [
                    {
                        'title': 'Introduction to Theology',
                        'description': 'Understanding the nature and scope of theological study',
                        'credits': 4,
                        'lessons': [
                            {'title': 'What is Theology?', 'type': 'theory', 'duration': 90},
                            {'title': 'Biblical Foundations', 'type': 'theory', 'duration': 120},
                            {'title': 'Historical Perspectives', 'type': 'theory', 'duration': 90},
                            {'title': 'Practical Application', 'type': 'practical', 'duration': 120},
                            {'title': 'Reflection and Assessment', 'type': 'assessment', 'duration': 60}
                        ]
                    },
                    {
                        'title': 'Scripture and Interpretation',
                        'description': 'Learning to read and interpret Scripture effectively',
                        'credits': 4,
                        'lessons': [
                            {'title': 'Biblical Authority', 'type': 'theory', 'duration': 90},
                            {'title': 'Hermeneutical Principles', 'type': 'theory', 'duration': 120},
                            {'title': 'Exegetical Methods', 'type': 'practical', 'duration': 150},
                            {'title': 'Contemporary Application', 'type': 'practical', 'duration': 120},
                            {'title': 'Scripture Study Project', 'type': 'assessment', 'duration': 90}
                        ]
                    },
                    {
                        'title': 'Christian Doctrine',
                        'description': 'Core doctrines of the Christian faith',
                        'credits': 4,
                        'lessons': [
                            {'title': 'The Nature of God', 'type': 'theory', 'duration': 90},
                            {'title': 'Christology', 'type': 'theory', 'duration': 90},
                            {'title': 'Pneumatology', 'type': 'theory', 'duration': 90},
                            {'title': 'Soteriology', 'type': 'theory', 'duration': 90},
                            {'title': 'Eschatology', 'type': 'theory', 'duration': 90},
                            {'title': 'Doctrinal Integration', 'type': 'assessment', 'duration': 120}
                        ]
                    }
                ]
            },
            {
                'name': 'Leadership Development',
                'description': 'Developing leadership skills for ministry and life',
                'sequence': 2,
                'credits': 10,
                'topics': [
                    {
                        'title': 'Biblical Leadership',
                        'description': 'Leadership principles from Scripture',
                        'credits': 3,
                        'lessons': [
                            {'title': 'Servant Leadership', 'type': 'theory', 'duration': 90},
                            {'title': 'Leadership in the Old Testament', 'type': 'theory', 'duration': 90},
                            {'title': 'Jesus as Leader', 'type': 'theory', 'duration': 90},
                            {'title': 'Apostolic Leadership', 'type': 'theory', 'duration': 90},
                            {'title': 'Leadership Case Studies', 'type': 'practical', 'duration': 120}
                        ]
                    },
                    {
                        'title': 'Personal Development',
                        'description': 'Growing in character and competence',
                        'credits': 3,
                        'lessons': [
                            {'title': 'Self-Awareness', 'type': 'practical', 'duration': 90},
                            {'title': 'Emotional Intelligence', 'type': 'practical', 'duration': 90},
                            {'title': 'Time Management', 'type': 'practical', 'duration': 90},
                            {'title': 'Goal Setting', 'type': 'practical', 'duration': 90},
                            {'title': 'Personal Development Plan', 'type': 'assessment', 'duration': 120}
                        ]
                    },
                    {
                        'title': 'Team Leadership',
                        'description': 'Leading and working with teams effectively',
                        'credits': 4,
                        'lessons': [
                            {'title': 'Team Dynamics', 'type': 'theory', 'duration': 90},
                            {'title': 'Communication Skills', 'type': 'practical', 'duration': 120},
                            {'title': 'Conflict Resolution', 'type': 'practical', 'duration': 120},
                            {'title': 'Delegation and Empowerment', 'type': 'practical', 'duration': 90},
                            {'title': 'Team Leadership Project', 'type': 'assessment', 'duration': 150}
                        ]
                    }
                ]
            },
            {
                'name': 'Gospel Advancement',
                'description': 'Strategies and methods for advancing the gospel',
                'sequence': 3,
                'credits': 8,
                'topics': [
                    {
                        'title': 'Evangelism and Outreach',
                        'description': 'Sharing the gospel effectively in various contexts',
                        'credits': 4,
                        'lessons': [
                            {'title': 'The Gospel Message', 'type': 'theory', 'duration': 90},
                            {'title': 'Personal Evangelism', 'type': 'practical', 'duration': 120},
                            {'title': 'Cultural Sensitivity', 'type': 'theory', 'duration': 90},
                            {'title': 'Digital Evangelism', 'type': 'practical', 'duration': 90},
                            {'title': 'Evangelism Practice', 'type': 'assessment', 'duration': 120}
                        ]
                    },
                    {
                        'title': 'Discipleship and Mentoring',
                        'description': 'Making disciples and developing others',
                        'credits': 4,
                        'lessons': [
                            {'title': 'The Great Commission', 'type': 'theory', 'duration': 90},
                            {'title': 'Discipleship Models', 'type': 'theory', 'duration': 90},
                            {'title': 'Mentoring Relationships', 'type': 'practical', 'duration': 120},
                            {'title': 'Spiritual Formation', 'type': 'practical', 'duration': 120},
                            {'title': 'Discipleship Plan', 'type': 'assessment', 'duration': 90}
                        ]
                    }
                ]
            }
        ]

        for module_data in modules_data:
            self.create_module_with_content(program_level, module_data)

    def create_module_with_content(self, program_level, module_data):
        """Create a module with all its topics, lessons, and resources"""

        # Create or get the base module
        module, created = Module.objects.get_or_create(
            name=module_data['name'],
            defaults={
                'description': module_data['description'],
                'is_active': True
            }
        )

        # Create program module
        program_module, created = ProgramModule.objects.get_or_create(
            program_level=program_level,
            module=module,
            defaults={
                'sequence_order': module_data['sequence'],
                'total_credits': module_data['credits'],
                'minimum_completion_percentage': 80,
                'is_active': True
            }
        )

        if created:
            self.stdout.write(f'Created module: {module.name}')

        # Create topics for this module
        for topic_index, topic_data in enumerate(module_data['topics'], 1):
            self.create_topic_with_lessons(program_module, topic_index, topic_data)

    def create_topic_with_lessons(self, program_module, topic_number, topic_data):
        """Create a topic with all its lessons and resources"""

        topic, created = ModuleTopic.objects.get_or_create(
            program_module=program_module,
            topic_number=topic_number,
            defaults={
                'title': topic_data['title'],
                'description': topic_data['description'],
                'learning_objectives': f'Master the concepts and skills in {topic_data["title"]}',
                'total_credits': topic_data['credits'],
                'total_hours': topic_data['credits'] * 15,  # 15 hours per credit
                'theory_hours': topic_data['credits'] * 8,
                'practical_hours': topic_data['credits'] * 7,
                'theory_content': f'Theoretical foundations of {topic_data["title"]}',
                'practical_activities': f'Hands-on activities for {topic_data["title"]}',
                'practical_deliverables': f'Projects and assignments for {topic_data["title"]}',
                'assessment_criteria': 'Understanding, application, and reflection quality',
                'order': topic_number,
                'is_active': True
            }
        )

        if created:
            self.stdout.write(f'  Created topic: {topic.title}')

        # Create lessons for this topic
        for lesson_index, lesson_data in enumerate(topic_data['lessons'], 1):
            self.create_lesson_with_resources(topic, lesson_index, lesson_data)

    def create_lesson_with_resources(self, topic, lesson_number, lesson_data):
        """Create a lesson with resources and assignments"""

        lesson, created = Lesson.objects.get_or_create(
            topic=topic,
            lesson_number=lesson_number,
            defaults={
                'title': lesson_data['title'],
                'description': f'Comprehensive study of {lesson_data["title"]}',
                'learning_objectives': f'Understand and apply concepts from {lesson_data["title"]}',
                'lesson_type': lesson_data['type'],
                'duration_minutes': lesson_data['duration'],
                'content': self.generate_lesson_content(lesson_data['title'], lesson_data['type']),
                'sequence_order': lesson_number,
                'is_active': True
            }
        )

        if created:
            self.stdout.write(f'    Created lesson: {lesson.title}')
            self.create_lesson_resources(lesson)

            # Create assignment for assessment lessons
            if lesson_data['type'] == 'assessment':
                self.create_lesson_assignment(lesson)

    def generate_lesson_content(self, title, lesson_type):
        """Generate appropriate content based on lesson type"""

        content_templates = {
            'theory': f"""
# {title}

## Learning Objectives
By the end of this lesson, you will be able to:
- Understand the key concepts of {title}
- Explain the biblical foundations
- Connect theory to practical application

## Key Concepts
This lesson covers the fundamental principles and theoretical framework of {title}.

## Biblical Foundation
We will explore relevant Scripture passages and their application to {title}.

## Discussion Questions
1. How does this concept apply to your current context?
2. What challenges might you face in implementing these ideas?
3. How does this connect to other areas of study?
            """,

            'practical': f"""
# {title} - Practical Application

## Overview
This hands-on session focuses on applying the concepts of {title} in real-world scenarios.

## Activities
- Interactive exercises
- Group discussions
- Case study analysis
- Skill practice sessions

## Learning Outcomes
You will develop practical skills and confidence in applying {title} concepts.

## Reflection
Consider how these practical skills will enhance your ministry and leadership effectiveness.
            """,

            'assessment': f"""
# {title} - Assessment and Evaluation

## Purpose
This assessment evaluates your understanding and application of the concepts covered in this topic.

## Assessment Components
- Written reflection
- Practical demonstration
- Peer evaluation
- Self-assessment

## Submission Guidelines
Please follow the assignment instructions carefully and submit by the due date.

## Grading Criteria
Your work will be evaluated based on understanding, application, and reflection quality.
            """
        }

        return content_templates.get(lesson_type, f"Content for {title}")

    def create_lesson_resources(self, lesson):
        """Create diverse resources for a lesson"""

        resources_data = [
            {
                'title': f'{lesson.title} - Study Guide',
                'resource_type': 'reading',
                'description': 'Comprehensive study guide covering key concepts',
                'content': f'Study guide content for {lesson.title}...',
                'is_required': True,
                'duration': 30,
                'order': 1
            },
            {
                'title': f'{lesson.title} - Video Lecture',
                'resource_type': 'video',
                'description': 'Video presentation of core concepts',
                'url': 'https://example.com/video-lecture',
                'is_required': True,
                'duration': lesson.duration_minutes,
                'order': 2
            },
            {
                'title': f'{lesson.title} - Additional Reading',
                'resource_type': 'document',
                'description': 'Supplementary reading material',
                'content': f'Additional reading material for {lesson.title}...',
                'is_required': False,
                'duration': 20,
                'order': 3
            }
        ]

        # Add practical resources for practical lessons
        if lesson.lesson_type == 'practical':
            resources_data.append({
                'title': f'{lesson.title} - Activity Worksheet',
                'resource_type': 'worksheet',
                'description': 'Interactive worksheet for practical exercises',
                'content': f'Worksheet content for {lesson.title}...',
                'is_required': True,
                'duration': 45,
                'order': 4
            })

        for resource_data in resources_data:
            resource, created = LessonResource.objects.get_or_create(
                lesson=lesson,
                title=resource_data['title'],
                defaults={
                    'resource_type': resource_data['resource_type'],
                    'description': resource_data['description'],
                    'content': resource_data.get('content', ''),
                    'url': resource_data.get('url', ''),
                    'is_required': resource_data['is_required'],
                    'estimated_duration_minutes': resource_data['duration'],
                    'order': resource_data['order'],
                    'is_active': True
                }
            )

            if created:
                self.stdout.write(f'      Created resource: {resource.title}')

    def create_lesson_assignment(self, lesson):
        """Create an assignment for assessment lessons"""

        assignment_types = {
            'Reflection and Assessment': 'essay',
            'Scripture Study Project': 'project',
            'Leadership Case Studies': 'case_study',
            'Personal Development Plan': 'project',
            'Team Leadership Project': 'project',
            'Evangelism Practice': 'practical',
            'Discipleship Plan': 'project'
        }

        assignment_type = assignment_types.get(lesson.title, 'essay')

        assignment, created = Assignment.objects.get_or_create(
            lesson=lesson,
            title=f'{lesson.topic.title} - {lesson.title}',
            defaults={
                'description': f'Assessment assignment for {lesson.topic.title}',
                'instructions': self.generate_assignment_instructions(lesson.title, assignment_type),
                'assignment_type': assignment_type,
                'max_points': 100,
                'due_date': timezone.now() + timedelta(days=14),  # 2 weeks from now
                'late_submission_penalty': 10,
                'allow_late_submission': True,
                'is_active': True
            }
        )

        if created:
            self.stdout.write(f'      Created assignment: {assignment.title}')

    def generate_assignment_instructions(self, lesson_title, assignment_type):
        """Generate appropriate assignment instructions"""

        instructions = {
            'essay': f"""
Write a comprehensive essay (1500-2000 words) on {lesson_title}.

Requirements:
- Clear thesis statement
- Biblical foundation with Scripture references
- Personal reflection and application
- Proper citations and references
- Professional formatting

Submission: Upload as PDF document
            """,

            'project': f"""
Complete a practical project demonstrating your understanding of {lesson_title}.

Requirements:
- Project proposal (500 words)
- Implementation plan
- Final project deliverable
- Reflection report (1000 words)
- Presentation (10 minutes)

Submission: Upload all components as separate files
            """,

            'case_study': f"""
Analyze the provided case study related to {lesson_title}.

Requirements:
- Situation analysis (500 words)
- Biblical principles application
- Recommended solutions
- Implementation strategy
- Expected outcomes

Submission: Upload analysis as PDF document
            """,

            'practical': f"""
Complete the practical exercise for {lesson_title}.

Requirements:
- Demonstrate practical skills
- Document your experience
- Reflect on learning outcomes
- Provide evidence of completion
- Submit reflection report (750 words)

Submission: Upload documentation and reflection
            """
        }

        return instructions.get(assignment_type, f"Complete the assignment for {lesson_title}")

    def create_sample_topics(self, program_module):
        """Create sample topics, lessons, resources, and assignments"""
        
        # Topic 1: Introduction
        topic1, created = ModuleTopic.objects.get_or_create(
            program_module=program_module,
            topic_number=1,
            defaults={
                'title': 'Introduction to Young Theologians',
                'description': 'An introduction to the foundational concepts of young theologians and gospel advancing.',
                'learning_objectives': 'Understand the role of young theologians in modern society',
                'total_credits': 3,
                'total_hours': 45,
                'theory_hours': 25,
                'practical_hours': 20,
                'theory_content': 'Theoretical foundations of theological studies',
                'practical_activities': 'Group discussions and reflection exercises',
                'practical_deliverables': 'Reflection paper on personal calling',
                'assessment_criteria': 'Understanding of concepts and personal reflection quality',
                'order': 1
            }
        )
        
        if created:
            self.stdout.write(f'Created topic: {topic1.title}')
            
            # Create lessons for topic 1
            self.create_sample_lessons(topic1)

        # Topic 2: Gospel Advancing Strategies
        topic2, created = ModuleTopic.objects.get_or_create(
            program_module=program_module,
            topic_number=2,
            defaults={
                'title': 'Gospel Advancing Strategies',
                'description': 'Practical strategies for advancing the gospel in contemporary contexts.',
                'learning_objectives': 'Develop practical skills for gospel advancement',
                'total_credits': 4,
                'total_hours': 60,
                'theory_hours': 30,
                'practical_hours': 30,
                'theory_content': 'Biblical foundations of evangelism and discipleship',
                'practical_activities': 'Role-playing and community engagement exercises',
                'practical_deliverables': 'Community outreach plan',
                'assessment_criteria': 'Practical application and strategic thinking',
                'order': 2
            }
        )
        
        if created:
            self.stdout.write(f'Created topic: {topic2.title}')
            self.create_sample_lessons(topic2)

    def create_sample_lessons(self, topic):
        """Create sample lessons for a topic"""
        
        lessons_data = [
            {
                'lesson_number': 1,
                'title': f'Introduction to {topic.title}',
                'description': f'Overview and introduction to {topic.title}',
                'lesson_type': 'theory',
                'duration_minutes': 90,
                'content': f'This lesson introduces the key concepts of {topic.title}.',
            },
            {
                'lesson_number': 2,
                'title': f'Practical Applications',
                'description': f'Hands-on practice and application of {topic.title} concepts',
                'lesson_type': 'practical',
                'duration_minutes': 120,
                'content': f'Interactive session focusing on practical applications.',
            },
            {
                'lesson_number': 3,
                'title': f'Assessment and Reflection',
                'description': f'Assessment and reflection on {topic.title} learning',
                'lesson_type': 'assessment',
                'duration_minutes': 60,
                'content': f'Assessment session with reflection activities.',
            }
        ]
        
        for lesson_data in lessons_data:
            lesson, created = Lesson.objects.get_or_create(
                topic=topic,
                lesson_number=lesson_data['lesson_number'],
                defaults={
                    'title': lesson_data['title'],
                    'description': lesson_data['description'],
                    'learning_objectives': f'Complete {lesson_data["title"]} successfully',
                    'lesson_type': lesson_data['lesson_type'],
                    'duration_minutes': lesson_data['duration_minutes'],
                    'content': lesson_data['content'],
                    'sequence_order': lesson_data['lesson_number'],
                }
            )
            
            if created:
                self.stdout.write(f'  Created lesson: {lesson.title}')
                self.create_sample_resources(lesson)
                self.create_sample_assignment(lesson)

    def create_sample_resources(self, lesson):
        """Create sample resources for a lesson"""
        
        resources_data = [
            {
                'title': f'{lesson.title} - Reading Material',
                'resource_type': 'reading',
                'description': 'Essential reading for this lesson',
                'content': f'Reading material covering the key concepts of {lesson.title}.',
                'is_required': True,
                'estimated_duration_minutes': 30,
                'order': 1
            },
            {
                'title': f'{lesson.title} - Video Lecture',
                'resource_type': 'video',
                'description': 'Video lecture explaining the concepts',
                'content': f'Video content for {lesson.title}.',
                'url': 'https://example.com/video',
                'is_required': True,
                'estimated_duration_minutes': 45,
                'order': 2
            },
            {
                'title': f'{lesson.title} - Supplementary Document',
                'resource_type': 'document',
                'description': 'Additional reference material',
                'content': f'Supplementary document for {lesson.title}.',
                'is_required': False,
                'estimated_duration_minutes': 20,
                'order': 3
            }
        ]
        
        for resource_data in resources_data:
            resource, created = LessonResource.objects.get_or_create(
                lesson=lesson,
                title=resource_data['title'],
                defaults=resource_data
            )
            
            if created:
                self.stdout.write(f'    Created resource: {resource.title}')

    def create_sample_assignment(self, lesson):
        """Create a sample assignment for a lesson"""
        
        if lesson.lesson_type == 'assessment':
            assignment, created = Assignment.objects.get_or_create(
                lesson=lesson,
                title=f'{lesson.topic.title} - Assessment',
                defaults={
                    'description': f'Assessment assignment for {lesson.topic.title}',
                    'instructions': f'Complete the assessment for {lesson.topic.title}. Submit your work by the due date.',
                    'assignment_type': 'essay',
                    'max_points': 100,
                    'due_date': timezone.now() + timedelta(days=7),
                    'late_submission_penalty': 10,
                    'allow_late_submission': True,
                }
            )
            
            if created:
                self.stdout.write(f'    Created assignment: {assignment.title}')
