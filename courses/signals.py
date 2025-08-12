"""
Signals for automatic progress initialization and tracking
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from students.models import StudentEnrollment
from .models import AssignmentSubmission
from .utils import ProgressiveAccessManager, CompletionTracker


@receiver(post_save, sender=StudentEnrollment)
def initialize_student_progress(sender, instance, created, **kwargs):
    """Initialize progressive learning when a student enrolls"""
    if created and instance.status == 'active':
        ProgressiveAccessManager.initialize_student_progress(
            instance.student,
            instance.faculty_program
        )


@receiver(post_save, sender=AssignmentSubmission)
def check_assignment_completion(sender, instance, created, **kwargs):
    """Check if assignment submission completes the week"""
    if created:
        CompletionTracker.check_assignment_completion(
            instance.student,
            instance.assignment
        )
