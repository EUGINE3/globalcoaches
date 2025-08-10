from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faculties.models import Faculty, AcademicLevel, FacultyProgram


class Command(BaseCommand):
    help = 'Create sample faculty data for Global Coaches Academy'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample faculty data...')
        
        # Create Academic Levels
        masterclass = AcademicLevel.objects.create(
            name='Masterclass',
            level_type='masterclass',
            duration_months=6,
            credits_required=12,
            description='Intensive 6-month program focusing on core competencies and practical application.',
            prerequisites='Basic understanding of leadership principles and commitment to personal growth.'
        )
        
        diploma = AcademicLevel.objects.create(
            name='Diploma',
            level_type='diploma',
            duration_months=12,
            credits_required=24,
            description='Comprehensive 12-month program with in-depth study and mentorship.',
            prerequisites='Completed Masterclass or equivalent experience in leadership.'
        )
        
        higher_diploma = AcademicLevel.objects.create(
            name='Higher Diploma',
            level_type='higher_diploma',
            duration_months=12,
            credits_required=36,
            description='Advanced 12-month program with research components and specialized focus.',
            prerequisites='Completed Diploma or significant leadership experience.'
        )
        
        # Create Faculties
        faculties_data = [
            {
                'name': 'Church & Theological Education and Transformation',
                'faculty_type': 'church_theological',
                'description': 'Transform church leadership through theological education and community engagement. This faculty equips leaders with biblical wisdom, theological understanding, and practical skills for church transformation and community development.',
                'pillar_focus': 'Spiritual leadership, theological education, community transformation, pastoral care, and church administration.'
            },
            {
                'name': 'Missional Leadership',
                'faculty_type': 'missional_leadership',
                'description': 'Develop missional leaders who can effectively serve and transform communities through strategic leadership and cultural engagement.',
                'pillar_focus': 'Mission strategy, cross-cultural leadership, community development, evangelism, and discipleship.'
            },
            {
                'name': 'SDGs & Community Transformation',
                'faculty_type': 'sdgs_community',
                'description': 'Address global challenges through sustainable development goals and community transformation initiatives.',
                'pillar_focus': 'Sustainable development, community engagement, social justice, poverty alleviation, and environmental stewardship.'
            },
            {
                'name': 'Education for Sustainable Development & Global Citizenship',
                'faculty_type': 'education_sustainable',
                'description': 'Prepare educators and leaders to promote sustainable development and global citizenship through innovative educational approaches.',
                'pillar_focus': 'Educational leadership, sustainable development education, global citizenship, curriculum development, and pedagogical innovation.'
            },
            {
                'name': 'Global Leadership & Diplomacy',
                'faculty_type': 'global_leadership',
                'description': 'Develop global leaders with diplomatic skills to address international challenges and promote cross-cultural understanding.',
                'pillar_focus': 'International relations, diplomatic skills, global governance, cultural intelligence, and strategic leadership.'
            },
            {
                'name': 'Entrepreneurship & Political Economics',
                'faculty_type': 'entrepreneurship',
                'description': 'Foster entrepreneurial leadership and political economic understanding for sustainable business and community development.',
                'pillar_focus': 'Entrepreneurial leadership, economic development, political economy, business strategy, and social entrepreneurship.'
            },
            {
                'name': 'Climate Warriors (Environmental Leadership & Action)',
                'faculty_type': 'climate_warriors',
                'description': 'Empower environmental leaders to address climate change and promote sustainable environmental practices.',
                'pillar_focus': 'Environmental leadership, climate action, sustainability, conservation, and green innovation.'
            }
        ]
        
        faculties = []
        for data in faculties_data:
            faculty = Faculty.objects.create(
                name=data['name'],
                slug=slugify(data['name']),
                faculty_type=data['faculty_type'],
                description=data['description'],
                pillar_focus=data['pillar_focus'],
                is_active=True
            )
            faculties.append(faculty)
            self.stdout.write(f'Created faculty: {faculty.name}')
        
        # Create Faculty Programs
        for faculty in faculties:
            # Masterclass program
            FacultyProgram.objects.create(
                faculty=faculty,
                academic_level=masterclass,
                program_structure=f"""
                Month 1-2: Foundation & Core Principles
                - Introduction to {faculty.name}
                - Leadership fundamentals
                - Core competencies development
                
                Month 3-4: Specialized Training
                - Advanced concepts in {faculty.name.lower()}
                - Practical applications
                - Case studies and real-world projects
                
                Month 5-6: Implementation & Capstone
                - Project implementation
                - Mentorship and guidance
                - Final assessment and certification
                """,
                is_active=True
            )
            
            # Diploma program
            FacultyProgram.objects.create(
                faculty=faculty,
                academic_level=diploma,
                program_structure=f"""
                Year 1: Comprehensive Study
                - Advanced theoretical foundations
                - Specialized coursework in {faculty.name.lower()}
                - Research methodology
                - Mentorship and leadership development
                - Community engagement projects
                - International collaboration opportunities
                """,
                is_active=True
            )
            
            # Higher Diploma program
            FacultyProgram.objects.create(
                faculty=faculty,
                academic_level=higher_diploma,
                program_structure=f"""
                Advanced Research & Leadership
                - Specialized research in {faculty.name.lower()}
                - Advanced leadership development
                - International partnerships
                - Policy development and implementation
                - Capstone research project
                - Global impact initiatives
                """,
                is_active=True
            )
            
            self.stdout.write(f'Created programs for: {faculty.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(faculties)} faculties with {len(faculties) * 3} programs each!'
            )
        ) 