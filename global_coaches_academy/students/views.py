from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StudentEnrollment
from core.models import UserProfile

@login_required
def student_profile(request):
    """Student profile management"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update profile information
        profile.phone_number = request.POST.get('phone', '')
        profile.country = request.POST.get('country', '')
        profile.bio = request.POST.get('bio', '')
        profile.date_of_birth = request.POST.get('dateOfBirth') or None
        profile.save()
        
        # Update user information
        request.user.first_name = request.POST.get('firstName', '')
        request.user.last_name = request.POST.get('lastName', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('students:student_profile')
    
    return render(request, 'students/student_profile.html', {'profile': profile})

@login_required
def student_dashboard(request):
    """Student dashboard with enrollments and progress"""
    enrollments = StudentEnrollment.objects.filter(student=request.user)
    return render(request, 'students/student_dashboard.html', {'enrollments': enrollments})

