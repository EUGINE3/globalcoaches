from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from faculties.models import FacultyProgram
import os

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

    def is_unlocked_for_student(self, student):
        """Check if this module is unlocked for a student"""
        # Check if student is enrolled
        from students.models import StudentEnrollment
        try:
            enrollment = StudentEnrollment.objects.get(
                student=student,
                faculty_program=self.faculty_program,
                status='active'
            )
        except StudentEnrollment.DoesNotExist:
            return False

        try:
            progress = ModuleProgress.objects.get(student=student, module=self)
            return progress.is_unlocked
        except ModuleProgress.DoesNotExist:
            # First module in program should be unlocked by default for enrolled students
            first_module = Module.objects.filter(
                faculty_program=self.faculty_program,
                is_active=True
            ).order_by('month_number').first()
            return self == first_module

    def get_or_create_progress(self, student):
        """Get or create module progress for student"""
        progress, created = ModuleProgress.objects.get_or_create(
            student=student,
            module=self
        )
        if created and self.is_unlocked_for_student(student):
            progress.is_unlocked = True
            progress.save()
        return progress

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

    def is_unlocked_for_student(self, student):
        """Check if this week is unlocked for a student"""
        try:
            progress = WeekProgress.objects.get(student=student, week=self)
            return progress.is_unlocked
        except WeekProgress.DoesNotExist:
            # Check if previous week is completed or if this is the first week
            if self.week_number == 1:
                # First week is always unlocked if module is unlocked (for enrolled students)
                return self.module.is_unlocked_for_student(student)
            else:
                # Check if previous week is completed
                previous_week = Week.objects.filter(
                    module=self.module,
                    week_number=self.week_number - 1
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

    def get_or_create_progress(self, student):
        """Get or create week progress for student"""
        progress, created = WeekProgress.objects.get_or_create(
            student=student,
            week=self
        )
        if created and self.is_unlocked_for_student(student):
            progress.is_unlocked = True
            progress.save()
        return progress


def weekly_resource_upload_path(instance, filename):
    """Generate upload path for weekly resources"""
    # Create path: weekly_resources/faculty_program/module_code/week_number/filename
    return f"weekly_resources/{instance.week.module.faculty_program.slug}/{instance.week.module.course_code}/week_{instance.week.week_number}/{filename}"


class WeeklyResource(models.Model):
    """Learning resources (videos, PDFs) for each week"""
    RESOURCE_TYPE_CHOICES = [
        ('video', 'Video'),
        ('pdf', 'PDF Document'),
        ('document', 'Document'),
        ('link', 'External Link'),
    ]

    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name='learning_resources')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Brief description of the resource")
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)

    # File upload fields
    file = models.FileField(
        upload_to=weekly_resource_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'])],
        help_text="Upload video or document files"
    )

    # External link field
    external_url = models.URLField(blank=True, help_text="External link to resource (YouTube, Vimeo, etc.)")

    # Metadata
    file_size = models.BigIntegerField(blank=True, null=True, help_text="File size in bytes")
    duration = models.DurationField(blank=True, null=True, help_text="Duration for video resources")
    is_required = models.BooleanField(default=False, help_text="Is this resource required for completion?")
    order = models.PositiveIntegerField(default=0, help_text="Display order within the week")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['week', 'order', 'created_at']
        unique_together = ['week', 'order']

    def __str__(self):
        return f"{self.week} - {self.title}"

    def get_file_extension(self):
        """Get file extension from uploaded file"""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return None

    def is_video(self):
        """Check if the resource is a video file"""
        if self.resource_type == 'video':
            return True
        if self.file:
            video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
            return self.get_file_extension() in video_extensions
        return False

    def is_pdf(self):
        """Check if the resource is a PDF file"""
        if self.resource_type == 'pdf':
            return True
        if self.file:
            return self.get_file_extension() == '.pdf'
        return False

    def get_file_size_display(self):
        """Get human readable file size"""
        if not self.file_size:
            return None

        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"

    def save(self, *args, **kwargs):
        """Override save to set file size automatically"""
        if self.file and hasattr(self.file, 'size'):
            self.file_size = self.file.size
        super().save(*args, **kwargs)

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

class ResourceView(models.Model):
    """Track when students view/complete learning resources"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(WeeklyResource, on_delete=models.CASCADE)
    first_viewed_at = models.DateTimeField(default=timezone.now)
    last_viewed_at = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(blank=True, null=True)
    view_count = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ['student', 'resource']

    def __str__(self):
        return f"{self.student.username} - {self.resource.title}"

    def mark_completed(self):
        """Mark resource as completed"""
        if not self.completed:
            self.completed = True
            self.completion_date = timezone.now()
            self.save()


class WeekProgress(models.Model):
    """Track student progress through individual weeks"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_unlocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ['student', 'week']

    def __str__(self):
        return f"{self.student.username} - {self.week}"

    @property
    def is_completed(self):
        """Check if week is completed based on requirements"""
        return self.completed_at is not None

    def check_completion_requirements(self):
        """Check if all requirements for week completion are met"""
        week = self.week

        # Check if assignment is submitted (if required)
        if hasattr(week, 'assignment') and week.assignment.is_required:
            assignment_submitted = AssignmentSubmission.objects.filter(
                assignment=week.assignment,
                student=self.student
            ).exists()
            if not assignment_submitted:
                return False

        # Check if all required resources are completed
        required_resources = week.learning_resources.filter(is_required=True, is_active=True)
        for resource in required_resources:
            resource_completed = ResourceView.objects.filter(
                student=self.student,
                resource=resource,
                completed=True
            ).exists()
            if not resource_completed:
                return False

        return True

    def mark_completed(self):
        """Mark week as completed if requirements are met"""
        if self.check_completion_requirements() and not self.is_completed:
            self.completed_at = timezone.now()
            self.save()

            # Check if this completes the module
            module_progress, created = ModuleProgress.objects.get_or_create(
                student=self.student,
                module=self.week.module
            )
            module_progress.check_completion()

            return True
        return False


class ModuleProgress(models.Model):
    """Track student progress through modules"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_unlocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ['student', 'module']

    def __str__(self):
        return f"{self.student.username} - {self.module.course_code}"

    @property
    def is_completed(self):
        """Check if module is completed"""
        return self.completed_at is not None

    @property
    def completion_percentage(self):
        """Calculate completion percentage based on weeks completed"""
        total_weeks = self.module.weeks.count()
        if total_weeks == 0:
            return 0

        completed_weeks = WeekProgress.objects.filter(
            student=self.student,
            week__module=self.module,
            completed_at__isnull=False
        ).count()

        return (completed_weeks / total_weeks) * 100

    def check_completion(self):
        """Check if all weeks in module are completed"""
        total_weeks = self.module.weeks.count()
        completed_weeks = WeekProgress.objects.filter(
            student=self.student,
            week__module=self.module,
            completed_at__isnull=False
        ).count()

        if total_weeks > 0 and completed_weeks == total_weeks and not self.is_completed:
            self.completed_at = timezone.now()
            self.save()

            # Unlock next module if exists
            self.unlock_next_module()

            return True
        return False

    def unlock_next_module(self):
        """Unlock the next module in sequence"""
        from students.models import StudentEnrollment

        try:
            enrollment = StudentEnrollment.objects.get(
                student=self.student,
                faculty_program=self.module.faculty_program
            )

            # Find next module in sequence
            next_module = Module.objects.filter(
                faculty_program=self.module.faculty_program,
                month_number=self.module.month_number + 1,
                is_active=True
            ).first()

            if next_module:
                next_progress, created = ModuleProgress.objects.get_or_create(
                    student=self.student,
                    module=next_module
                )
                if created or not next_progress.is_unlocked:
                    next_progress.is_unlocked = True
                    next_progress.save()

                    # Unlock first week of next module
                    first_week = next_module.weeks.filter(week_number=1).first()
                    if first_week:
                        week_progress, created = WeekProgress.objects.get_or_create(
                            student=self.student,
                            week=first_week
                        )
                        week_progress.is_unlocked = True
                        week_progress.save()

        except StudentEnrollment.DoesNotExist:
            pass


class StudentProgress(models.Model):
    """Legacy model - kept for backward compatibility"""
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

