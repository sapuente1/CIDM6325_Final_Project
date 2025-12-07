# pantries/forms.py
from django import forms
from donations.models import Pantry


class PantryForm(forms.ModelForm):
    """Form for updating pantry profiles"""
    
    class Meta:
        model = Pantry
        fields = ['organization_name', 'contact_phone', 'location', 'service_area', 'capacity']
        widgets = {
            'organization_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Food Bank Name'}
            ),
            'contact_phone': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '(555) 123-4567'}
            ),
            'location': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'City or general location'}
            ),
            'service_area': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Geographic area served'}
            ),
            'capacity': forms.NumberInput(
                attrs={'min': 1, 'class': 'form-control', 'placeholder': 'Number of people served weekly'}
            ),
        }
        labels = {
            'organization_name': 'Organization Name',
            'contact_phone': 'Phone Number',
            'location': 'Location',
            'service_area': 'Service Area',
            'capacity': 'Weekly Capacity (people served)',
        }
        help_texts = {
            'capacity': 'Approximate number of people your pantry can serve weekly.',
            'contact_phone': 'Contact phone number for donors.',
            'location': 'City or general location of your pantry.',
            'service_area': 'Geographic area your pantry serves.',
        }
    
    def clean_capacity(self):
        """Validate that capacity is positive"""
        capacity = self.cleaned_data.get('capacity')
        if capacity and capacity <= 0:
            raise forms.ValidationError("Capacity must be greater than zero.")
        return capacity
    
    def clean_contact_phone(self):
        """Basic phone number validation"""
        phone = self.cleaned_data.get('contact_phone')
        if phone:
            # Remove all non-digit characters for length check
            digits_only = ''.join(filter(str.isdigit, phone))
            if len(digits_only) < 10:
                raise forms.ValidationError("Please enter a valid phone number with at least 10 digits.")
        return phone
