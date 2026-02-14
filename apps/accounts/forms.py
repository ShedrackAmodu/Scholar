from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User, LoginHistory, Role, Permission
import re


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with role-based styling"""
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email or username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Try to authenticate with the provided username/email
            self.user_cache = authenticate(self.request, username=username, password=password)
            
            # If authentication failed, try to find user by email if '@' is present
            if self.user_cache is None and '@' in username:
                try:
                    user = User.objects.get(email=username)
                    self.user_cache = authenticate(self.request, username=user.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if self.user_cache is None:
                raise ValidationError("Invalid email, username, or password.")
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data


class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number'
        })
    )
    role = forms.ChoiceField(
        choices=User.Roles.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'role')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Simple phone validation
            if not re.match(r'^\+?1?\d{9,15}$', phone):
                raise ValidationError("Enter a valid phone number.")
        return phone


class CustomUserChangeForm(UserChangeForm):
    """Form for editing users"""
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 
                 'profile_picture', 'address', 'date_of_birth')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    """Form for users to update their own profile"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'profile_picture', 
                 'address', 'date_of_birth')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )


class RoleForm(forms.ModelForm):
    """Form for creating/editing roles"""
    
    class Meta:
        model = Role
        fields = ('name', 'description', 'permissions')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'permissions': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        }


class PermissionForm(forms.ModelForm):
    """Form for creating/editing permissions"""
    
    class Meta:
        model = Permission
        fields = ('name', 'codename', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'codename': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
