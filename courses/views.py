from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Module, Week, WeeklyResource, Assignment, ModuleProgress, WeekProgress, ResourceView
from .utils import ProgressiveAccessManager, CompletionTracker
from students.models import StudentEnrollment

@login_required
def module_detail(request, module_id):
    """Module detail page with weekly breakdown"""
    module = get_object_or_404(Module, id=module_id, is_active=True)

    # Check if student can access this module
    if not ProgressiveAccessManager.can_access_module(request.user, module):
        messages.error(request, 'You need to complete previous modules before accessing this content.')
        return redirect('core:dashboard')

    # Get or create module progress
    module_progress = module.get_or_create_progress(request.user)

    # Get weeks with progress information
    weeks = []
    for week in module.weeks.all().prefetch_related('learning_resources', 'assignment'):
        week_progress = week.get_or_create_progress(request.user)
        week.progress = week_progress
        week.is_accessible = ProgressiveAccessManager.can_access_week(request.user, week)

        # Add resource progress information
        for resource in week.learning_resources.all():
            try:
                resource.view_progress = ResourceView.objects.get(
                    student=request.user, resource=resource
                )
            except ResourceView.DoesNotExist:
                resource.view_progress = None

        weeks.append(week)

    context = {
        'module': module,
        'weeks': weeks,
        'module_progress': module_progress,
    }
    return render(request, 'courses/module_detail.html', context)

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
    """Assignment submission page"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    # Check if student can access this assignment's week
    if not ProgressiveAccessManager.can_access_week(request.user, assignment.week):
        messages.error(request, 'You need to complete previous weeks before accessing this assignment.')
        return redirect('courses:module_detail', module_id=assignment.week.module.id)

    return render(request, 'courses/submit_assignment.html', {'assignment_id': assignment_id})


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
def student_progress_overview(request):
    """Overview of student's progress across all enrolled programs"""
    enrollments = StudentEnrollment.objects.filter(student=request.user, status='active')

    progress_data = []
    for enrollment in enrollments:
        modules = Module.objects.filter(
            faculty_program=enrollment.faculty_program,
            is_active=True
        ).order_by('month_number')

        module_progress = []
        for module in modules:
            accessible = ProgressiveAccessManager.can_access_module(request.user, module)
            if accessible:
                progress = module.get_or_create_progress(request.user)
                module_progress.append({
                    'module': module,
                    'progress': progress,
                    'accessible': True
                })
            else:
                module_progress.append({
                    'module': module,
                    'progress': None,
                    'accessible': False
                })

        next_action = ProgressiveAccessManager.get_next_required_action(
            request.user, enrollment.faculty_program
        )

        progress_data.append({
            'enrollment': enrollment,
            'modules': module_progress,
            'next_action': next_action
        })

    context = {
        'progress_data': progress_data,
    }
    return render(request, 'courses/progress_overview.html', context)

