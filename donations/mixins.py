"""
Custom mixins for role-based access control in CFMP.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


class DonorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require user to be authenticated and have donor role"""
    
    def test_func(self):
        return hasattr(self.request.user, 'donor')
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("You must be registered as a donor to access this page.")


class PantryRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require user to be authenticated and have pantry role"""
    
    def test_func(self):
        return hasattr(self.request.user, 'pantry')
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("You must be registered as a pantry to access this page.")


class OwnerRequiredMixin(UserPassesTestMixin):
    """Require user to be the owner of the object"""
    
    def test_func(self):
        obj = self.get_object()
        return hasattr(self.request.user, 'donor') and obj.donor == self.request.user.donor
    
    def handle_no_permission(self):
        raise PermissionDenied("You can only modify your own donations.")


class DonationOwnerMixin(UserPassesTestMixin):
    """Mixin to ensure user owns the donation"""
    
    def test_func(self):
        donation = self.get_object()
        return (hasattr(self.request.user, 'donor') and 
                donation.donor == self.request.user.donor)
    
    def handle_no_permission(self):
        raise PermissionDenied("You can only access your own donations.")


class AvailableDonationMixin:
    """Mixin to ensure donation is available for claiming"""
    
    def get_object(self):
        obj = super().get_object()
        if obj.status != 'available':
            raise PermissionDenied("This donation is not available for claiming.")
        return obj