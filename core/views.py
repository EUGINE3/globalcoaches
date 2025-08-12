from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileUpdateForm
from .models import UserProfile

def landing_page(request):
    """Landing page with hero section and call to action"""
    return render(request, 'core/landing_page.html')


def redirect_to_auth_login(request):
    """Redirect to new authentication login"""
    return redirect('authentication:login')


def redirect_to_auth_logout(request):
    """Redirect to new authentication logout"""
    return redirect('authentication:logout')


def redirect_to_auth_register(request):
    """Redirect to new authentication register"""
    return redirect('authentication:register')

def user_login(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'core:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')

def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:landing_page')

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Global Coaches Academy.')
            return redirect('core:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def dashboard(request):
    """Student dashboard view"""
    return render(request, 'core/dashboard.html')

@login_required
def profile_update(request):
    """Update user profile view"""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('core:dashboard')
    else:
        form = UserProfileUpdateForm(instance=profile)
    
    return render(request, 'core/profile_update.html', {'form': form})

