from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class FAQ(models.Model):
    """Frequently Asked Questions"""
    CATEGORY_CHOICES = [
        ('registration', 'Registration'),
        ('login', 'Login & Access'),
        ('assignments', 'Assignments'),
        ('mentorship', 'Mentorship'),
        ('certificates', 'Certificates'),
        ('technical', 'Technical Support'),
        ('general', 'General'),
    ]
    
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0, help_text="Display order within category")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['category', 'order', 'question']

    def __str__(self):
        return self.question

class Feedback(models.Model):
    """User feedback and suggestions"""
    FEEDBACK_TYPES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('improvement', 'Improvement Suggestion'),
        ('compliment', 'Compliment'),
        ('complaint', 'Complaint'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback', blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, help_text="For anonymous feedback")
    email = models.EmailField(blank=True, help_text="For anonymous feedback")
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='other')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    attachment = models.FileField(upload_to='feedback_attachments/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=10, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    submitted_at = models.DateTimeField(default=timezone.now)
    response = models.TextField(blank=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback_responses')

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.feedback_type}: {self.subject}"

class SupportTicket(models.Model):
    """Support tickets for student assistance"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_response', 'Waiting for Response'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    ticket_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=FAQ.CATEGORY_CHOICES, default='general')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.ticket_number}: {self.subject}"

class SupportTicketResponse(models.Model):
    """Responses to support tickets"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to='ticket_attachments/', blank=True, null=True)
    is_staff_response = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Response to Ticket #{self.ticket.ticket_number}"

class ContactInfo(models.Model):
    """Contact information and emergency support"""
    contact_type = models.CharField(max_length=50, choices=[
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('whatsapp', 'WhatsApp'),
        ('address', 'Physical Address'),
    ])
    label = models.CharField(max_length=100, help_text="e.g., 'General Inquiries', 'Emergency Support'")
    value = models.CharField(max_length=200, help_text="Email, phone number, or address")
    description = models.TextField(blank=True)
    is_emergency = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'contact_type']

    def __str__(self):
        return f"{self.label}: {self.value}"

