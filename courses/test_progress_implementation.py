"""
Test script to verify the progress tracking implementation
Run this with: python manage.py shell < test_progress_implementation.py
"""

from django.contrib.auth.models import User
from courses.models import (
    ModuleProgress, LessonProgress, ResourceProgress, 
    AssignmentSubmission, Lesson, ModuleTopic, ProgramModule
)
from courses.progress_utils import ProgressCalculator
from programs.models import ProgramLevel
from students.models import StudentEnrollment

def test_progress_implementation():
    print("Testing Progress Implementation...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_student',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'Student'
        }
    )
    
    if created:
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    
    # Get a program level and module
    program_level = ProgramLevel.objects.filter(is_active=True).first()
    if not program_level:
        print("No active program level found. Please create one first.")
        return
    
    program_module = ProgramModule.objects.filter(
        program_level=program_level,
        is_active=True
    ).first()
    
    if not program_module:
        print("No active program module found. Please create one first.")
        return
    
    print(f"Testing with program level: {program_level.name}")
    print(f"Testing with program module: {program_module.module.name}")
    
    # Test 1: Create or get module progress
    print("\n1. Testing Module Progress Creation...")
    module_progress = ProgressCalculator.update_module_progress(user, program_module)
    print(f"Module progress created/updated: {module_progress.completion_percentage}%")
    print(f"Progress percentage: {module_progress.progress_percentage}%")
    print(f"Is completed: {module_progress.is_completed}")
    
    # Test 2: Test lesson progress calculation
    print("\n2. Testing Lesson Progress Calculation...")
    lessons = Lesson.objects.filter(
        topic__program_module=program_module,
        is_active=True
    )[:3]  # Test with first 3 lessons
    
    for lesson in lessons:
        lesson_progress = ProgressCalculator.update_lesson_progress(user, lesson)
        print(f"Lesson '{lesson.title}': {lesson_progress.completion_percentage}% complete")
    
    # Test 3: Test template snippet compatibility
    print("\n3. Testing Template Snippet Compatibility...")
    test_items = [
        {'completion_percentage': 0},
        {'completion_percentage': 25.5},
        {'completion_percentage': 50.0},
        {'completion_percentage': 75.3},
        {'completion_percentage': 100.0},
        {'completion_percentage': None},  # Test default
    ]
    
    for item in test_items:
        # Simulate the template snippet: {{ item.completion_percentage|default:0|floatformat:0 }}%
        percentage = item.get('completion_percentage', 0) or 0
        formatted = f"{percentage:.0f}%"
        print(f"Template snippet result: {formatted}")
    
    # Test 4: Test progress display helper
    print("\n4. Testing Progress Display Helper...")
    from courses.progress_utils import ProgressDisplayHelper
    
    test_percentages = [0, 25, 50, 75, 100]
    for pct in test_percentages:
        color = ProgressDisplayHelper.get_progress_color(pct)
        css_class = ProgressDisplayHelper.get_progress_display_class(pct)
        formatted = ProgressDisplayHelper.format_progress_percentage(pct)
        print(f"{pct}% -> Color: {color}, Class: {css_class}, Formatted: {formatted}")
    
    # Test 5: Test recalculation
    print("\n5. Testing Progress Recalculation...")
    result = ProgressCalculator.recalculate_all_progress(user, program_level)
    print(f"Recalculation result: {result}")
    
    print("\n✅ Progress implementation test completed successfully!")
    print("\nTemplate snippet usage:")
    print("Progress: {{ item.completion_percentage|default:0|floatformat:0 }}%")
    print("\nThis will display progress percentages consistently across all templates.")

if __name__ == "__main__":
    test_progress_implementation()
