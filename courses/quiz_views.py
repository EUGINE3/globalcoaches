from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Assignment, QuizQuestion, QuizChoice, AssignmentSubmission
from django.contrib import messages
from django.db.models import Sum, F

@login_required
def quiz_detail(request, assignment_id):
    quiz = get_object_or_404(Assignment, id=assignment_id, is_quiz=True)
    context = {
        'quiz': quiz,
        'questions': quiz.questions.order_by('order').prefetch_related('choices'),
        'time_limit': quiz.time_limit_minutes * 60 if quiz.time_limit_minutes else None,
    }
    return render(request, 'courses/quiz_detail.html', context)

@login_required
def start_quiz(request, assignment_id):
    quiz = get_object_or_404(Assignment, id=assignment_id, is_quiz=True)
    
    # Check if there's an existing submission
    existing_submission = AssignmentSubmission.objects.filter(
        assignment=quiz,
        student=request.user,
        is_graded=False
    ).first()
    
    if existing_submission:
        messages.warning(request, "You already have an ongoing quiz attempt.")
        return redirect('courses:quiz_detail', assignment_id=quiz.id)
    
    # Create new submission
    submission = AssignmentSubmission.objects.create(
        assignment=quiz,
        student=request.user,
        submitted_at=timezone.now()
    )
    
    return redirect('courses:take_quiz', assignment_id=quiz.id)

@login_required
def take_quiz(request, assignment_id):
    quiz = get_object_or_404(Assignment, id=assignment_id, is_quiz=True)
    submission = get_object_or_404(
        AssignmentSubmission, 
        assignment=quiz, 
        student=request.user, 
        is_graded=False
    )
    
    if request.method == 'POST':
        score = 0
        total_points = quiz.questions.aggregate(total=Sum('points'))['total'] or 0
        
        # Process each question
        for question in quiz.questions.all():
            if question.question_type in ['multiple_choice', 'true_false']:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    choice = QuizChoice.objects.get(id=choice_id)
                    if choice.is_correct:
                        score += question.points
            else:  # short_answer or essay
                answer = request.POST.get(f'question_{question.id}')
                if answer:  # Store answer for manual grading
                    submission.submission_text += f"\nQuestion {question.id}: {answer}"
        
        # Calculate percentage and update submission
        percentage = (score / total_points * 100) if total_points > 0 else 0
        submission.points_earned = score
        submission.grade_percentage = percentage
        submission.is_graded = True
        submission.graded_at = timezone.now()
        submission.save()
        
        messages.success(request, "Quiz submitted successfully!")
        return redirect('courses:quiz_results', submission_id=submission.id)
    
    context = {
        'quiz': quiz,
        'submission': submission,
        'questions': quiz.questions.order_by('order').prefetch_related('choices'),
        'time_limit': quiz.time_limit_minutes * 60 if quiz.time_limit_minutes else None,
    }
    return render(request, 'courses/take_quiz.html', context)

@login_required
def quiz_results(request, submission_id):
    submission = get_object_or_404(
        AssignmentSubmission.objects.select_related('assignment'),
        id=submission_id,
        student=request.user
    )
    
    if not submission.assignment.is_quiz:
        messages.error(request, "This submission is not for a quiz.")
        return redirect('courses:dashboard')
    
    context = {
        'submission': submission,
        'quiz': submission.assignment,
        'passed': submission.grade_percentage >= submission.assignment.passing_score,
    }
    return render(request, 'courses/quiz_results.html', context)

@login_required
def check_quiz_time(request, submission_id):
    """AJAX endpoint to check if quiz time has expired"""
    submission = get_object_or_404(
        AssignmentSubmission,
        id=submission_id,
        student=request.user,
        is_graded=False
    )
    
    if submission.assignment.time_limit_minutes:
        time_limit = submission.assignment.time_limit_minutes * 60
        elapsed_time = (timezone.now() - submission.submitted_at).total_seconds()
        time_remaining = max(0, time_limit - elapsed_time)
        
        if time_remaining <= 0:
            # Auto-submit the quiz
            submission.is_graded = True
            submission.points_earned = 0
            submission.grade_percentage = 0
            submission.save()
            return JsonResponse({'expired': True})
            
        return JsonResponse({
            'expired': False,
            'time_remaining': time_remaining
        })
    
    return JsonResponse({'expired': False})
