"""
Signals for automatic progress initialization and tracking
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from students.models import StudentEnrollment
from .utils import ProgressiveAccessManager


# Temporarily disabled to avoid model conflicts
# @receiver(post_save, sender=StudentEnrollment)
# def initialize_student_progress(sender, instance, created, **kwargs):
#     """Initialize progressive learning when a student enrolls"""
#     if created and instance.status == 'active':
#         ProgressiveAccessManager.initialize_student_progress(
#             instance.student
#         )
