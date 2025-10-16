"""
Progress calculation utilities for the Global Coaches Academy
"""
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    ModuleProgress, LessonProgress, ResourceProgress, 
    AssignmentSubmission, Lesson, ModuleTopic, ProgramModule
)


class ProgressCalculator:
    """Centralized progress calculation utilities"""
    
    @staticmethod
    def calculate_lesson_progress(student, lesson):
        """
        Calculate completion percentage for a lesson based on:
        - Required resources completed
        - Assignments completed with passing grade
        """
        total_items = 0
        completed_items = 0

        # Count required resources
        required_resources = lesson.resources.filter(is_required=True, is_active=True)
        total_items += required_resources.count()

        # Count completed resources
        completed_resources = ResourceProgress.objects.filter(
            student=student,
            resource__in=required_resources,
            is_completed=True
        ).count()
        completed_items += completed_resources

        # Count assignments
        assignments = lesson.assignments.filter(is_active=True)
        total_items += assignments.count()

        # Count completed assignments (graded submissions with passing grade)
        completed_assignments = AssignmentSubmission.objects.filter(
            student=student,
            assignment__in=assignments,
            is_graded=True,
            grade_percentage__gte=70  # Passing grade threshold
        ).count()
        completed_items += completed_assignments

        # Calculate percentage
        if total_items > 0:
            completion_percentage = (completed_items / total_items) * 100
        else:
            completion_percentage = 100  # No items means 100% complete

        return completion_percentage

    @staticmethod
    def calculate_topic_progress(student, topic):
        """
        Calculate completion percentage for a topic based on:
        - Lessons completed
        - Topic-level assignments completed
        """
        # Get all lessons in the topic
        lessons = topic.lessons.filter(is_active=True)
        total_lessons = lessons.count()
        
        if total_lessons == 0:
            return 0

        # Count completed lessons
        completed_lessons = 0
        for lesson in lessons:
            lesson_progress = LessonProgress.objects.filter(
                student=student,
                lesson=lesson
            ).first()
            
            if lesson_progress and lesson_progress.is_completed:
                completed_lessons += 1

        # Calculate base percentage from lessons
        base_percentage = (completed_lessons / total_lessons) * 100

        # Check for topic-level assignments
        topic_assignments = topic.assignments.filter(is_active=True)
        if topic_assignments.exists():
            # If there are topic assignments, require them for 100% completion
            completed_assignments = AssignmentSubmission.objects.filter(
                student=student,
                assignment__in=topic_assignments,
                is_graded=True,
                grade_percentage__gte=70
            ).count()
            
            total_assignments = topic_assignments.count()
            if total_assignments > 0 and completed_assignments < total_assignments:
                # Cap at 99% if assignments are not completed
                return min(base_percentage, 99)

        return base_percentage

    @staticmethod
    def calculate_module_progress(student, program_module):
        """
        Calculate completion percentage for a module based on:
        - Topics completed
        - Module-level assignments completed
        """
        # Get all topics in the module
        topics = program_module.topics.filter(is_active=True)
        total_topics = topics.count()
        
        if total_topics == 0:
            return 0

        # Calculate progress for each topic
        total_progress = 0
        for topic in topics:
            topic_progress = ProgressCalculator.calculate_topic_progress(student, topic)
            total_progress += topic_progress

        # Average progress across all topics
        average_progress = total_progress / total_topics if total_topics > 0 else 0

        return average_progress

    @staticmethod
    def update_lesson_progress(student, lesson):
        """
        Update or create lesson progress record with calculated completion percentage
        """
        completion_percentage = ProgressCalculator.calculate_lesson_progress(student, lesson)
        
        lesson_progress, created = LessonProgress.objects.get_or_create(
            student=student,
            lesson=lesson,
            defaults={
                'started_at': timezone.now(),
                'is_started': True
            }
        )
        
        lesson_progress.completion_percentage = completion_percentage
        lesson_progress.is_completed = completion_percentage >= 100
        
        if lesson_progress.is_completed and not lesson_progress.completed_at:
            lesson_progress.completed_at = timezone.now()
        
        lesson_progress.save()
        return lesson_progress

    @staticmethod
    def update_module_progress(student, program_module):
        """
        Update or create module progress record with calculated completion percentage
        """
        completion_percentage = ProgressCalculator.calculate_module_progress(student, program_module)
        
        module_progress, created = ModuleProgress.objects.get_or_create(
            student=student,
            program_module=program_module,
            defaults={
                'is_unlocked': True,
                'unlocked_at': timezone.now()
            }
        )
        
        module_progress.progress_percentage = completion_percentage
        module_progress.completion_percentage = completion_percentage
        module_progress.is_completed = completion_percentage >= program_module.minimum_completion_percentage
        
        if module_progress.is_completed and not module_progress.completed_at:
            module_progress.completed_at = timezone.now()
        
        module_progress.save()
        return module_progress

    @staticmethod
    def recalculate_all_progress(student, program_level=None):
        """
        Recalculate all progress for a student, optionally limited to a program level
        """
        from programs.models import ProgramModule
        
        if program_level:
            program_modules = ProgramModule.objects.filter(
                program_level=program_level,
                is_active=True
            )
        else:
            program_modules = ProgramModule.objects.filter(is_active=True)
        
        updated_modules = 0
        updated_lessons = 0
        
        for program_module in program_modules:
            # Update module progress
            ProgressCalculator.update_module_progress(student, program_module)
            updated_modules += 1
            
            # Update lesson progress for all lessons in this module
            lessons = Lesson.objects.filter(
                topic__program_module=program_module,
                is_active=True
            )
            
            for lesson in lessons:
                ProgressCalculator.update_lesson_progress(student, lesson)
                updated_lessons += 1
        
        return {
            'modules_updated': updated_modules,
            'lessons_updated': updated_lessons
        }


class ProgressDisplayHelper:
    """Helper utilities for displaying progress in templates"""
    
    @staticmethod
    def get_progress_display_class(percentage):
        """Get CSS class based on progress percentage"""
        if percentage >= 100:
            return 'progress-complete'
        elif percentage >= 75:
            return 'progress-high'
        elif percentage >= 50:
            return 'progress-medium'
        elif percentage >= 25:
            return 'progress-low'
        else:
            return 'progress-minimal'
    
    @staticmethod
    def get_progress_color(percentage):
        """Get color based on progress percentage"""
        if percentage >= 100:
            return '#28a745'  # Green
        elif percentage >= 75:
            return '#20c997'  # Teal
        elif percentage >= 50:
            return '#17a2b8'  # Info blue
        elif percentage >= 25:
            return '#ffc107'  # Warning yellow
        else:
            return '#dc3545'  # Danger red
    
    @staticmethod
    def format_progress_percentage(percentage, decimal_places=0):
        """Format percentage for display"""
        return f"{percentage:.{decimal_places}f}%"
