"""
Utility functions for progressive learning and prerequisite validation
"""
from django.contrib.auth.models import User
from .models import Module, Week, ModuleProgress, WeekProgress, ResourceView
from students.models import StudentEnrollment


class ProgressiveAccessManager:
    """Manages progressive access to modules and weeks"""
    
    @staticmethod
    def initialize_student_progress(student, faculty_program):
        """Initialize progress tracking for a new student enrollment"""
        # Get first module in the program
        first_module = Module.objects.filter(
            faculty_program=faculty_program,
            is_active=True
        ).order_by('month_number').first()
        
        if first_module:
            # Create and unlock first module
            module_progress, created = ModuleProgress.objects.get_or_create(
                student=student,
                module=first_module
            )
            module_progress.is_unlocked = True
            module_progress.save()
            
            # Unlock first week of first module
            first_week = first_module.weeks.filter(week_number=1).first()
            if first_week:
                week_progress, created = WeekProgress.objects.get_or_create(
                    student=student,
                    week=first_week
                )
                week_progress.is_unlocked = True
                week_progress.save()
    
    @staticmethod
    def can_access_module(student, module):
        """Check if student can access a specific module"""
        # Check if student is enrolled in this faculty program
        from students.models import StudentEnrollment
        try:
            enrollment = StudentEnrollment.objects.get(
                student=student,
                faculty_program=module.faculty_program,
                status='active'
            )
        except StudentEnrollment.DoesNotExist:
            return False

        try:
            progress = ModuleProgress.objects.get(student=student, module=module)
            return progress.is_unlocked
        except ModuleProgress.DoesNotExist:
            # Check if this is the first module - if so, auto-unlock it
            first_module = Module.objects.filter(
                faculty_program=module.faculty_program,
                is_active=True
            ).order_by('month_number').first()

            if module == first_module:
                # Auto-create and unlock first module
                progress, created = ModuleProgress.objects.get_or_create(
                    student=student,
                    module=module
                )
                progress.is_unlocked = True
                progress.save()
                return True
            return False
    
    @staticmethod
    def can_access_week(student, week):
        """Check if student can access a specific week"""
        # First check if module is accessible
        if not ProgressiveAccessManager.can_access_module(student, week.module):
            return False

        try:
            progress = WeekProgress.objects.get(student=student, week=week)
            return progress.is_unlocked
        except WeekProgress.DoesNotExist:
            # Check if this is the first week or if previous week is completed
            if week.week_number == 1:
                # Auto-create and unlock first week if module is accessible
                progress, created = WeekProgress.objects.get_or_create(
                    student=student,
                    week=week
                )
                progress.is_unlocked = True
                progress.save()
                return True
            else:
                previous_week = Week.objects.filter(
                    module=week.module,
                    week_number=week.week_number - 1
                ).first()
                if previous_week:
                    try:
                        prev_progress = WeekProgress.objects.get(
                            student=student,
                            week=previous_week
                        )
                        return prev_progress.is_completed
                    except WeekProgress.DoesNotExist:
                        return False
                return False
    
    @staticmethod
    def unlock_next_week(student, current_week):
        """Unlock the next week after completing current week"""
        next_week = Week.objects.filter(
            module=current_week.module,
            week_number=current_week.week_number + 1
        ).first()
        
        if next_week:
            week_progress, created = WeekProgress.objects.get_or_create(
                student=student,
                week=next_week
            )
            week_progress.is_unlocked = True
            week_progress.save()
            return next_week
        return None
    
    @staticmethod
    def get_student_accessible_modules(student, faculty_program):
        """Get all modules accessible to a student"""
        accessible_modules = []
        modules = Module.objects.filter(
            faculty_program=faculty_program,
            is_active=True
        ).order_by('month_number')
        
        for module in modules:
            if ProgressiveAccessManager.can_access_module(student, module):
                accessible_modules.append(module)
            else:
                break  # Stop at first inaccessible module
        
        return accessible_modules
    
    @staticmethod
    def get_student_accessible_weeks(student, module):
        """Get all weeks accessible to a student in a module"""
        accessible_weeks = []
        weeks = module.weeks.all().order_by('week_number')
        
        for week in weeks:
            if ProgressiveAccessManager.can_access_week(student, week):
                accessible_weeks.append(week)
            else:
                break  # Stop at first inaccessible week
        
        return accessible_weeks
    
    @staticmethod
    def get_next_required_action(student, faculty_program):
        """Get the next action required for student progression"""
        try:
            enrollment = StudentEnrollment.objects.get(
                student=student,
                faculty_program=faculty_program
            )
        except StudentEnrollment.DoesNotExist:
            return None
        
        # Find current module and week
        accessible_modules = ProgressiveAccessManager.get_student_accessible_modules(
            student, faculty_program
        )
        
        if not accessible_modules:
            return {
                'type': 'enrollment',
                'message': 'Complete enrollment process to begin learning'
            }
        
        # Check current progress
        for module in accessible_modules:
            accessible_weeks = ProgressiveAccessManager.get_student_accessible_weeks(
                student, module
            )
            
            for week in accessible_weeks:
                week_progress = week.get_or_create_progress(student)
                
                if not week_progress.is_completed:
                    # Check what's needed to complete this week
                    incomplete_items = []
                    
                    # Check required resources
                    required_resources = week.learning_resources.filter(
                        is_required=True, is_active=True
                    )
                    for resource in required_resources:
                        try:
                            resource_view = ResourceView.objects.get(
                                student=student, resource=resource
                            )
                            if not resource_view.completed:
                                incomplete_items.append(f"Complete resource: {resource.title}")
                        except ResourceView.DoesNotExist:
                            incomplete_items.append(f"View resource: {resource.title}")
                    
                    # Check assignment submission
                    if hasattr(week, 'assignment') and week.assignment.is_required:
                        from .models import AssignmentSubmission
                        if not AssignmentSubmission.objects.filter(
                            assignment=week.assignment, student=student
                        ).exists():
                            incomplete_items.append(f"Submit assignment: {week.assignment.title}")
                    
                    if incomplete_items:
                        return {
                            'type': 'week_completion',
                            'week': week,
                            'module': module,
                            'incomplete_items': incomplete_items,
                            'message': f"Complete Week {week.week_number}: {week.theme}"
                        }
        
        return {
            'type': 'completed',
            'message': 'All available content completed! Check back for new modules.'
        }


class CompletionTracker:
    """Handles completion tracking and automatic progression"""
    
    @staticmethod
    def mark_resource_viewed(student, resource):
        """Mark a resource as viewed and increment view count"""
        resource_view, created = ResourceView.objects.get_or_create(
            student=student,
            resource=resource
        )
        
        if not created:
            resource_view.view_count += 1
            resource_view.save()
        
        return resource_view
    
    @staticmethod
    def mark_resource_completed(student, resource):
        """Mark a resource as completed"""
        resource_view = CompletionTracker.mark_resource_viewed(student, resource)
        resource_view.mark_completed()
        
        # Check if this completes the week
        week_progress = resource.week.get_or_create_progress(student)
        if week_progress.mark_completed():
            # Week completed, unlock next week
            ProgressiveAccessManager.unlock_next_week(student, resource.week)
        
        return resource_view
    
    @staticmethod
    def check_assignment_completion(student, assignment):
        """Check if assignment submission completes the week"""
        week_progress = assignment.week.get_or_create_progress(student)
        if week_progress.mark_completed():
            # Week completed, unlock next week
            ProgressiveAccessManager.unlock_next_week(student, assignment.week)
