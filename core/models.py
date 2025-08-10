from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    """Extended user profile for Global Coaches Academy"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_mentor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Profile"

class Partner(models.Model):
    """Partner organizations like ICY Africa, Africa for SDGs, LADA"""
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='partner_logos/')
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Testimonial(models.Model):
    """Testimonials from graduates, mentors, or founders"""
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)  # Graduate, Mentor, Founder
    content = models.TextField()
    photo = models.ImageField(upload_to='testimonial_photos/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.role}"

