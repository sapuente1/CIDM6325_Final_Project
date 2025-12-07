"""
Django views for donations app.
"""

from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.http import Http404
from .models import Donation
from .forms import DonationForm, DonationSearchForm, ClaimDonationForm
from .mixins import DonorRequiredMixin, PantryRequiredMixin, OwnerRequiredMixin, AvailableDonationMixin


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_donations'] = Donation.objects.filter(
            status='available'
        ).select_related('donor__user').order_by('-created_at')[:6]
        context['total_donations'] = Donation.objects.filter(status='available').count()
        return context


class DonationListView(ListView):
    """Public list of available donations"""
    model = Donation
    template_name = 'donations/list.html'
    context_object_name = 'donations'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Donation.objects.filter(
            status='available'
        ).select_related('donor__user').order_by('-created_at')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(food_type__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        # Filter by food type
        food_type = self.request.GET.get('food_type')
        if food_type:
            queryset = queryset.filter(food_type=food_type)
            
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = DonationSearchForm(self.request.GET)
        context['food_types'] = Donation.FOOD_TYPE_CHOICES
        return context


class DonationDetailView(DetailView):
    """Detailed view of a single donation"""
    model = Donation
    template_name = 'donations/detail.html'
    context_object_name = 'donation'
    
    def get_queryset(self):
        return Donation.objects.select_related('donor__user', 'claimed_by__user')


class DonationCreateView(DonorRequiredMixin, CreateView):
    """Create a new donation (donor only)"""
    model = Donation
    form_class = DonationForm
    template_name = 'donations/donation_form.html'
    success_url = reverse_lazy('donations:my_donations')
    
    def form_valid(self, form):
        form.instance.donor = self.request.user.donor
        messages.success(self.request, 'Donation created successfully!')
        return super().form_valid(form)


class DonationUpdateView(DonorRequiredMixin, OwnerRequiredMixin, UpdateView):
    """Edit existing donation (owner only)"""
    model = Donation
    form_class = DonationForm
    template_name = 'donations/update.html'
    success_url = reverse_lazy('donations:my_donations')
    
    def form_valid(self, form):
        messages.success(self.request, 'Donation updated successfully!')
        return super().form_valid(form)


class DonationDeleteView(DonorRequiredMixin, OwnerRequiredMixin, DeleteView):
    """Delete donation (owner only)"""
    model = Donation
    template_name = 'donations/delete.html'
    success_url = reverse_lazy('donations:my_donations')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Donation deleted successfully!')
        return super().delete(request, *args, **kwargs)


class DonationClaimView(PantryRequiredMixin, DetailView):
    """Claim a donation (pantry only)"""
    model = Donation
    template_name = 'donations/claim.html'
    
    def get_object(self):
        obj = super().get_object()
        if obj.status != 'available':
            raise Http404("This donation is not available for claiming.")
        return obj
    
    def post(self, request, *args, **kwargs):
        donation = self.get_object()
        form = ClaimDonationForm(request.POST)
        
        if form.is_valid():
            # Claim the donation
            donation.claim(request.user.pantry)
            messages.success(request, f'You have successfully claimed "{donation.food_type}" from {donation.donor.organization_name}!')
            return redirect('donations:claimed')
        else:
            messages.error(request, 'Please correct the errors in the form.')
            return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ClaimDonationForm()
        return context


class MyDonationsView(DonorRequiredMixin, ListView):
    """Donor's own donations dashboard"""
    template_name = 'donations/my_donations.html'
    context_object_name = 'donations'
    paginate_by = 20
    
    def get_queryset(self):
        return Donation.objects.filter(
            donor=self.request.user.donor
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        donations = self.get_queryset()
        context['total_donations'] = donations.count()
        context['available_count'] = donations.filter(status='available').count()
        context['claimed_count'] = donations.filter(status='claimed').count()
        context['fulfilled_count'] = donations.filter(status='fulfilled').count()
        return context


class ClaimedDonationsView(PantryRequiredMixin, ListView):
    """Pantry's claimed donations"""
    template_name = 'donations/claimed.html'
    context_object_name = 'donations'
    paginate_by = 20
    
    def get_queryset(self):
        return Donation.objects.filter(
            claimed_by=self.request.user.pantry,
            status__in=['claimed', 'fulfilled']
        ).order_by('-claimed_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        donations = self.get_queryset()
        context['total_claimed'] = donations.count()
        context['pending_pickup'] = donations.filter(status='claimed').count()
        context['fulfilled_count'] = donations.filter(status='fulfilled').count()
        return context


class DonationSearchView(ListView):
    """Advanced search view for donations"""
    model = Donation
    template_name = 'donations/search.html'
    context_object_name = 'donations'
    paginate_by = 20
    
    def get_queryset(self):
        form = DonationSearchForm(self.request.GET)
        queryset = Donation.objects.filter(status='available').select_related('donor__user')
        
        if form.is_valid():
            search = form.cleaned_data.get('search')
            if search:
                queryset = queryset.filter(
                    Q(food_type__icontains=search) |
                    Q(description__icontains=search) |
                    Q(location__icontains=search)
                )
            
            food_type = form.cleaned_data.get('food_type')
            if food_type:
                queryset = queryset.filter(food_type=food_type)
            
            status = form.cleaned_data.get('status')
            if status:
                queryset = queryset.filter(status=status)
            
            location = form.cleaned_data.get('location')
            if location:
                queryset = queryset.filter(location__icontains=location)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = DonationSearchForm(self.request.GET)
        return context


class DonationFulfillView(PantryRequiredMixin, DetailView):
    """Mark a claimed donation as fulfilled"""
    model = Donation
    template_name = 'donations/fulfill.html'
    
    def get_object(self):
        obj = super().get_object()
        if obj.claimed_by != self.request.user.pantry:
            raise Http404("You can only fulfill your own claimed donations.")
        if obj.status != 'claimed':
            raise Http404("This donation is not available for fulfillment.")
        return obj
    
    def post(self, request, *args, **kwargs):
        donation = self.get_object()
        
        # Mark as fulfilled
        donation.status = 'fulfilled'
        donation.save(update_fields=['status'])
        
        messages.success(request, f'Donation "{donation.food_type}" has been marked as fulfilled!')
        return redirect('donations:claimed')
