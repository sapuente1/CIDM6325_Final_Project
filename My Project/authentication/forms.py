from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from donations.models import Donor, Pantry


class BaseUserRegistrationForm(UserCreationForm):
    """Base registration form with common fields"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class DonorRegistrationForm(BaseUserRegistrationForm):
    """Registration form for food donors"""
    organization_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Restaurant, Grocery Store, etc.'
        }),
        help_text="Name of your organization or business"
    )
    contact_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(555) 123-4567'
        })
    )
    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, State'
        }),
        help_text="Your location for pickup coordination"
    )
    
    def clean_organization_name(self):
        org_name = self.cleaned_data.get('organization_name')
        if Donor.objects.filter(organization_name=org_name).exists():
            raise forms.ValidationError("A donor with this organization name already exists.")
        return org_name


class PantryRegistrationForm(BaseUserRegistrationForm):
    """Registration form for food pantries"""
    organization_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Community Food Bank, etc.'
        }),
        help_text="Name of your food pantry or organization"
    )
    contact_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(555) 123-4567'
        })
    )
    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, State'
        }),
        help_text="Your service location"
    )
    service_area = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Geographic area you serve'
        })
    )
    capacity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '100'
        }),
        help_text="Approximate number of people served weekly"
    )
    
    def clean_organization_name(self):
        org_name = self.cleaned_data.get('organization_name')
        if Pantry.objects.filter(organization_name=org_name).exists():
            raise forms.ValidationError("A pantry with this organization name already exists.")
        return org_name