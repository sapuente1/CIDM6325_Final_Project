# donations/validators.py
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

def validate_future_date(value):
    """Ensure date is in the future"""
    if value <= timezone.now():
        raise ValidationError("Date must be in the future.")

def validate_reasonable_expiry(value):
    """Ensure expiry date is reasonable (not too far in future)"""
    max_future = timezone.now() + timedelta(days=365)  # 1 year max
    if value > max_future:
        raise ValidationError("Expiry date cannot be more than 1 year in the future.")

def validate_phone_number(value):
    """Basic phone number validation"""
    import re
    if not re.match(r'^\+?1?\d{9,15}$', value.replace('-', '').replace(' ', '')):
        raise ValidationError("Enter a valid phone number.")

def validate_positive_quantity(value):
    """Ensure quantity is positive"""
    if value <= 0:
        raise ValidationError("Quantity must be greater than zero.")