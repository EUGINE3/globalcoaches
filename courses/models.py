from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from faculties.models import FacultyProgram

class Module(models.Model):
    """Monthly modules for each faculty program"""
    faculty_program = models.ForeignKey(FacultyProgram, on_delete=models.CASCADE, related_name='modules')
    name = models.CharField(max_length=200)
    course_code = models.CharField(max_length=20, unique=True, help_text="e.g., GCCT-M101")
    credits = models.IntegerField(default=2)
    month_number = models.IntegerField()
    description = models.TextField()
    learning_objectives = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['faculty_program', 'month_number']
        ordering = ['faculty_program', 'month_number']

    def __str__(self):
        return f"{self.course_code} - {self.name}"

class Week(models.Model):
    """Weekly breakdown within each module (4 weeks per module)"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='weeks')
    week_number = models.IntegerField()  # 1-4
    theme = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    scripture_quote = models.TextField(blank=True, help_text="For faith-based faculties")
    thought_quote = models.TextField(blank=True, help_text="For non-faith-based faculties")
    content = models.TextField()
    resources = models.TextField(blank=True, help_text="Additional resources and readings")
    
    class Meta:
        unique_together = ['module', 'week_number']
        ordering = ['module', 'week_number']

    def __str__(self):
        return f"{self.module.course_code} - Week {self.week_number}: {self.theme}"

class Assignment(models.Model):
    """Weekly practical assignments"""
    week = models.OneToOneField(Week, on_delete=models.CASCADE, related_name='assignment')
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField()
    max_points = models.IntegerField(default=100)
    due_date_offset = models.IntegerField(default=7, help_text="Days from week start")
    submission_format = models.CharField(max_length=100, default="PDF/Word Document")
    is_required = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.week.module.course_code} - Week {self.week.week_number} Assignment"

class AssignmentSubmission(models.Model):
    """Student assignment submissions"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    file_upload = models.FileField(upload_to='assignment_submissions/')
    text_submission = models.TextField(blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    grade = models.IntegerField(blank=True, null=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_assignments')
    graded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

class StudentProgress(models.Model):
    """Track student progress through modules and weeks"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    week = models.ForeignKey(Week, on_delete=models.CASCADE, blank=True, null=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['student', 'module', 'week']

    def __str__(self):
        return f"{self.student.username} - {self.module.course_code} Progress"

