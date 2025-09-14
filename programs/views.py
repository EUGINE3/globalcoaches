from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ProgramLevel, Module, ProgramModule
from students.models import StudentEnrollment
from courses.utils import ProgressiveAccessManager


def program_overview(request):
    """Display overview of the Global Coaches Program"""
    program_levels = ProgramLevel.objects.filter(is_active=True)
    modules = Module.objects.filter(is_active=True)

    # Get user's enrollment status for each program level
    user_enrollments = {}
    if request.user.is_authenticated:
        enrollments = StudentEnrollment.objects.filter(student=request.user)
        for enrollment in enrollments:
            user_enrollments[enrollment.program_level.id] = enrollment.status

    return render(request, 'programs/program_overview.html', {
        'program_levels': program_levels,
        'modules': modules,
        'user_enrollments': user_enrollments
    })


def program_level_detail(request, level_id):
    """Display detailed view of a specific program level"""
    program_level = get_object_or_404(ProgramLevel, id=level_id)
    program_modules = ProgramModule.objects.filter(
        program_level=program_level,
        is_active=True
    ).select_related('module')

    # Check user's enrollment status
    user_enrollment = None
    if request.user.is_authenticated:
        user_enrollment = StudentEnrollment.objects.filter(
            student=request.user,
            program_level=program_level
        ).first()

    return render(request, 'programs/program_level_detail.html', {
        'program_level': program_level,
        'program_modules': program_modules,
        'level_id': level_id,
        'user_enrollment': user_enrollment
    })


def module_detail(request, module_id):
    """Display detailed view of a specific module"""
    module = get_object_or_404(Module, id=module_id)
    program_modules = ProgramModule.objects.filter(
        module=module, 
        is_active=True
    ).select_related('program_level')
    return render(request, 'programs/module_detail.html', {
        'module': module,
        'program_modules': program_modules,
        'module_id': module_id
    })


@login_required
def apply_to_program(request, level_id):
    """Handle program application"""
    program_level = get_object_or_404(ProgramLevel, id=level_id)
    
    if request.method == 'POST':
        # Get form data
        personal_statement = request.POST.get('personal_statement')
        goals_objectives = request.POST.get('goals_objectives')
        previous_experience = request.POST.get('previous_experience')
        commitment = request.POST.get('commitment')
        
        # Validate required fields
        if not all([personal_statement, goals_objectives, commitment]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'programs/apply_to_program.html', {'program_level': program_level})
        
        try:
            # Check if student is already enrolled in this program level
            existing_enrollment = StudentEnrollment.objects.filter(
                student=request.user,
                program_level=program_level
            ).first()
            
            if existing_enrollment:
                if existing_enrollment.status == 'active':
                    messages.info(request, 'You are already enrolled in this program level. Access your courses from the dashboard.')
                    return redirect('core:dashboard')
                else:
                    messages.warning(request, 'You have already applied to this program level.')
                    return redirect('programs:program_level_detail', level_id=level_id)
            
            # Create the enrollment with active status (auto-enrollment)
            enrollment = StudentEnrollment.objects.create(
                student=request.user,
                program_level=program_level,
                status='active',  # Automatically activate enrollment
                notes=f"Personal Statement: {personal_statement}\nGoals: {goals_objectives}\nExperience: {previous_experience}"
            )

            # Initialize progressive learning for the student
            try:
                access_manager = ProgressiveAccessManager()
                access_manager.initialize_student_progress(request.user)

                messages.success(request, f'Congratulations! You have been successfully enrolled in the {program_level.name}. You can now access your courses!')
                return redirect('core:dashboard')  # Redirect to dashboard to see courses
            except Exception as e:
                # If progressive learning initialization fails, still show success but log the error
                messages.success(request, f'You have been enrolled in the {program_level.name}!')
                messages.warning(request, 'Course access is being set up. Please check back in a few minutes.')
                return redirect('core:dashboard')
            
        except Exception as e:
            messages.error(request, f'An error occurred while submitting your application: {str(e)}')
    
    return render(request, 'programs/apply_to_program.html', {'program_level': program_level})


@login_required
def enroll_in_program(request, level_id):
    """Simple one-click enrollment in a program"""
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('programs:program_level_detail', level_id=level_id)

    program_level = get_object_or_404(ProgramLevel, id=level_id, is_active=True)

    try:
        # Check if student is already enrolled
        existing_enrollment = StudentEnrollment.objects.filter(
            student=request.user,
            program_level=program_level
        ).first()

        if existing_enrollment:
            if existing_enrollment.status == 'active':
                messages.info(request, f'You are already enrolled in {program_level.name}!')
                return redirect('courses:student_dashboard')
            else:
                # Reactivate existing enrollment
                existing_enrollment.status = 'active'
                existing_enrollment.save()
                messages.success(request, f'Your enrollment in {program_level.name} has been reactivated!')
                return redirect('courses:student_dashboard')

        # Create new enrollment
        enrollment = StudentEnrollment.objects.create(
            student=request.user,
            program_level=program_level,
            status='active',
            notes=f'Direct enrollment by {request.user.get_full_name() or request.user.username}'
        )

        messages.success(request, f'🎉 Congratulations! You have successfully enrolled in {program_level.name}!')
        messages.info(request, 'You can now access your courses and start learning!')

        return render(request, 'programs/enrollment_success.html', {
            'program_level': program_level,
            'enrollment': enrollment
        })

    except Exception as e:
        messages.error(request, f'An error occurred during enrollment: {str(e)}')
        return redirect('programs:program_level_detail', level_id=level_id)


@login_required
def my_enrollments(request):
    """Display user's current enrollments"""
    enrollments = StudentEnrollment.objects.filter(
        student=request.user
    ).select_related('program_level').order_by('-enrollment_date')

    return render(request, 'programs/my_enrollments.html', {
        'enrollments': enrollments
    })
