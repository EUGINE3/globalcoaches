from django.db import models
from django.utils import timezone

class Faculty(models.Model):
    """The 7 core faculties of Global Coaches Academy"""
    FACULTY_CHOICES = [
        ('church_theological', 'Church & Theological Education and Transformation'),
        ('missional_leadership', 'Missional Leadership'),
        ('sdgs_community', 'SDGs & Community Transformation'),
        ('education_sustainable', 'Education for Sustainable Development & Global Citizenship'),
        ('global_leadership', 'Global Leadership & Diplomacy'),
        ('entrepreneurship', 'Entrepreneurship & Political Economics'),
        ('climate_warriors', 'Climate Warriors (Environmental Leadership & Action)'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    faculty_type = models.CharField(max_length=50, choices=FACULTY_CHOICES, unique=True)
    description = models.TextField()
    pillar_focus = models.TextField(help_text="Main pillar and value focus")
    image = models.ImageField(upload_to='faculty_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Faculties"

    def __str__(self):
        return self.name

class AcademicLevel(models.Model):
    """Academic levels: Masterclass, Diploma, Higher Diploma"""
    LEVEL_CHOICES = [
        ('masterclass', 'Masterclass (6 months)'),
        ('diploma', 'Diploma (12 months)'),
        ('higher_diploma', 'Higher Diploma (12 months)'),
    ]
    
    name = models.CharField(max_length=100)
    level_type = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    duration_months = models.IntegerField()
    credits_required = models.IntegerField()
    description = models.TextField()
    prerequisites = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.duration_months} months)"

class FacultyProgram(models.Model):
    """Programs offered by each faculty at different academic levels"""
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='programs')
    academic_level = models.ForeignKey(AcademicLevel, on_delete=models.CASCADE)
    program_structure = models.TextField(help_text="Detailed program structure")
    table_of_contents = models.FileField(upload_to='program_toc/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['faculty', 'academic_level']
    
    def __str__(self):
        return f"{self.faculty.name} - {self.academic_level.name}"

