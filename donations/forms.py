# donations/forms.py
from django import forms
from django.utils import timezone
from .models import Donation

class DonationForm(forms.ModelForm):
    """Form for creating and updating donations"""
    
    class Meta:
        model = Donation
        fields = ['food_type', 'description', 'quantity', 'unit', 'location', 'expiry_date', 'pickup_instructions']
        widgets = {
            'expiry_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Describe the food donation...'}
            ),
            'quantity': forms.NumberInput(
                attrs={'min': 0.1, 'step': 0.1, 'class': 'form-control'}
            ),
            'unit': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'e.g., lbs, servings, items'}
            ),
            'location': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Pickup location'}
            ),
            'food_type': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'pickup_instructions': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Any special pickup instructions...'}
            ),
        }
        labels = {
            'food_type': 'Type of Food',
            'expiry_date': 'Expiry Date and Time',
            'quantity': 'Quantity',
            'unit': 'Unit of Measurement',
            'location': 'Pickup Location',
            'description': 'Description',
            'pickup_instructions': 'Pickup Instructions',
        }
    
    def clean_expiry_date(self):
        """Validate that expiry date is in the future"""
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date and expiry_date <= timezone.now():
            raise forms.ValidationError("Expiry date must be in the future.")
        return expiry_date
    
    def clean_quantity(self):
        """Validate that quantity is positive"""
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity
    
    def clean_description(self):
        """Validate description length and content"""
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 10:
            raise forms.ValidationError("Please provide a more detailed description (at least 10 characters).")
        return description.strip() if description else description


class DonationSearchForm(forms.Form):
    """Form for searching and filtering donations"""
    
    search = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by food type or description...',
            'class': 'form-control'
        }),
        label='Search'
    )
    
    food_type = forms.ChoiceField(
        choices=[('', 'All Food Types')] + Donation.FOOD_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Food Type'
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Donation.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Status'
    )
    
    location = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Filter by location...',
            'class': 'form-control'
        }),
        label='Location'
    )


class ClaimDonationForm(forms.Form):
    """Form for claiming a donation by a pantry"""
    
    notes = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Optional notes about this claim...'
        }),
        label='Notes (Optional)'
    )
    
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I confirm that I want to claim this donation'
    )
