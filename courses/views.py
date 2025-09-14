from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models
from django.utils import timezone
from .models import (
    ProgramLevel, Module, ProgramModule, Course, WeeklyResource, ModuleProgress,
    WeekProgress, ResourceView, StudentEnrollment, Assignment, AssignmentSubmission,
    Lesson, LessonProgress, ResourceProgress
)
from .utils import ProgressiveAccessManager, CompletionTracker
from students.models import StudentEnrollment

def program_overview(request):
    """Display overview of the Global Coaches Program structure"""
    program_levels = ProgramLevel.objects.filter(is_active=True).order_by('id')
    modules = Module.objects.filter(is_active=True).order_by('id')

    # Get program modules for each level
    program_data = []
    for level in program_levels:
        level_modules = ProgramModule.objects.filter(
            program_level=level,
            is_active=True
        ).select_related('module').order_by('module__id')

        program_data.append({
            'level': level,
            'modules': level_modules
        })

    context = {
        'program_levels': program_levels,
        'modules': modules,
        'program_data': program_data,
    }
    return render(request, 'courses/program_overview.html', context)

@login_required
def module_detail(request, module_id):
    """Program module detail page with topics and lessons breakdown"""
    program_module = get_object_or_404(ProgramModule, id=module_id, is_active=True)

    # Check if student can access this program module
    if not ProgressiveAccessManager.can_access_program_module(request.user, program_module):
        messages.error(request, 'You need to complete previous modules before accessing this content.')
        return redirect('courses:student_dashboard')

    # Get or create module progress
    from .models import ModuleProgress
    module_progress = ModuleProgress.objects.filter(
        student=request.user,
        program_module=program_module
    ).first()

    if not module_progress:
        module_progress = ModuleProgress.objects.create(
            student=request.user,
            program_module=program_module,
            is_unlocked=True
        )

    # Get topics with lessons and progress information
    topics = []
    for topic in program_module.topics.filter(is_active=True).order_by('order'):
        # Get lessons for this topic
        lessons = []
        for lesson in topic.lessons.filter(is_active=True).order_by('lesson_number'):
            # Check lesson progress
            from .models import LessonProgress
            lesson_progress = LessonProgress.objects.filter(
                student=request.user,
                lesson=lesson
            ).first()

            lesson.progress = lesson_progress
            lesson.is_accessible = ProgressiveAccessManager.can_access_lesson(request.user, lesson)

            # Get lesson resources
            resources = []
            for resource in lesson.resources.filter(is_active=True).order_by('order'):
                from .models import ResourceProgress
                resource_progress = ResourceProgress.objects.filter(
                    student=request.user,
                    resource=resource
                ).first()
                resource.progress = resource_progress
                resources.append(resource)

            lesson.resource_list = resources
            lessons.append(lesson)

        topic.lesson_list = lessons

        # Calculate topic progress for summary (lessons + assignment gating)
        total_lessons = len(lessons)
        completed_lessons = sum(1 for lesson in lessons if lesson.progress and lesson.progress.is_completed)
        topic.total_lessons = total_lessons
        topic.completed_lessons = completed_lessons

        base_pct = round((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

        # Assignment gating: if the topic (or its lessons) has assignments, require submission(s) to reach 100%
        topic_assignments_qs = Assignment.objects.filter(
            models.Q(topic=topic) | models.Q(lesson__topic=topic),
            is_active=True
        )
        total_assignments = topic_assignments_qs.count()
        submitted_assignments = AssignmentSubmission.objects.filter(
            student=request.user,
            assignment__in=topic_assignments_qs
        ).values('assignment_id').distinct().count()

        topic.progress_percentage = base_pct
        if total_assignments > 0 and submitted_assignments < total_assignments and topic.progress_percentage == 100:
            # Block 100% until all assignments submitted
            topic.progress_percentage = 99

        topic.lessons_label = "Lessons" if total_lessons > 1 else "Lesson"

        topics.append(topic)

    # Get assignments for this program module
    assignments = Assignment.objects.filter(
        topic__program_module=program_module,
        is_active=True
    ).order_by('due_date')

    context = {
        'program_module': program_module,
        'module': program_module.module,  # For backward compatibility
        'topics': topics,
        'assignments': assignments,
        'module_progress': module_progress,
    }
    return render(request, 'courses/module_detail.html', context)

@login_required
def lesson_detail(request, lesson_id):
    """Individual lesson detail page with resources and activities"""
    from .models import Lesson, LessonProgress, ResourceProgress

    lesson = get_object_or_404(Lesson, id=lesson_id, is_active=True)

    # Check if student can access this lesson
    if not ProgressiveAccessManager.can_access_lesson(request.user, lesson):
        messages.error(request, 'You need to complete previous lessons before accessing this content.')
        return redirect('courses:module_detail', module_id=lesson.topic.program_module.id)

    # Get or create lesson progress
    lesson_progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson,
        defaults={'started_at': timezone.now()}
    )

    # Update last accessed time
    lesson_progress.last_accessed = timezone.now()
    lesson_progress.save()

    # Get lesson resources with progress
    resources = []
    for resource in lesson.resources.filter(is_active=True).order_by('order'):
        resource_progress = ResourceProgress.objects.filter(
            student=request.user,
            resource=resource
        ).first()
        resource.progress = resource_progress
        resources.append(resource)

    # Get lesson assignments
    assignments = lesson.assignments.filter(is_active=True).order_by('due_date')

    context = {
        'lesson': lesson,
        'lesson_progress': lesson_progress,
        'resources': resources,
        'assignments': assignments,
        'topic': lesson.topic,
        'program_module': lesson.topic.program_module,
    }
    return render(request, 'courses/lesson_detail.html', context)

@login_required
def topic_detail(request, topic_id):
    """Topic detail page showing all lessons within the topic"""
    from .models import ModuleTopic, LessonProgress, ResourceProgress

    topic = get_object_or_404(ModuleTopic, id=topic_id, is_active=True)
    program_module = topic.program_module

    # Check if student can access this topic's module
    if not ProgressiveAccessManager.can_access_program_module(request.user, program_module):
        messages.error(request, 'You need to complete previous modules before accessing this content.')
        return redirect('courses:progressive_modules')

    # Get lessons with progress and accessibility
    lessons = []
    for lesson in topic.lessons.filter(is_active=True).order_by('sequence_order', 'lesson_number'):
        # Get lesson progress
        lesson_progress = LessonProgress.objects.filter(
            student=request.user,
            lesson=lesson
        ).first()

        lesson.progress = lesson_progress
        lesson.is_accessible = ProgressiveAccessManager.can_access_lesson(request.user, lesson)

        # Get lesson resources with progress
        resources = []
        for resource in lesson.resources.filter(is_active=True).order_by('order'):
            resource_progress = ResourceProgress.objects.filter(
                student=request.user,
                resource=resource
            ).first()
            resource.progress = resource_progress
            resources.append(resource)

        lesson.resource_list = resources

        # Get lesson assignments
        lesson.assignment_list = lesson.assignments.filter(is_active=True).order_by('due_date')

        lessons.append(lesson)

    # Calculate topic progress (lessons + assignment gating)
    total_lessons = len(lessons)
    completed_lessons = sum(1 for lesson in lessons if lesson.progress and lesson.progress.is_completed)
    base_pct = round((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

    # Get topic assignments (topic-level and lesson-level)
    topic_assignments_qs = Assignment.objects.filter(
        models.Q(topic=topic) | models.Q(lesson__topic=topic),
        is_active=True
    ).order_by('due_date')

    submitted_assignments = AssignmentSubmission.objects.filter(
        student=request.user,
        assignment__in=topic_assignments_qs
    ).values('assignment_id').distinct().count()

    total_assignments = topic_assignments_qs.count()
    topic_progress = base_pct
    if total_assignments > 0 and submitted_assignments < total_assignments and topic_progress == 100:
        topic_progress = 99

    context = {
        'topic': topic,
        'program_module': program_module,
        'lessons': lessons,
        'topic_assignments': list(topic_assignments_qs),
        'topic_progress': topic_progress,
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
    }
    return render(request, 'courses/topic_detail.html', context)

@login_required
def week_detail(request, module_id, week_number):
    """Weekly content detail page"""
    module = get_object_or_404(Module, id=module_id, is_active=True)
    week = get_object_or_404(Week, module=module, week_number=week_number)

    # Check if student can access this week
    if not ProgressiveAccessManager.can_access_week(request.user, week):
        messages.error(request, 'You need to complete previous weeks before accessing this content.')
        return redirect('courses:module_detail', module_id=module.id)

    # Get week progress
    week_progress = week.get_or_create_progress(request.user)

    # Get resources with progress information
    resources = []
    for resource in week.learning_resources.filter(is_active=True).order_by('order', 'created_at'):
        try:
            resource.view_progress = ResourceView.objects.get(
                student=request.user, resource=resource
            )
        except ResourceView.DoesNotExist:
            resource.view_progress = None
        resources.append(resource)

    context = {
        'module': module,
        'week': week,
        'resources': resources,
        'week_progress': week_progress,
    }
    return render(request, 'courses/week_detail.html', context)

@login_required
def submit_assignment(request, assignment_id):
    """Assignment submission page (upload text/file); submission required for topic completion."""
    assignment = get_object_or_404(Assignment, id=assignment_id, is_active=True)

    # Determine the related program module for access control and redirect target
    if assignment.lesson:
        topic = assignment.lesson.topic
    else:
        topic = assignment.topic
    program_module = topic.program_module

    # Check if student can access this assignment's module
    if not ProgressiveAccessManager.can_access_program_module(request.user, program_module):
        messages.error(request, 'You need to complete previous modules before accessing this assignment.')
        return redirect('courses:progressive_modules')

    if request.method == 'POST':
        # Handle submission
        submission_text = request.POST.get('submission_text', '').strip()
        submission_file = request.FILES.get('submission_file')

        # Next attempt number
        last_attempt = AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).order_by('-attempt_number').first()
        next_attempt = (last_attempt.attempt_number + 1) if last_attempt else 1

        AssignmentSubmission.objects.create(
            assignment=assignment,
            student=request.user,
            submission_text=submission_text,
            submission_file=submission_file,
            attempt_number=next_attempt,
        )
        messages.success(request, 'Assignment submitted successfully!')
        return redirect('courses:topic_detail', topic_id=topic.id)

    return render(request, 'courses/submit_assignment.html', {
        'assignment': assignment,
        'program_module': program_module,
        'topic': topic,
    })


@login_required
@require_POST
def mark_resource_viewed(request, resource_id):
    """API endpoint to mark a resource as viewed"""
    resource = get_object_or_404(WeeklyResource, id=resource_id)

    # Check if student can access this resource's week
    if not ProgressiveAccessManager.can_access_week(request.user, resource.week):
        return JsonResponse({'error': 'Access denied'}, status=403)

    resource_view = CompletionTracker.mark_resource_viewed(request.user, resource)

    return JsonResponse({
        'success': True,
        'view_count': resource_view.view_count,
        'completed': resource_view.completed
    })


@login_required
@require_POST
def mark_resource_completed(request, resource_id):
    """API endpoint to mark a resource as completed"""
    resource = get_object_or_404(WeeklyResource, id=resource_id)

    # Check if student can access this resource's week
    if not ProgressiveAccessManager.can_access_week(request.user, resource.week):
        return JsonResponse({'error': 'Access denied'}, status=403)

    resource_view = CompletionTracker.mark_resource_completed(request.user, resource)

    # Check if week is now completed
    week_progress = resource.week.get_or_create_progress(request.user)
    week_completed = week_progress.is_completed

    return JsonResponse({
        'success': True,
        'resource_completed': resource_view.completed,
        'week_completed': week_completed,
        'completion_date': resource_view.completion_date.isoformat() if resource_view.completion_date else None
    })



@login_required
@require_POST
def mark_lesson_completed(request, lesson_id):
    """API endpoint to mark a lesson as completed"""
    # Import here to avoid circulars
    from .models import Lesson, LessonProgress

    lesson = get_object_or_404(Lesson, id=lesson_id, is_active=True)

    # Check if student can access this lesson
    if not ProgressiveAccessManager.can_access_lesson(request.user, lesson):
        return JsonResponse({'error': 'Access denied'}, status=403)

    # Update or create lesson progress
    progress, _ = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson,
        defaults={'started_at': timezone.now()}
    )
    progress.is_started = True
    progress.is_completed = True
    progress.completion_percentage = 100.0
    progress.completed_at = timezone.now()
    progress.save()

    # Update module progress based on lesson completion
    CompletionTracker.update_module_progress_from_lessons(request.user, lesson.topic.program_module)

    return JsonResponse({'success': True})


@login_required
def student_progress_overview(request):
    """Overview of student's progress across all enrolled programs"""
    enrollments = StudentEnrollment.objects.filter(student=request.user, status='active')

    progress_data = []
    for enrollment in enrollments:
        # Get program modules for this enrollment's program level
        program_modules = ProgramModule.objects.filter(
            program_level=enrollment.program_level,
            is_active=True
        ).select_related('module').order_by('id')

        module_progress = []
        for program_module in program_modules:
            # Check if student can access this program module
            accessible = ProgressiveAccessManager.can_access_program_module(request.user, program_module)

            # Get or create progress for this program module
            from .models import ModuleProgress
            progress = ModuleProgress.objects.filter(
                student=request.user,
                program_module=program_module
            ).first()

            if not progress and accessible:
                # Create progress if accessible but doesn't exist
                progress = ModuleProgress.objects.create(
                    student=request.user,
                    program_module=program_module,
                    is_unlocked=True
                )

            module_progress.append({
                'program_module': program_module,
                'module': program_module.module,
                'progress': progress,
                'accessible': accessible,
                'progress_percentage': progress.progress_percentage if progress else 0,
                'is_completed': progress.is_completed if progress else False
            })

        next_action = ProgressiveAccessManager.get_next_required_action(
            request.user, enrollment.program_level
        )

        progress_data.append({
            'enrollment': enrollment,
            'program_level': enrollment.program_level,
            'modules': module_progress,
            'next_action': next_action
        })

    context = {
        'progress_data': progress_data,
    }
    return render(request, 'courses/progress_overview.html', context)


@login_required
def progressive_modules(request):
    """Display progressive module learning path for the student"""
    # Get student's active enrollment
    enrollment = StudentEnrollment.objects.filter(
        student=request.user,
        status='active'
    ).first()

    if not enrollment:
        messages.error(request, 'You are not enrolled in any active program.')
        return redirect('core:dashboard')

    # Get progression data
    progression = ProgressiveAccessManager.get_student_module_progression(
        request.user, enrollment.program_level
    )

    # Get next available module
    next_module = ProgressiveAccessManager.get_next_available_module(
        request.user, enrollment.program_level
    )

    # Calculate statistics
    total_modules = len(progression)
    unlocked_modules = sum(1 for item in progression if item['status'] in ['unlocked', 'completed'])
    completed_modules = sum(1 for item in progression if item['status'] == 'completed')

    if total_modules > 0:
        overall_progress = round((completed_modules / total_modules) * 100)
    else:
        overall_progress = 0

    stats = {
        'total_modules': total_modules,
        'unlocked_modules': unlocked_modules,
        'completed_modules': completed_modules,
        'overall_progress': overall_progress,
    }

    context = {
        'progression': progression,
        'next_module': next_module,
        'program_level': enrollment.program_level,
        'stats': stats,
    }

    return render(request, 'courses/progressive_modules.html', context)


@login_required
def student_dashboard(request):
    """Comprehensive student dashboard with progress, assignments, and activities"""
    from django.utils import timezone
    from datetime import timedelta
    from .models import Assignment, AssignmentSubmission, LessonProgress, ResourceProgress

    # Get student's active enrollment
    enrollment = StudentEnrollment.objects.filter(
        student=request.user,
        status='active'
    ).first()

    if not enrollment:
        messages.error(request, 'You are not enrolled in any active program.')
        return redirect('core:dashboard')

    # Get module progression
    module_progression = ProgressiveAccessManager.get_student_module_progression(
        request.user, enrollment.program_level
    )

    # Calculate dashboard statistics
    total_modules = len(module_progression)
    completed_modules = sum(1 for item in module_progression if item['status'] == 'completed')

    # Calculate total credits earned
    total_credits_earned = sum(
        item['module'].credits for item in module_progression
        if item['status'] == 'completed'
    )

    # Get upcoming assignments
    now = timezone.now()
    upcoming_assignments = Assignment.objects.filter(
        models.Q(lesson__topic__program_module__program_level=enrollment.program_level) |
        models.Q(topic__program_module__program_level=enrollment.program_level),
        due_date__gte=now - timedelta(days=7),  # Include overdue assignments from last week
        is_active=True
    ).exclude(
        submissions__student=request.user,
        submissions__is_graded=True,
        submissions__grade_percentage__gte=70
    ).order_by('due_date')[:10]

    # Add calculated fields to assignments
    for assignment in upcoming_assignments:
        assignment.days_until_due = assignment.days_until_due()
        assignment.is_overdue = assignment.is_overdue()

    # pending_assignments = upcoming_assignments.filter(due_date__gte=now).count()

    # Calculate overall progress
    if total_modules > 0:
        overall_progress = round((completed_modules / total_modules) * 100)
    else:
        overall_progress = 0

    dashboard_stats = {
        'total_modules': total_modules,
        'completed_modules': completed_modules,
        'total_credits_earned': total_credits_earned,
        # 'pending_assignments': pending_assignments,
        'overall_progress': overall_progress,
    }

    # Get next lesson to work on
    next_lesson = None
    for item in module_progression:
        if item['status'] == 'unlocked':
            # Find first incomplete lesson in this module
            from .models import Lesson
            lessons = Lesson.objects.filter(
                topic__program_module=item['module'],
                is_active=True
            ).order_by('topic__order', 'lesson_number')

            for lesson in lessons:
                lesson_progress = LessonProgress.objects.filter(
                    student=request.user,
                    lesson=lesson
                ).first()

                if not lesson_progress or not lesson_progress.is_completed:
                    next_lesson = lesson
                    break

            if next_lesson:
                break

    # Get recent activities
    recent_activities = []

    # Recent lesson progress
    recent_lesson_progress = LessonProgress.objects.filter(
        student=request.user,
        last_accessed__gte=now - timedelta(days=7)
    ).order_by('-last_accessed')[:5]

    for progress in recent_lesson_progress:
        recent_activities.append({
            'type': 'lesson',
            'title': f"Worked on {progress.lesson.title}",
            'timestamp': progress.last_accessed
        })

    # Recent assignment submissions
    recent_submissions = AssignmentSubmission.objects.filter(
        student=request.user,
        submitted_at__gte=now - timedelta(days=7)
    ).order_by('-submitted_at')[:5]

    for submission in recent_submissions:
        recent_activities.append({
            'type': 'assignment',
            'title': f"Submitted {submission.assignment.title}",
            'timestamp': submission.submitted_at
        })

    # Recent resource views
    recent_resource_progress = ResourceProgress.objects.filter(
        student=request.user,
        last_viewed_at__gte=now - timedelta(days=7)
    ).order_by('-last_viewed_at')[:5]

    for progress in recent_resource_progress:
        recent_activities.append({
            'type': 'resource',
            'title': f"Viewed {progress.resource.title}",
            'timestamp': progress.last_viewed_at
        })

    # Sort activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:10]  # Limit to 10 most recent

    context = {
        'enrollment': enrollment,
        'module_progression': module_progression,
        'dashboard_stats': dashboard_stats,
        'upcoming_assignments': upcoming_assignments,
        'next_lesson': next_lesson,
        'recent_activities': recent_activities,
    }

    return render(request, 'courses/student_dashboard.html', context)

