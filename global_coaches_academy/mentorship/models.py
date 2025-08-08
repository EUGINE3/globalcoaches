from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from students.models import StudentEnrollment

class MentorProfile(models.Model):
    """Extended profile for mentors"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    expertise_areas = models.TextField(help_text="Areas of expertise and specialization")
    years_experience = models.IntegerField()
    max_mentees = models.IntegerField(default=5)
    current_mentees_count = models.IntegerField(default=0)
    bio = models.TextField()
    linkedin_profile = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Mentor: {self.user.get_full_name() or self.user.username}"

    def can_take_more_mentees(self):
        return self.current_mentees_count < self.max_mentees

class MentorshipPairing(models.Model):
    """Mentor-student pairing records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
    ]
    
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='mentorships')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorships')
    enrollment = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE, related_name='mentorships')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paired_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    pairing_method = models.CharField(max_length=20, choices=[('auto', 'Automatic'), ('manual', 'Manual')], default='auto')
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['mentor', 'student', 'enrollment']

    def __str__(self):
        return f"{self.mentor.user.username} mentoring {self.student.username}"

class MentorshipMessage(models.Model):
    """Messages between mentors and students"""
    pairing = models.ForeignKey(MentorshipPairing, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    attachment = models.FileField(upload_to='mentorship_messages/', blank=True, null=True)
    sent_at = models.DateTimeField(default=timezone.now)
    read_at = models.DateTimeField(blank=True, null=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.sender.username}: {self.subject}"

class WeeklyCheckin(models.Model):
    """Weekly check-in submissions from students"""
    pairing = models.ForeignKey(MentorshipPairing, on_delete=models.CASCADE, related_name='checkins')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    week_ending = models.DateField()
    progress_summary = models.TextField(help_text="What did you accomplish this week?")
    challenges_faced = models.TextField(help_text="What challenges did you face?")
    goals_next_week = models.TextField(help_text="What are your goals for next week?")
    mentor_support_needed = models.TextField(blank=True, help_text="What support do you need from your mentor?")
    mood_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Rate your mood (1-5)")
    submitted_at = models.DateTimeField(default=timezone.now)
    mentor_response = models.TextField(blank=True)
    mentor_responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['pairing', 'week_ending']
        ordering = ['-week_ending']

    def __str__(self):
        return f"{self.student.username} - Week ending {self.week_ending}"

class PeerReview(models.Model):
    """Peer reviews for assignments"""
    assignment_submission = models.ForeignKey('courses.AssignmentSubmission', on_delete=models.CASCADE, related_name='peer_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='peer_reviews_given')
    content_quality = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Rate content quality (1-5)")
    creativity = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Rate creativity (1-5)")
    presentation = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Rate presentation (1-5)")
    feedback = models.TextField(help_text="Constructive feedback")
    suggestions = models.TextField(blank=True, help_text="Suggestions for improvement")
    submitted_at = models.DateTimeField(default=timezone.now)
    is_anonymous = models.BooleanField(default=True)

    class Meta:
        unique_together = ['assignment_submission', 'reviewer']

    def __str__(self):
        return f"Peer review by {self.reviewer.username}"

    @property
    def average_rating(self):
        return (self.content_quality + self.creativity + self.presentation) / 3

