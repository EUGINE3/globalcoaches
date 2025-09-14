from django.db import models
from django.utils import timezone

class ProgramLevel(models.Model):
    """The 3-tier training pathway levels"""
    LEVEL_CHOICES = [
        ('certificate', 'Certificate Level'),
        ('diploma', 'Diploma Level'),
        ('advanced_diploma', 'Advanced Diploma Level'),
    ]
    
    name = models.CharField(max_length=100)
    level_type = models.CharField(max_length=20, choices=LEVEL_CHOICES, unique=True)
    description = models.TextField()
    duration_months = models.IntegerField()
    focus_areas = models.TextField(help_text="Key focus areas for this level")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

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
    learning_objectives = models.TextField(help_text="Key learning objectives")
    image = models.ImageField(upload_to='module_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Modules"
    
    def __str__(self):
        return self.name

class ProgramModule(models.Model):
    """Modules offered at different program levels with varying depth"""
    program_level = models.ForeignKey(ProgramLevel, on_delete=models.CASCADE, related_name='modules')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='programs')
    depth_level = models.CharField(max_length=20, choices=[
        ('foundational', 'Foundational'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ])
    credits = models.IntegerField()
    description = models.TextField(help_text="How this module is taught at this level")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['program_level', 'module']
    
    def __str__(self):
        return f"{self.program_level.name} - {self.module.name} ({self.depth_level})"

