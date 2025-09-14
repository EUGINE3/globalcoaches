"""
Utility functions for progressive learning and prerequisite validation
"""
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from .models import (
    Module, ModuleProgress, WeekProgress, ResourceView, WeeklyResource,
    Lesson, LessonProgress, Assignment, AssignmentSubmission
)
from students.models import StudentEnrollment
from programs.models import ProgramLevel,ProgramModule


class ProgressiveAccessManager:
    """Manages progressive access to modules and weeks"""

    @staticmethod
    def initialize_student_progress(student):
        """Initialize progress tracking for a new student enrollment"""
        # Get the student's enrollment
        enrollment = StudentEnrollment.objects.filter(
            student=student,
            status='active'
        ).first()

        if not enrollment:
            return

        # Get first module in the program (sequence_order = 1)
        first_program_module = ProgramModule.objects.filter(
            program_level=enrollment.program_level,
            is_active=True,
            sequence_order=1
        ).first()

        if first_program_module:
            # Create and unlock first module
            module_progress, created = ModuleProgress.objects.get_or_create(
                student=student,
                program_module=first_program_module
            )
            module_progress.is_unlocked = True
            module_progress.unlocked_at = timezone.now()
            module_progress.is_completed = False
            module_progress.save()

            return f"Unlocked first module: {first_program_module.module.name}"

        return "No modules found to unlock"
    
    @staticmethod
    def can_access_program_module(student, program_module):
        """Check if student can access a specific program module"""
        # Check if student is enrolled in this program level
        try:
            enrollment = StudentEnrollment.objects.filter(
                student=student,
                # program_level=program_module.program_level,
                status='active'
            ).first()
            if not enrollment:
                return False
        except StudentEnrollment.DoesNotExist:
            return False

        # Get existing progress
        progress = ModuleProgress.objects.filter(student=student, program_module=program_module).first()

        if progress:
            return progress.is_unlocked

        # No progress record exists - check if this module can be unlocked
        # Check if this is the first module (sequence_order = 1)
        if program_module.sequence_order == 1:
            # Auto-create and unlock first module
            progress = ModuleProgress.objects.create(
                student=student,
                program_module=program_module,
                is_unlocked=True,
                unlocked_at=timezone.now()
            )
            return True

        # Check if all prerequisites are completed
        return ProgressiveAccessManager._check_prerequisites(student, program_module)

    @staticmethod
    def _check_prerequisites(student, program_module):
        """Check if all prerequisites for a module are completed"""
        # Check sequence-based prerequisites
        previous_modules = ProgramModule.objects.filter(
            program_level=program_module.program_level,
            sequence_order__lt=program_module.sequence_order,
            is_active=True
        )

        for prev_module in previous_modules:
            prev_progress = ModuleProgress.objects.filter(
                student=student,
                program_module=prev_module
            ).first()

            if not prev_progress:
                return False
            if not prev_progress.is_completed:
                return False
            if prev_progress.progress_percentage < prev_module.minimum_completion_percentage:
                return False

        # Check explicit prerequisites (if the model has a prerequisites field)
        if hasattr(program_module, 'prerequisites'):
            for prereq in program_module.prerequisites.all():
                prereq_progress = ModuleProgress.objects.filter(
                    student=student,
                    program_module=prereq
                ).first()

                if not prereq_progress:
                    return False
                if not prereq_progress.is_completed:
                    return False
                if prereq_progress.progress_percentage < prereq.minimum_completion_percentage:
                    return False

        return True
    
    @staticmethod
    def unlock_next_modules(student, completed_program_module):
        """Unlock the next modules when current one is completed"""
        unlocked_modules = []

        # Get modules that have this module as a prerequisite
        dependent_modules = ProgramModule.objects.filter(
            prerequisites=completed_program_module,
            is_active=True
        )

        for module in dependent_modules:
            if ProgressiveAccessManager._check_prerequisites(student, module):
                progress, created = ModuleProgress.objects.get_or_create(
                    student=student,
                    program_module=module
                )
                if not progress.is_unlocked:
                    progress.is_unlocked = True
                    progress.unlocked_at = timezone.now()
                    progress.save()
                    unlocked_modules.append(module)

        # Also check sequence-based unlocking
        next_sequence_module = ProgramModule.objects.filter(
            program_level=completed_program_module.program_level,
            sequence_order=completed_program_module.sequence_order + 1,
            is_active=True
        ).first()

        if next_sequence_module and ProgressiveAccessManager._check_prerequisites(student, next_sequence_module):
            progress, created = ModuleProgress.objects.get_or_create(
                student=student,
                program_module=next_sequence_module
            )
            if not progress.is_unlocked:
                progress.is_unlocked = True
                progress.unlocked_at = timezone.now()
                progress.save()
                unlocked_modules.append(next_sequence_module)

        return unlocked_modules

    @staticmethod
    def get_student_module_progression(student, program_level):
        """Get detailed progression status for all modules in a program level"""
        modules = ProgramModule.objects.filter(
            program_level=program_level,
            is_active=True
        ).order_by('sequence_order')
        

        progression = []
        for module in modules:
            progress = ModuleProgress.objects.filter(student=student, program_module=module).first()
            can_access = ProgressiveAccessManager.can_access_program_module(student, module)

            if progress:
                if progress.is_completed:
                    status = 'completed'
                elif progress.is_unlocked:
                    status = 'unlocked'
                else:
                    status = 'locked'
            else:
                # Use the proper access control method
                status = 'unlocked' if can_access else 'locked'

            prerequisite_status = module.get_prerequisite_status(student)

            progression.append({
                'module': module,
                'progress': progress,
                'status': status,
                'can_access': can_access,
                'prerequisites': prerequisite_status,
                'completion_percentage': progress.progress_percentage if progress else 0
            })

        return progression

    @staticmethod
    def get_next_available_module(student, program_level):
        """Get the next module the student should work on"""
        progression = ProgressiveAccessManager.get_student_module_progression(student, program_level)

        for item in progression:
            if item['status'] == 'unlocked' and not item['progress'].is_completed:
                return item['module']

        return None

    @staticmethod
    def can_access_lesson(student, lesson):
        """Check if student can access a specific lesson"""
        # First check if the topic's module is accessible
        if not ProgressiveAccessManager.can_access_program_module(student, lesson.topic.program_module):
            return False

        # Check lesson prerequisites
        for prereq in lesson.prerequisites.all():
            try:
                prereq_progress = LessonProgress.objects.get(student=student, lesson=prereq)
                if not prereq_progress.is_completed:
                    return False
            except LessonProgress.DoesNotExist:
                return False

        # Check if previous lessons in the same topic are completed
        previous_lessons = Lesson.objects.filter(
            topic=lesson.topic,
            sequence_order__lt=lesson.sequence_order,
            is_active=True
        )

        for prev_lesson in previous_lessons:
            try:
                prev_progress = LessonProgress.objects.get(student=student, lesson=prev_lesson)
                if not prev_progress.is_completed:
                    return False
            except LessonProgress.DoesNotExist:
                return False

        return True

    @staticmethod
    def get_student_lesson_progression(student, topic):
        """Get detailed progression status for all lessons in a topic"""
        from .models import LessonProgress

        lessons = Lesson.objects.filter(
            topic=topic,
            is_active=True
        ).order_by('sequence_order')

        progression = []
        for lesson in lessons:
            try:
                progress = LessonProgress.objects.get(student=student, lesson=lesson)
                status = 'completed' if progress.is_completed else ('in_progress' if progress.is_started else 'unlocked')
            except LessonProgress.DoesNotExist:
                can_access = ProgressiveAccessManager.can_access_lesson(student, lesson)
                status = 'unlocked' if can_access else 'locked'
                progress = None

            progression.append({
                'lesson': lesson,
                'progress': progress,
                'status': status,
                'can_access': ProgressiveAccessManager.can_access_lesson(student, lesson),
                'completion_percentage': progress.completion_percentage if progress else 0
            })

        return progression

    @staticmethod
    def get_next_required_action(student, program_level):
        """Get the next action the student should take"""
        # Get module progression
        module_progression = ProgressiveAccessManager.get_student_module_progression(student, program_level)

        # Find first incomplete module
        for item in module_progression:
            if item['status'] == 'unlocked':
                # Find first incomplete lesson in this module
                from .models import Lesson, LessonProgress

                topics = item['module'].topics.filter(is_active=True).order_by('order')
                for topic in topics:
                    lessons = Lesson.objects.filter(topic=topic, is_active=True).order_by('sequence_order')

                    for lesson in lessons:
                        if ProgressiveAccessManager.can_access_lesson(student, lesson):
                            lesson_progress = LessonProgress.objects.filter(student=student, lesson=lesson).first()
                            if lesson_progress:
                                if not lesson_progress.is_completed:
                                    return {
                                        'type': 'lesson',
                                        'message': f'Continue with {lesson.title}',
                                        'lesson': lesson,
                                        'module': item['module']
                                    }
                            else:
                                return {
                                    'type': 'lesson',
                                    'message': f'Start {lesson.title}',
                                    'lesson': lesson,
                                    'module': item['module']
                                }

        # Check for pending assignments
        from .models import Assignment, AssignmentSubmission
        from django.utils import timezone

        pending_assignments = Assignment.objects.filter(
            models.Q(lesson__topic__program_module__program_level=program_level) |
            models.Q(topic__program_module__program_level=program_level),
            due_date__gte=timezone.now(),
            is_active=True
        ).exclude(
            submissions__student=student,
            submissions__is_graded=True,
            submissions__grade_percentage__gte=70
        ).order_by('due_date').first()

        if pending_assignments:
            return {
                'type': 'assignment',
                'message': f'Complete assignment: {pending_assignments.title}',
                'assignment': pending_assignments
            }

        return {
            'type': 'complete',
            'message': 'All current tasks completed! Great work!'
        }
        
        if next_program_module:
            # Create and unlock next module
            module_progress, created = ModuleProgress.objects.get_or_create(
                student=student,
                program_module=next_program_module
            )
            module_progress.is_completed = False
            module_progress.save()
            return next_program_module
        
        return None


class CompletionTracker:
    """Tracks completion of modules and resources"""

    @staticmethod
    def mark_module_completed(student, program_module):
        """Mark a module as completed and unlock next module"""
        progress = ModuleProgress.objects.filter(
            student=student,
            program_module=program_module
        ).first()

        if progress:
            progress.is_completed = True
            progress.save()

            # Unlock next module
            ProgressiveAccessManager.unlock_next_modules(student, program_module)

    @staticmethod
    def calculate_module_progress(student, program_module):
        """Calculate completion percentage for a module (stored value)"""
        progress = ModuleProgress.objects.filter(
            student=student,
            program_module=program_module
        ).first()

        if progress:
            return progress.progress_percentage
        return 0

    @staticmethod
    def update_module_progress_from_lessons(student, program_module):
        """Recalculate module progress based on completed lessons and unlock next module if threshold met"""
        # Count all active lessons in this program module
        total_lessons = Lesson.objects.filter(
            topic__program_module=program_module,
            is_active=True
        ).count()
        if total_lessons == 0:
            # Nothing to compute
            return 0

        completed_lessons = LessonProgress.objects.filter(
            student=student,
            lesson__topic__program_module=program_module,
            is_completed=True
        ).count()

        percentage = round((completed_lessons / total_lessons) * 100, 2)

        module_progress, _ = ModuleProgress.objects.get_or_create(
            student=student,
            program_module=program_module
        )

        was_completed = module_progress.is_completed
        module_progress.progress_percentage = percentage

        if percentage >= program_module.minimum_completion_percentage:
            module_progress.is_completed = True
            if not was_completed:
                module_progress.completed_at = timezone.now()
                # Unlock next modules only once when crossing the threshold
                ProgressiveAccessManager.unlock_next_modules(student, program_module)

        module_progress.save()
        return percentage