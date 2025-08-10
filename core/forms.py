from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, COUNTRY_CHOICES, COUNTRY_CHOICES

class CustomUserCreationForm(UserCreationForm):
    """Custom registration form with additional fields"""
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select your country'
        })
    )
    institution = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your institution/organization'
        })
    )
    town = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your town/city'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update field widgets with Bootstrap classes
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        # Generate username from email
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
            # Create UserProfile with additional fields
            UserProfile.objects.create(
                user=user,
                country=self.cleaned_data['country'],
                town=self.cleaned_data['town'],
                institution=self.cleaned_data['institution']
            )
        return user 

class UserProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information"""
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select your country'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'country', 'town', 'institution', 'bio', 'profile_picture', 'date_of_birth']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            }),
            'town': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your town/city'
            }),
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your institution/organization'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        } 