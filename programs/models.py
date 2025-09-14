from django.db import models
from django.utils import timezone


class ProgramLevel(models.Model):
    """The 3-tier training pathway levels for the Global Coaches Program"""
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
    
    class Meta:
        verbose_name = "Program Level"
        verbose_name_plural = "Program Levels"
        ordering = ['id']
    
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
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        ordering = ['id']

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
    sequence_order = models.IntegerField(default=1)
    minimum_completion_percentage = models.FloatField(default=80.0, help_text="Minimum percentage required to complete this module")
    
    
    class Meta:
        unique_together = ['program_level', 'module']
        verbose_name = "Program Module"
        verbose_name_plural = "Program Modules"
    
    def __str__(self):
        return f"{self.program_level.name} - {self.module.name} ({self.depth_level})"

    def get_prerequisite_status(self, student):
        """Get the prerequisite status for this module for a given student"""
        # For now, we'll use sequence_order as the main prerequisite logic
        # A module is accessible if:
        # 1. It's the first module (sequence_order = 1), OR
        # 2. All previous modules in sequence are completed

        if self.sequence_order == 1:
            return {
                'met': True,
                'message': 'First module - no prerequisites',
                'missing_prerequisites': []
            }

        # Check if previous modules are completed
        from courses.models import ModuleProgress
        previous_modules = ProgramModule.objects.filter(
            program_level=self.program_level,
            sequence_order__lt=self.sequence_order,
            is_active=True
        ).order_by('sequence_order')

        missing_prerequisites = []
        for prev_module in previous_modules:
            progress = ModuleProgress.objects.filter(
                student=student,
                program_module=prev_module
            ).first()

            if not progress or not progress.is_completed:
                missing_prerequisites.append(prev_module)

        if missing_prerequisites:
            return {
                'met': False,
                'message': f'Complete {len(missing_prerequisites)} prerequisite module(s)',
                'missing_prerequisites': missing_prerequisites
            }

        return {
            'met': True,
            'message': 'All prerequisites completed',
            'missing_prerequisites': []
        }
