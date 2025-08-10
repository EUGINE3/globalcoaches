from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import MentorProfile, MentorshipPairing, PeerReview, WeeklyCheckin

@login_required
def mentorship_portal(request):
    """Main mentorship portal page"""
    # Get user's mentorship pairing
    try:
        pairing = MentorshipPairing.objects.get(student=request.user, status='active')
        mentor = pairing.mentor
    except MentorshipPairing.DoesNotExist:
        pairing = None
        mentor = None
    
    # Get recent check-ins
    recent_checkins = WeeklyCheckin.objects.filter(
        student=request.user
    ).order_by('-submitted_at')[:5]
    
    # Get peer reviews
    peer_reviews = PeerReview.objects.filter(
        reviewer=request.user
    ).order_by('-submitted_at')[:5]
    
    context = {
        'pairing': pairing,
        'mentor': mentor,
        'recent_checkins': recent_checkins,
        'peer_reviews': peer_reviews,
    }
    return render(request, 'mentorship/mentorship_portal.html', context)

@login_required
def mentor_pairing(request):
    """Handle mentor pairing requests"""
    if request.method == 'POST':
        # Auto-assign mentor based on availability and expertise
        available_mentors = MentorProfile.objects.filter(
            is_available=True,
            max_mentees__gt=0
        )
        
        if available_mentors.exists():
            mentor_profile = available_mentors.first()
            # Need to get or create a student enrollment first
            from students.models import StudentEnrollment
            enrollment = StudentEnrollment.objects.filter(student=request.user).first()
            
            if enrollment:
                pairing = MentorshipPairing.objects.create(
                    mentor=mentor_profile,
                    student=request.user,
                    enrollment=enrollment,
                    status='pending'
                )
                messages.success(request, f'Mentorship request sent to {mentor_profile.user.get_full_name()}!')
            else:
                messages.warning(request, 'You need to enroll in a program first before requesting a mentor.')
        else:
            messages.warning(request, 'No mentors available at the moment. Please try again later.')
    
    return redirect('mentorship:mentorship_portal')

@login_required
def weekly_checkin(request):
    """Submit weekly check-in"""
    if request.method == 'POST':
        # Get the user's active mentorship pairing
        try:
            pairing = MentorshipPairing.objects.get(student=request.user, status='active')
            from datetime import date
            checkin = WeeklyCheckin.objects.create(
                pairing=pairing,
                student=request.user,
                week_ending=date.today(),
                progress_summary=request.POST.get('progress_summary', ''),
                challenges_faced=request.POST.get('challenges_faced', ''),
                goals_next_week=request.POST.get('goals_next_week', ''),
                mentor_support_needed=request.POST.get('mentor_support_needed', ''),
                mood_rating=int(request.POST.get('mood_rating', 3))
            )
            messages.success(request, 'Weekly check-in submitted successfully!')
        except MentorshipPairing.DoesNotExist:
            messages.warning(request, 'You need to have an active mentorship to submit check-ins.')
        return redirect('mentorship:mentorship_portal')
    
    return render(request, 'mentorship/weekly_checkin.html')

@login_required
def peer_review(request, assignment_id):
    """Submit peer review for assignment"""
    # This would be connected to actual assignments
    if request.method == 'POST':
        review = PeerReview.objects.create(
            reviewer=request.user,
            assignment_reference=assignment_id,
            feedback=request.POST.get('feedback', ''),
            rating=int(request.POST.get('rating', 3)),
            suggestions=request.POST.get('suggestions', '')
        )
        messages.success(request, 'Peer review submitted successfully!')
        return redirect('mentorship:mentorship_portal')
    
    return render(request, 'mentorship/peer_review.html', {'assignment_id': assignment_id})

