from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def module_detail(request, module_id):
    """Module detail page with weekly breakdown"""
    return render(request, 'courses/module_detail.html', {'module_id': module_id})

@login_required
def week_detail(request, module_id, week_number):
    """Weekly content detail page"""
    return render(request, 'courses/week_detail.html', {
        'module_id': module_id,
        'week_number': week_number
    })

@login_required
def submit_assignment(request, assignment_id):
    """Assignment submission page"""
    return render(request, 'courses/submit_assignment.html', {'assignment_id': assignment_id})

