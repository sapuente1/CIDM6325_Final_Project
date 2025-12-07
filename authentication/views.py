from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.models import User
from donations.models import Donor, Pantry
from .forms import DonorRegistrationForm, PantryRegistrationForm
from monitoring.metrics import BusinessMetrics


class CustomLoginView(DjangoLoginView):
    """Custom login view with role-based redirects"""
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect based on user role"""
        user = self.request.user
        if hasattr(user, 'donor'):
            return reverse_lazy('donations:my_donations')
        elif hasattr(user, 'pantry'):
            return reverse_lazy('donations:my_claims')
        elif user.is_staff:
            return reverse_lazy('admin:index')
        else:
            return reverse_lazy('home')
    
    def form_valid(self, form):
        """Add welcome message on successful login"""
        response = super().form_valid(form)
        user = self.request.user
        if hasattr(user, 'donor'):
            messages.success(self.request, f'Welcome back, {user.donor.organization_name}!')
        elif hasattr(user, 'pantry'):
            messages.success(self.request, f'Welcome back, {user.pantry.organization_name}!')
        else:
            messages.success(self.request, f'Welcome back, {user.get_full_name() or user.username}!')
        return response


class CustomLogoutView(DjangoLogoutView):
    """Custom logout view with confirmation message"""
    next_page = 'home'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)


class RegistrationChoiceView(TemplateView):
    """Landing page for choosing registration type"""
    template_name = 'authentication/register_choice.html'


class DonorRegistrationView(CreateView):
    """Registration view for food donors"""
    model = Donor
    form_class = DonorRegistrationForm
    template_name = 'authentication/donor_register.html'
    success_url = reverse_lazy('donations:my_donations')
    
    def form_valid(self, form):
        """Create User and Donor profile, then auto-login"""
        # Create the User instance
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            password=form.cleaned_data['password1']
        )
        
        # Create the Donor profile
        donor = Donor.objects.create(
            user=user,
            organization_name=form.cleaned_data['organization_name'],
            contact_phone=form.cleaned_data['contact_phone'],
            location=form.cleaned_data['location']
        )
        
        # Auto-login the user
        login(self.request, user)
        messages.success(
            self.request, 
            f'Welcome to CFMP, {donor.organization_name}! Your donor account has been created.'
        )
        
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        """Add error message for form validation failures"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class PantryRegistrationView(CreateView):
    """Registration view for food pantries"""
    model = Pantry
    form_class = PantryRegistrationForm
    template_name = 'authentication/pantry_register.html'
    success_url = reverse_lazy('donations:my_claims')
    
    def form_valid(self, form):
        """Create User and Pantry profile, then auto-login"""
        # Create the User instance
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            password=form.cleaned_data['password1']
        )
        
        # Create the Pantry profile
        pantry = Pantry.objects.create(
            user=user,
            organization_name=form.cleaned_data['organization_name'],
            contact_phone=form.cleaned_data['contact_phone'],
            location=form.cleaned_data['location'],
            service_area=form.cleaned_data['service_area'],
            capacity=form.cleaned_data['capacity']
        )
        
        # Auto-login the user
        login(self.request, user)
        messages.success(
            self.request, 
            f'Welcome to CFMP, {pantry.organization_name}! Your pantry account has been created.'
        )
        
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        """Add error message for form validation failures"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProfileRedirectView(TemplateView):
    """Redirect authenticated users to appropriate profile view"""
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:login')
        
        if hasattr(request.user, 'donor'):
            return redirect('donations:my_donations')
        elif hasattr(request.user, 'pantry'):
            return redirect('donations:my_claims')
        elif request.user.is_staff:
            return redirect('admin:index')
        else:
            messages.warning(request, 'Please contact an administrator to set up your account.')
            return redirect('home')
