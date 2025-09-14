"""
Management command to set up progressive module structure
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.models import ProgramLevel, Module, ProgramModule, ModuleProgress
from courses.utils import ProgressiveAccessManager
from students.models import StudentEnrollment
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Set up progressive module structure with proper sequencing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all module progress and start fresh',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up progressive module structure...'))

        if options['reset']:
            self.stdout.write('Resetting all module progress...')
            ModuleProgress.objects.all().delete()

        # Set up sequence order for modules based on their logical progression
        self.setup_module_sequences()
        
        # Set up prerequisites
        self.setup_module_prerequisites()
        
        # Initialize progress for existing students
        self.initialize_existing_students()
        
        self.stdout.write(self.style.SUCCESS('Progressive module structure setup complete!'))

    def setup_module_sequences(self):
        """Set up logical sequence order for modules"""
        self.stdout.write('Setting up module sequences...')
        
        # Define the logical progression order for modules
        module_sequences = {
            'young_theologians': 1,  # Foundation - spiritual grounding
            'missional_leadership': 2,  # Leadership basics
            'sdgs_community': 3,  # Community understanding
            'education_sustainable': 4,  # Educational foundation
            'entrepreneurship': 5,  # Economic understanding
            'diplomacy_leadership': 6,  # Advanced leadership
            'climate_warriors': 7,  # Specialized application
        }

        for program_level in ProgramLevel.objects.filter(is_active=True):
            self.stdout.write(f'  Setting up sequences for {program_level.name}...')
            
            for module_type, sequence in module_sequences.items():
                try:
                    module = Module.objects.get(module_type=module_type, is_active=True)
                    program_module, created = ProgramModule.objects.get_or_create(
                        program_level=program_level,
                        module=module,
                        defaults={
                            'depth_level': self.get_depth_level(program_level),
                            'learning_outcomes': f'Learning outcomes for {module.name} at {program_level.name} level',
                            'assessment_criteria': f'Assessment criteria for {module.name}',
                            'sequence_order': sequence,
                            'minimum_completion_percentage': 80,
                        }
                    )
                    
                    if not created:
                        program_module.sequence_order = sequence
                        program_module.minimum_completion_percentage = 80
                        program_module.save()
                    
                    self.stdout.write(f'    {module.name}: Sequence {sequence}')
                    
                except Module.DoesNotExist:
                    self.stdout.write(f'    Warning: Module {module_type} not found')

    def get_depth_level(self, program_level):
        """Get depth level based on program level"""
        level_mapping = {
            'certificate': 1,
            'diploma': 2,
            'advanced_diploma': 3,
        }
        return level_mapping.get(program_level.level_type, 1)

    def setup_module_prerequisites(self):
        """Set up prerequisite relationships between modules"""
        self.stdout.write('Setting up module prerequisites...')
        
        # Define prerequisite relationships
        prerequisites = {
            'missional_leadership': ['young_theologians'],
            'sdgs_community': ['young_theologians', 'missional_leadership'],
            'education_sustainable': ['sdgs_community'],
            'entrepreneurship': ['sdgs_community'],
            'diplomacy_leadership': ['missional_leadership', 'education_sustainable'],
            'climate_warriors': ['sdgs_community', 'education_sustainable'],
        }

        for program_level in ProgramLevel.objects.filter(is_active=True):
            self.stdout.write(f'  Setting prerequisites for {program_level.name}...')
            
            for module_type, prereq_types in prerequisites.items():
                try:
                    module = Module.objects.get(module_type=module_type, is_active=True)
                    program_module = ProgramModule.objects.get(
                        program_level=program_level,
                        module=module
                    )
                    
                    # Clear existing prerequisites
                    program_module.prerequisites.clear()
                    
                    # Add new prerequisites
                    for prereq_type in prereq_types:
                        try:
                            prereq_module = Module.objects.get(module_type=prereq_type, is_active=True)
                            prereq_program_module = ProgramModule.objects.get(
                                program_level=program_level,
                                module=prereq_module
                            )
                            program_module.prerequisites.add(prereq_program_module)
                            self.stdout.write(f'    {module.name} requires {prereq_module.name}')
                        except (Module.DoesNotExist, ProgramModule.DoesNotExist):
                            self.stdout.write(f'    Warning: Prerequisite {prereq_type} not found')
                    
                except (Module.DoesNotExist, ProgramModule.DoesNotExist):
                    self.stdout.write(f'    Warning: Module {module_type} not found')

    def initialize_existing_students(self):
        """Initialize progressive access for existing students"""
        self.stdout.write('Initializing progress for existing students...')
        
        active_enrollments = StudentEnrollment.objects.filter(status='active')
        
        for enrollment in active_enrollments:
            self.stdout.write(f'  Initializing {enrollment.student.username}...')
            result = ProgressiveAccessManager.initialize_student_progress(enrollment.student)
            self.stdout.write(f'    {result}')
            
            # Calculate progress for any existing module progress
            existing_progress = ModuleProgress.objects.filter(student=enrollment.student)
            for progress in existing_progress:
                progress.calculate_progress()
                self.stdout.write(f'    Updated progress for {progress.program_module.module.name}: {progress.progress_percentage}%')

        self.stdout.write(f'Initialized progress for {active_enrollments.count()} students')
