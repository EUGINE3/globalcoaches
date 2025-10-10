from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from programs.models import ProgramLevel, ProgramModule
from students.models import StudentEnrollment
from django.core.validators import MinValueValidator, MaxValueValidator
from .quiz_models import QuizQuestion, QuizChoice
import os


def weekly_resource_upload_path(instance, filename):
    """Generate upload path for weekly resources"""
    return f'weekly_resources/{instance.course.program_module.program_level.level_type}/{instance.course.program_module.module.module_type}/week_{instance.week_number}/{filename}'



class Module(models.Model):
    """The 7 integrated modules that cut across all levels"""
    MODULE_CHOICES = [
        ('young_theologians', 'Module 1: Young Theologians and Gospel Advancing'),
        ('missional_leadership', 'Module 2: Missional Leadership'),
        ('sdgs_community', 'Module 3: SDGs & Community Transformation'),
        ('education_sustainable', 'Module 4: Education for Sustainable Development & Global Citizenship'),
        ('entrepreneurship', 'Module 5: Entrepreneurship and Political Economics'),
        ('diplomacy', 'Module 6: Diplomacy & Global Leadership'),
        ('climate_warriors', 'Module 7: Climate Warriors'),
    ]
    
    name = models.CharField(max_length=200)
    module_type = models.CharField(max_length=50, choices=MODULE_CHOICES, unique=True)
    description = models.TextField()
    learning_objectives = models.TextField()
    image = models.ImageField(upload_to='module_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"

    def __str__(self):
        return self.name




class ModuleTopic(models.Model):
    """Individual topics within a module with theory and practical components"""
    program_module = models.ForeignKey(ProgramModule, on_delete=models.CASCADE, related_name='topics')
    topic_number = models.IntegerField(help_text="Topic number within the module")
    title = models.CharField(max_length=200)
    description = models.TextField()
    learning_objectives = models.TextField(help_text="Specific learning objectives for this topic")
    
    # Credit and time allocation
    total_credits = models.IntegerField(help_text="Total credits for this topic")
    total_hours = models.IntegerField(help_text="Total hours for this topic")
    theory_hours = models.IntegerField(help_text="Theory component hours")
    practical_hours = models.IntegerField(help_text="Practical component hours")
    
    # Theory component
    theory_content = models.TextField(help_text="Theory content and classroom activities")
    theory_resources = models.TextField(blank=True, help_text="Required readings, case studies, etc.")
    
    # Practical component
    practical_activities = models.TextField(help_text="Practical activities and exercises")
    practical_deliverables = models.TextField(help_text="What students need to produce")
    assessment_criteria = models.TextField(help_text="How this topic will be assessed")
    
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order within the module")
    
    class Meta:
        unique_together = ['program_module', 'topic_number']
        ordering = ['program_module', 'order', 'topic_number']
        verbose_name = "Module Topic"
        verbose_name_plural = "Module Topics"
    
    def __str__(self):
        return f"Topic {self.topic_number}: {self.title}"
    
    def save(self, *args, **kwargs):
        # Ensure total hours equals theory + practical
        if self.theory_hours and self.practical_hours:
            self.total_hours = self.theory_hours + self.practical_hours
        super().save(*args, **kwargs)

    def get_lessons_count(self):
        """Get total number of lessons in this topic"""
        return self.lessons.filter(is_active=True).count()

    def get_total_resources_count(self):
        """Get total number of resources across all lessons"""
        return LessonResource.objects.filter(
            lesson__topic=self,
            lesson__is_active=True,
            is_active=True
        ).count()


class Lesson(models.Model):
    """Individual lessons/sessions within a topic"""
    topic = models.ForeignKey(ModuleTopic, on_delete=models.CASCADE, related_name='lessons')
    lesson_number = models.IntegerField(help_text="Lesson number within the topic")
    title = models.CharField(max_length=200)
    description = models.TextField()
    learning_objectives = models.TextField(help_text="Specific learning objectives for this lesson")

    # Lesson type and duration
    LESSON_TYPES = [
        ('theory', 'Theory Session'),
        ('practical', 'Practical Session'),
        ('mixed', 'Mixed Session'),
        ('assessment', 'Assessment Session'),
        ('discussion', 'Discussion Session'),
    ]
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default='mixed')
    duration_minutes = models.IntegerField(default=90, help_text="Lesson duration in minutes")

    # Content and instructions
    content = models.TextField(help_text="Lesson content and instructions")
    instructor_notes = models.TextField(blank=True, help_text="Notes for instructors")

    # Progressive access
    sequence_order = models.IntegerField(default=1, help_text="Order within the topic")
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, help_text="Lessons that must be completed first")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['topic', 'lesson_number']
        ordering = ['topic', 'sequence_order', 'lesson_number']
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"

    def __str__(self):
        return f"{self.topic.title} - Lesson {self.lesson_number}: {self.title}"

    def get_resources_count(self):
        """Get number of resources in this lesson"""
        return self.resources.filter(is_active=True).count()

    def get_assignments_count(self):
        """Get number of assignments in this lesson"""
        return self.assignments.filter(is_active=True).count()


def lesson_resource_upload_path(instance, filename):
    """Generate upload path for lesson resources"""
    return f'lesson_resources/{instance.lesson.topic.program_module.program_level.level_type}/{instance.lesson.topic.program_module.module.module_type}/topic_{instance.lesson.topic.topic_number}/lesson_{instance.lesson.lesson_number}/{filename}'


class LessonResource(models.Model):
    """Resources for individual lessons"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')

    # Resource type and content
    RESOURCE_TYPES = [
        ('video', 'Video'),
        ('reading', 'Reading Material'),
        ('document', 'Document'),
        ('link', 'External Link'),
        ('presentation', 'Presentation'),
        ('audio', 'Audio'),
        ('interactive', 'Interactive Content'),
    ]
    # resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)

    # Content fields
    content = models.TextField(blank=True, help_text="Text content or description")
    file = models.FileField(upload_to=lesson_resource_upload_path, blank=True, null=True)
    url = models.URLField(blank=True, help_text="External URL for links")

    # Settings
    is_required = models.BooleanField(default=True, help_text="Required for lesson completion")
    # estimated_duration_minutes = models.IntegerField(default=15, help_text="Estimated time to complete")
    order = models.IntegerField(default=0, help_text="Display order within lesson")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['lesson', 'order', 'created_at']
        verbose_name = "Lesson Resource"
        verbose_name_plural = "Lesson Resources"

    def __str__(self):
        if self.file:
            filename = os.path.basename(self.file.name)
            return f"{self.lesson.title} - {filename}"
        elif self.url:
            return f"{self.lesson.title} - Link"
        else:
            return f"{self.lesson.title} - Resource"

    def get_file_extension(self):
        """Get file extension for display"""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return None

    def get_resource_name(self):
        """Get the name of the resource (filename or URL)"""
        if self.file:
            return os.path.basename(self.file.name)
        elif self.url:
            return self.url
        return "No file or URL"

    def get_resource_type_display(self):
        """Get the type of resource based on file extension or URL"""
        if self.file:
            ext = self.get_file_extension()
            if ext:
                if ext in ['.mp4', '.avi', '.mov', '.wmv']:
                    return 'Video'
                elif ext in ['.pdf', '.doc', '.docx']:
                    return 'Document'
                elif ext in ['.ppt', '.pptx']:
                    return 'Presentation'
                elif ext in ['.mp3', '.wav', '.m4a']:
                    return 'Audio'
                else:
                    return 'File'
        elif self.url:
            return 'External Link'
        return 'Unknown'

    def has_file(self):
        """Check if resource has a file"""
        return bool(self.file)

    def has_url(self):
        """Check if resource has a URL"""
        return bool(self.url)


def assignment_upload_path(instance, filename):
    """Generate upload path for assignment files"""
    return f'assignments/{instance.lesson.topic.program_module.program_level.level_type}/{instance.lesson.topic.program_module.module.module_type}/topic_{instance.lesson.topic.topic_number}/lesson_{instance.lesson.lesson_number}/{filename}'


class Assignment(models.Model):
    """Assignments for lessons or topics"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments', null=True, blank=True)
    topic = models.ForeignKey(ModuleTopic, on_delete=models.CASCADE, related_name='assignments', null=True, blank=True)

    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField(help_text="Detailed instructions for students")

    # Assignment settings
    ASSIGNMENT_TYPES = [
        ('essay', 'Essay'),
        ('project', 'Project'),
        ('presentation', 'Presentation'),
        ('practical', 'Practical Exercise'),
        ('research', 'Research Assignment'),
        ('case_study', 'Case Study'),
        ('reflection', 'Reflection Paper'),
        ('quiz', 'Quiz'),
        ('exam', 'Exam'),
    ]
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES)

    # Grading and deadlines
    max_points = models.IntegerField(default=100, help_text="Maximum points for this assignment")
    due_date = models.DateTimeField(help_text="Assignment due date")
    late_submission_penalty = models.IntegerField(default=10, help_text="Percentage penalty per day late")
    allow_late_submission = models.BooleanField(default=True)

    # Files and resources
    assignment_file = models.FileField(upload_to=assignment_upload_path, blank=True, null=True, help_text="Assignment document or template")
    rubric_file = models.FileField(upload_to=assignment_upload_path, blank=True, null=True, help_text="Grading rubric")

    # Quiz specific fields
    is_quiz = models.BooleanField(default=False)
    time_limit_minutes = models.IntegerField(null=True, blank=True)
    passing_score = models.IntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Minimum score required to pass (%)'
    )
    shuffle_questions = models.BooleanField(default=True)
    show_correct_answers = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'created_at']
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self):
        if self.lesson:
            return f"{self.lesson.title} - {self.title}"
        elif self.topic:
            return f"{self.topic.title} - {self.title}"
        return self.title

    def clean(self):
        """Ensure assignment is linked to either lesson or topic, not both"""
        from django.core.exceptions import ValidationError
        if not self.lesson and not self.topic:
            raise ValidationError("Assignment must be linked to either a lesson or a topic.")
        if self.lesson and self.topic:
            raise ValidationError("Assignment cannot be linked to both lesson and topic.")

    def is_overdue(self):
        """Check if assignment is overdue"""
        return timezone.now() > self.due_date

    def days_until_due(self):
        """Get days until due date"""
        delta = self.due_date - timezone.now()
        return delta.days if delta.days > 0 else 0


def submission_upload_path(instance, filename):
    """Generate upload path for student submissions"""
    assignment = instance.assignment
    if assignment.lesson:
        return f'submissions/{assignment.lesson.topic.program_module.program_level.level_type}/{assignment.lesson.topic.program_module.module.module_type}/topic_{assignment.lesson.topic.topic_number}/lesson_{assignment.lesson.lesson_number}/{instance.student.username}/{filename}'
    elif assignment.topic:
        return f'submissions/{assignment.topic.program_module.program_level.level_type}/{assignment.topic.program_module.module.module_type}/topic_{assignment.topic.topic_number}/{instance.student.username}/{filename}'
    return f'submissions/misc/{instance.student.username}/{filename}'


class AssignmentSubmission(models.Model):
    """Student submissions for assignments"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions')

    # Submission content
    submission_text = models.TextField(blank=True, help_text="Text submission or notes")
    submission_file = models.FileField(upload_to=submission_upload_path, blank=True, null=True)

    # Submission tracking
    submitted_at = models.DateTimeField(default=timezone.now)
    is_late = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1, help_text="Submission attempt number")

    # Grading
    is_graded = models.BooleanField(default=False)
    points_earned = models.IntegerField(null=True, blank=True)
    grade_percentage = models.FloatField(null=True, blank=True)

    # Feedback
    instructor_feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions')

    class Meta:
        unique_together = ['assignment', 'student', 'attempt_number']
        ordering = ['-submitted_at']
        verbose_name = "Assignment Submission"
        verbose_name_plural = "Assignment Submissions"

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title} (Attempt {self.attempt_number})"

    def save(self, *args, **kwargs):
        # Check if submission is late
        if not self.pk:  # Only on creation
            self.is_late = timezone.now() > self.assignment.due_date

        # Calculate grade percentage
        if self.points_earned is not None and self.assignment.max_points > 0:
            self.grade_percentage = (self.points_earned / self.assignment.max_points) * 100

        super().save(*args, **kwargs)

    def get_letter_grade(self):
        """Convert percentage to letter grade"""
        if self.grade_percentage is None:
            return "Not Graded"

        if self.grade_percentage >= 90:
            return "A"
        elif self.grade_percentage >= 80:
            return "B"
        elif self.grade_percentage >= 70:
            return "C"
        elif self.grade_percentage >= 60:
            return "D"
        else:
            return "F"

    def get_status(self):
        """Get submission status"""
        if not self.is_graded:
            return "Pending Review"
        elif self.grade_percentage >= 70:
            return "Passed"
        else:
            return "Needs Improvement"


class LessonProgress(models.Model):
    """Track student progress through lessons"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='student_progress')

    # Progress tracking
    is_started = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    completion_percentage = models.FloatField(default=0.0)

    # Time tracking
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    time_spent_minutes = models.IntegerField(default=0)

    class Meta:
        unique_together = ['student', 'lesson']
        verbose_name = "Lesson Progress"
        verbose_name_plural = "Lesson Progress"

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"

    def calculate_progress(self):
        """Calculate lesson completion based on resources and assignments"""
        total_items = 0
        completed_items = 0

        # Count required resources
        required_resources = self.lesson.resources.filter(is_required=True, is_active=True)
        total_items += required_resources.count()

        # Count completed resources
        completed_resources = ResourceProgress.objects.filter(
            student=self.student,
            resource__in=required_resources,
            is_completed=True
        ).count()
        completed_items += completed_resources

        # Count assignments
        assignments = self.lesson.assignments.filter(is_active=True)
        total_items += assignments.count()

        # Count completed assignments (graded submissions)
        completed_assignments = AssignmentSubmission.objects.filter(
            student=self.student,
            assignment__in=assignments,
            is_graded=True,
            grade_percentage__gte=70  # Passing grade
        ).count()
        completed_items += completed_assignments

        # Calculate percentage
        if total_items > 0:
            self.completion_percentage = (completed_items / total_items) * 100
            self.is_completed = self.completion_percentage >= 100

            if self.is_completed and not self.completed_at:
                self.completed_at = timezone.now()
        else:
            self.completion_percentage = 100
            self.is_completed = True

        self.save()
        return self.completion_percentage


class ResourceProgress(models.Model):
    """Track student progress through lesson resources"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_progress')
    resource = models.ForeignKey(LessonResource, on_delete=models.CASCADE, related_name='student_progress')

    # Progress tracking
    is_viewed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)

    # Time tracking
    first_viewed_at = models.DateTimeField(null=True, blank=True)
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.IntegerField(default=0)

    class Meta:
        unique_together = ['student', 'resource']
        verbose_name = "Resource Progress"
        verbose_name_plural = "Resource Progress"

    def __str__(self):
        return f"{self.student.username} - {self.resource.title}"

    def mark_viewed(self):
        """Mark resource as viewed"""
        now = timezone.now()
        if not self.is_viewed:
            self.is_viewed = True
            self.first_viewed_at = now

        self.last_viewed_at = now
        self.view_count += 1
        self.save()

    def mark_completed(self):
        """Mark resource as completed"""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            if not self.is_viewed:
                self.mark_viewed()
            self.save()

class Course(models.Model):
    """Individual courses within modules"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    program_module = models.ForeignKey(ProgramModule, on_delete=models.CASCADE, related_name='courses')
    week_count = models.IntegerField(default=4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.title

class WeeklyResource(models.Model):
    """Weekly learning resources for courses"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='weekly_resources')
    week_number = models.IntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    resource_type = models.CharField(max_length=50, choices=[
        ('video', 'Video'),
        ('reading', 'Reading'),
        ('assignment', 'Assignment'),
        ('discussion', 'Discussion'),
        ('quiz', 'Quiz'),
    ])
    is_required = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['course', 'week_number', 'order']
        ordering = ['week_number', 'order']

    def __str__(self):
        return f"Week {self.week_number}: {self.title}"

class WeekProgress(models.Model):
    """Track student progress through weekly resources"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    weekly_resource = models.ForeignKey(WeeklyResource, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['student', 'weekly_resource']

    def __str__(self):
        return f"{self.student.username} - {self.weekly_resource.title}"

class ResourceView(models.Model):
    """Track when students view resources"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    weekly_resource = models.ForeignKey(WeeklyResource, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(default=timezone.now)
    time_spent = models.IntegerField(default=0, help_text="Time spent in seconds")

    class Meta:
        unique_together = ['student', 'weekly_resource']

    def __str__(self):
        return f"{self.student.username} viewed {self.weekly_resource.title}"

class ModuleProgress(models.Model):
    """Track overall module progress for students"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    program_module = models.ForeignKey(ProgramModule, on_delete=models.CASCADE)
    progress_percentage = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)

    # Progressive learning tracking
    is_unlocked = models.BooleanField(default=False, help_text="Whether this module is accessible to the student")
    unlocked_at = models.DateTimeField(null=True, blank=True, help_text="When this module was unlocked")

    class Meta:
        unique_together = ['student', 'program_module']
        ordering = ['program_module__id']

    def __str__(self):
        return f"{self.student.username} - {self.program_module}"

    def calculate_progress(self):
        """Calculate progress based on completed topics and resources"""
        total_topics = self.program_module.topics.filter(is_active=True).count()
        if total_topics == 0:
            return 0

        # Calculate based on weekly resources completion
        total_resources = WeeklyResource.objects.filter(
            course__program_module=self.program_module,
            is_required=True
        ).count()

        if total_resources == 0:
            return 0

        completed_resources = WeekProgress.objects.filter(
            student=self.student,
            weekly_resource__course__program_module=self.program_module,
            is_completed=True
        ).count()

        progress = (completed_resources / total_resources) * 100
        self.progress_percentage = progress

        # Check if module should be marked as completed
        if progress >= self.program_module.minimum_completion_percentage:
            if not self.is_completed:
                self.is_completed = True
                self.completed_at = timezone.now()
                # Unlock next modules
                self._unlock_next_modules()

        self.save()
        return progress

    def _unlock_next_modules(self):
        """Unlock next modules when this one is completed"""
        from .utils import ProgressiveAccessManager
        ProgressiveAccessManager.unlock_next_modules(self.student, self.program_module)


# Discussion Models
class ModuleDiscussion(models.Model):
    """Discussion forum for each module"""
    program_module = models.OneToOneField(ProgramModule, on_delete=models.CASCADE, related_name='discussion')
    title = models.CharField(max_length=200, default="Module Discussion")
    description = models.TextField(blank=True, help_text="Description of what this discussion is about")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Module Discussion"
        verbose_name_plural = "Module Discussions"

    def __str__(self):
        return f"Discussion: {self.program_module}"

    @property
    def total_posts(self):
        return self.posts.count()

    @property
    def latest_post(self):
        return self.posts.order_by('-created_at').first()


class TopicDiscussion(models.Model):
    """Discussion forum for each topic"""
    topic = models.OneToOneField(ModuleTopic, on_delete=models.CASCADE, related_name='discussion')
    title = models.CharField(max_length=200, default="Topic Discussion")
    description = models.TextField(blank=True, help_text="Description of what this discussion is about")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Topic Discussion"
        verbose_name_plural = "Topic Discussions"

    def __str__(self):
        return f"Discussion: {self.topic.title}"

    @property
    def total_posts(self):
        return self.posts.count()

    @property
    def latest_post(self):
        return self.posts.order_by('-created_at').first()


class DiscussionPost(models.Model):
    """Individual posts in discussions"""
    # Either module or topic discussion (not both)
    module_discussion = models.ForeignKey(ModuleDiscussion, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    topic_discussion = models.ForeignKey(TopicDiscussion, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussion_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    attachment = models.FileField(upload_to='discussion_attachments/', blank=True, null=True)

    # Threading support
    parent_post = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)

    # Moderation
    is_pinned = models.BooleanField(default=False, help_text="Pin important posts to the top")
    is_locked = models.BooleanField(default=False, help_text="Lock post to prevent further replies")
    is_approved = models.BooleanField(default=True, help_text="Approve post for visibility")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        verbose_name = "Discussion Post"
        verbose_name_plural = "Discussion Posts"

    def __str__(self):
        return f"{self.author.username}: {self.title}"

    def save(self, *args, **kwargs):
        # Ensure only one discussion type is set
        if self.module_discussion and self.topic_discussion:
            raise ValueError("Post cannot belong to both module and topic discussions")
        if not self.module_discussion and not self.topic_discussion:
            raise ValueError("Post must belong to either module or topic discussion")
        super().save(*args, **kwargs)

    @property
    def is_reply(self):
        return self.parent_post is not None

    @property
    def reply_count(self):
        return self.replies.filter(is_approved=True).count()

    @property
    def discussion(self):
        return self.module_discussion or self.topic_discussion

    def can_edit(self, user):
        """Check if user can edit this post"""
        return user == self.author or user.is_staff

    def can_reply(self, user):
        """Check if user can reply to this post"""
        return not self.is_locked and self.is_approved


class DiscussionLike(models.Model):
    """Likes/reactions on discussion posts"""
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussion_likes')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['post', 'user']
        verbose_name = "Discussion Like"
        verbose_name_plural = "Discussion Likes"

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"


class DiscussionView(models.Model):
    """Track who has viewed which discussions"""
    # Either module or topic discussion
    module_discussion = models.ForeignKey(ModuleDiscussion, on_delete=models.CASCADE, related_name='views', null=True, blank=True)
    topic_discussion = models.ForeignKey(TopicDiscussion, on_delete=models.CASCADE, related_name='views', null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussion_views')
    last_viewed_at = models.DateTimeField(default=timezone.now)
    last_post_seen = models.ForeignKey(DiscussionPost, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = [
            ['module_discussion', 'user'],
            ['topic_discussion', 'user']
        ]
        verbose_name = "Discussion View"
        verbose_name_plural = "Discussion Views"

    def __str__(self):
        discussion = self.module_discussion or self.topic_discussion
        return f"{self.user.username} viewed {discussion}"



    last_viewed_at = models.DateTimeField(default=timezone.now)
    last_post_seen = models.ForeignKey(DiscussionPost, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = [
            ['module_discussion', 'user'],
            ['topic_discussion', 'user']
        ]
        verbose_name = "Discussion View"
        verbose_name_plural = "Discussion Views"

    def __str__(self):
        discussion = self.module_discussion or self.topic_discussion
        return f"{self.user.username} viewed {discussion}"

