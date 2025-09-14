from django.core.management.base import BaseCommand
from courses.models import ProgramLevel, Module, ProgramModule

class Command(BaseCommand):
    help = 'Create sample program levels and modules for the Global Coaches Program'

    def handle(self, *args, **options):
        self.stdout.write('Creating Global Coaches Program structure...')
        
        # Create Program Levels
        certificate_level, created = ProgramLevel.objects.get_or_create(
            level_type='certificate',
            defaults={
                'name': 'Certificate Level',
                'description': 'Provides a strong foundation in all core areas (faith, leadership, SDGs, education, climate, diplomacy, entrepreneurship). Every participant graduates as a well-rounded coach with exposure to all modules.',
                'duration_months': 6,
                'credits_required': 18,
                'prerequisites': 'Basic education and commitment to leadership development'
            }
        )
        
        diploma_level, created = ProgramLevel.objects.get_or_create(
            level_type='diploma',
            defaults={
                'name': 'Diploma Level',
                'description': 'Focuses on deeper practice, applied coaching, and community-based projects. Coaches engage in real projects that combine multiple disciplines and demonstrate measurable impact.',
                'duration_months': 12,
                'credits_required': 36,
                'prerequisites': 'Certificate Level completion or equivalent experience'
            }
        )
        
        advanced_diploma_level, created = ProgramLevel.objects.get_or_create(
            level_type='advanced_diploma',
            defaults={
                'name': 'Advanced Diploma Level',
                'description': 'Coaches step into leadership, mentorship, and multiplication roles. Participants refine their specialization while remaining grounded in the holistic Global Coaches framework.',
                'duration_months': 12,
                'credits_required': 48,
                'prerequisites': 'Diploma Level completion and demonstrated leadership experience'
            }
        )
        
        self.stdout.write(f'Created program levels: {certificate_level.name}, {diploma_level.name}, {advanced_diploma_level.name}')
        
        # Create Modules
        modules_data = [
            {
                'module_type': 'young_theologians',
                'name': 'Module 1: Young Theologians and Gospel Advancing',
                'description': 'Building a strong theological foundation and developing skills in gospel advancement and spiritual leadership.',
                'learning_objectives': 'Understand core theological principles, develop gospel advancement strategies, and build spiritual leadership capacity.'
            },
            {
                'module_type': 'missional_leadership',
                'name': 'Module 2: Missional Leadership',
                'description': 'Developing missional leadership skills for community transformation and sustainable impact.',
                'learning_objectives': 'Master missional leadership principles, develop community engagement strategies, and build sustainable leadership practices.'
            },
            {
                'module_type': 'sdgs_community',
                'name': 'Module 3: SDGs & Community Transformation',
                'description': 'Understanding and implementing Sustainable Development Goals for community transformation.',
                'learning_objectives': 'Understand SDGs framework, develop community transformation strategies, and implement sustainable development practices.'
            },
            {
                'module_type': 'education_sustainable',
                'name': 'Module 4: Education for Sustainable Development & Global Citizenship',
                'description': 'Promoting education for sustainable development and fostering global citizenship.',
                'learning_objectives': 'Design sustainable education programs, promote global citizenship, and develop educational leadership skills.'
            },
            {
                'module_type': 'entrepreneurship',
                'name': 'Module 5: Entrepreneurship and Political Economics',
                'description': 'Developing entrepreneurial skills and understanding political economics for social impact.',
                'learning_objectives': 'Master entrepreneurial principles, understand political economics, and develop social impact ventures.'
            },
            {
                'module_type': 'diplomacy_leadership',
                'name': 'Module 6: Diplomacy & Global Leadership',
                'description': 'Building diplomatic skills and global leadership capacity for international impact.',
                'learning_objectives': 'Develop diplomatic skills, build global leadership capacity, and foster international collaboration.'
            },
            {
                'module_type': 'climate_warriors',
                'name': 'Module 7: Climate Warriors',
                'description': 'Environmental leadership and climate action for sustainable future.',
                'learning_objectives': 'Understand climate science, develop environmental leadership skills, and implement climate action strategies.'
            }
        ]
        
        created_modules = []
        for module_data in modules_data:
            module, created = Module.objects.get_or_create(
                module_type=module_data['module_type'],
                defaults=module_data
            )
            created_modules.append(module)
            self.stdout.write(f'Created module: {module.name}')
        
        # Create Program Modules (linking levels with modules at different depths)
        program_modules_data = [
            # Certificate Level - Foundation depth
            (certificate_level, created_modules[0], 1, 'Foundation level understanding of theological principles and gospel advancement.', 'Basic theological knowledge assessment and gospel advancement project.'),
            (certificate_level, created_modules[1], 1, 'Foundation level missional leadership principles and basic community engagement.', 'Leadership assessment and community engagement project.'),
            (certificate_level, created_modules[2], 1, 'Foundation level understanding of SDGs and basic community transformation.', 'SDGs knowledge assessment and community project.'),
            (certificate_level, created_modules[3], 1, 'Foundation level education for sustainable development principles.', 'Educational program design and global citizenship project.'),
            (certificate_level, created_modules[4], 1, 'Foundation level entrepreneurship and political economics understanding.', 'Business plan development and economic analysis project.'),
            (certificate_level, created_modules[5], 1, 'Foundation level diplomatic skills and global leadership principles.', 'Diplomatic simulation and global leadership assessment.'),
            (certificate_level, created_modules[6], 1, 'Foundation level climate science and environmental leadership.', 'Climate action project and environmental assessment.'),
            
            # Diploma Level - Practice depth
            (diploma_level, created_modules[0], 2, 'Advanced theological application and gospel advancement in diverse contexts.', 'Advanced theological project and gospel advancement implementation.'),
            (diploma_level, created_modules[1], 2, 'Advanced missional leadership practice and community transformation projects.', 'Community transformation project and leadership assessment.'),
            (diploma_level, created_modules[2], 2, 'Advanced SDGs implementation and community transformation leadership.', 'SDGs implementation project and community impact assessment.'),
            (diploma_level, created_modules[3], 2, 'Advanced education for sustainable development and global citizenship programs.', 'Educational program implementation and global citizenship project.'),
            (diploma_level, created_modules[4], 2, 'Advanced entrepreneurship and political economics application.', 'Social enterprise development and economic impact project.'),
            (diploma_level, created_modules[5], 2, 'Advanced diplomatic practice and global leadership implementation.', 'Diplomatic project and global leadership initiative.'),
            (diploma_level, created_modules[6], 2, 'Advanced climate action and environmental leadership implementation.', 'Climate action initiative and environmental impact project.'),
            
            # Advanced Diploma Level - Leadership depth
            (advanced_diploma_level, created_modules[0], 3, 'Theological leadership and gospel advancement multiplication.', 'Theological leadership project and gospel advancement multiplication.'),
            (advanced_diploma_level, created_modules[1], 3, 'Missional leadership multiplication and community transformation leadership.', 'Leadership multiplication project and community transformation leadership.'),
            (advanced_diploma_level, created_modules[2], 3, 'SDGs leadership and community transformation multiplication.', 'SDGs leadership initiative and community transformation multiplication.'),
            (advanced_diploma_level, created_modules[3], 3, 'Educational leadership and global citizenship multiplication.', 'Educational leadership project and global citizenship multiplication.'),
            (advanced_diploma_level, created_modules[4], 3, 'Entrepreneurial leadership and economic impact multiplication.', 'Entrepreneurial leadership project and economic impact multiplication.'),
            (advanced_diploma_level, created_modules[5], 3, 'Diplomatic leadership and global impact multiplication.', 'Diplomatic leadership project and global impact multiplication.'),
            (advanced_diploma_level, created_modules[6], 3, 'Environmental leadership and climate action multiplication.', 'Environmental leadership project and climate action multiplication.'),
        ]
        
        for level, module, depth, outcomes, assessment in program_modules_data:
            program_module, created = ProgramModule.objects.get_or_create(
                program_level=level,
                module=module,
                defaults={
                    'depth_level': depth,
                    'learning_outcomes': outcomes,
                    'assessment_criteria': assessment
                }
            )
            if created:
                self.stdout.write(f'Created program module: {level.name} - {module.name} (Depth: {depth})')
        
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created Global Coaches Program structure with 3 levels and 7 modules!'
            )
        )
