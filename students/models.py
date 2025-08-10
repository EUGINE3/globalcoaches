from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from faculties.models import FacultyProgram

class StudentEnrollment(models.Model):
    """Student enrollment in faculty programs"""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('suspended', 'Suspended'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    faculty_program = models.ForeignKey(FacultyProgram, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField(blank=True, null=True)
    expected_completion_date = models.DateField(blank=True, null=True)
    actual_completion_date = models.DateField(blank=True, null=True)
    total_credits_earned = models.IntegerField(default=0)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['student', 'faculty_program']

    def __str__(self):
        return f"{self.student.username} - {self.faculty_program}"

    def calculate_progress_percentage(self):
        """Calculate completion percentage"""
        if not self.faculty_program.academic_level.credits_required:
            return 0
        return (self.total_credits_earned / self.faculty_program.academic_level.credits_required) * 100

class Certificate(models.Model):
    """Student certificates and graduation records"""
    CERTIFICATE_TYPES = [
        ('completion', 'Certificate of Completion'),
        ('diploma', 'Diploma'),
        ('higher_diploma', 'Higher Diploma'),
        ('masterclass', 'Masterclass Certificate'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    enrollment = models.OneToOneField(StudentEnrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPES)
    certificate_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField(default=timezone.now)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.certificate_type} - {self.certificate_number}"

class StudentReflection(models.Model):
    """Student reflections and journal entries"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reflections')
    enrollment = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE, related_name='reflections')
    title = models.CharField(max_length=200)
    content = models.TextField()
    week_reference = models.CharField(max_length=100, blank=True, help_text="Reference to specific week/module")
    is_private = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - {self.title}"

class FinalProject(models.Model):
    """Final projects for graduation"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='final_projects')
    enrollment = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE, related_name='final_projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    project_file = models.FileField(upload_to='final_projects/')
    presentation_file = models.FileField(upload_to='final_presentations/', blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    defense_date = models.DateTimeField(blank=True, null=True)
    grade = models.CharField(max_length=10, blank=True)
    feedback = models.TextField(blank=True)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_projects')

    def __str__(self):
        return f"{self.student.username} - {self.title}"

