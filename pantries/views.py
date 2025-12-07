# pantries/views.py
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from donations.models import Pantry
from .forms import PantryForm


class PantryRequiredMixin(UserPassesTestMixin):
    """Ensure user is a pantry"""
    
    def test_func(self):
        return hasattr(self.request.user, 'pantry')
    
    def handle_no_permission(self):
        messages.error(self.request, "You must be a registered food pantry to perform this action.")
        return super().handle_no_permission()


class PantryDetailView(DetailView):
    """View pantry profile (public)"""
    model = Pantry
    template_name = 'pantries/detail.html'
    context_object_name = 'pantry'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get recent claimed donations (last 5)
        context['claimed_donations'] = self.object.claimed_donations.select_related('donor__user').all()[:5]
        context['total_claims'] = self.object.total_claims
        context['recent_claims'] = self.object.recent_claims.count()
        
        # Check if current user owns this pantry
        context['is_owner'] = (
            self.request.user.is_authenticated and
            hasattr(self.request.user, 'pantry') and
            self.object == self.request.user.pantry
        )
        return context


class PantryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update pantry profile (owner only)"""
    model = Pantry
    form_class = PantryForm
    template_name = 'pantries/update.html'
    
    def test_func(self):
        pantry = self.get_object()
        return (hasattr(self.request.user, 'pantry') and 
                pantry == self.request.user.pantry)
    
    def handle_no_permission(self):
        messages.error(self.request, "You can only edit your own pantry profile.")
        return super().handle_no_permission()
    
    def form_valid(self, form):
        messages.success(self.request, 'Pantry profile updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('pantries:detail', kwargs={'pk': self.object.pk})
