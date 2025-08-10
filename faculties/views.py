from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Faculty, AcademicLevel, FacultyProgram
from students.models import StudentEnrollment

def faculty_overview(request):
    """Display overview of all faculties"""
    faculties = Faculty.objects.all()
    return render(request, 'faculties/faculty_overview.html', {'faculties': faculties})

def faculty_detail(request, faculty_id):
    """Display detailed view of a specific faculty"""
    faculty = get_object_or_404(Faculty, id=faculty_id)
    return render(request, 'faculties/faculty_detail.html', {
        'faculty': faculty,
        'faculty_id': faculty_id
    })

@login_required
def apply_to_faculty(request, faculty_id):
    """Handle faculty application"""
    faculty = get_object_or_404(Faculty, id=faculty_id)
    
    if request.method == 'POST':
        # Get form data
        program_level = request.POST.get('program_level')
        personal_statement = request.POST.get('personal_statement')
        goals_objectives = request.POST.get('goals_objectives')
        previous_experience = request.POST.get('previous_experience')
        commitment = request.POST.get('commitment')
        
        # Validate required fields
        if not all([program_level, personal_statement, goals_objectives, commitment]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'faculties/apply_to_faculty.html', {'faculty': faculty})
        
        try:
            # Get the academic level
            academic_level = AcademicLevel.objects.get(level_type=program_level)
            
            # Get or create the faculty program
            faculty_program, created = FacultyProgram.objects.get_or_create(
                faculty=faculty,
                academic_level=academic_level,
                defaults={
                    'program_structure': f'Program structure for {faculty.name} - {academic_level.name}',
                    'is_active': True
                }
            )
            
            # Check if student is already enrolled
            existing_enrollment = StudentEnrollment.objects.filter(
                student=request.user,
                faculty_program=faculty_program
            ).first()
            
            if existing_enrollment:
                messages.warning(request, 'You have already applied to this program.')
                return redirect('faculties:faculty_detail', faculty_id=faculty_id)
            
            # Create the enrollment
            enrollment = StudentEnrollment.objects.create(
                student=request.user,
                faculty_program=faculty_program,
                status='pending',
                notes=f"Personal Statement: {personal_statement}\nGoals: {goals_objectives}\nExperience: {previous_experience}"
            )
            
            messages.success(request, f'Your application to {faculty.name} has been submitted successfully!')
            return redirect('faculties:faculty_detail', faculty_id=faculty_id)
            
        except AcademicLevel.DoesNotExist:
            messages.error(request, 'Invalid program level selected.')
        except Exception as e:
            messages.error(request, f'An error occurred while submitting your application: {str(e)}')
    
    return render(request, 'faculties/apply_to_faculty.html', {'faculty': faculty})

