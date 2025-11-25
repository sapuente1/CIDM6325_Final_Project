from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import UpdateView

from .mixins import RateLimitMixin
from .forms import ProfileForm
from .models import Profile


class IndexView(TemplateView):
    """Minimal index landing page for the Accounts app."""

    template_name: str = "accounts/index.html"


class RateLimitedLoginView(RateLimitMixin, auth_views.LoginView):
    """Login view with simple rate limiting."""


class SignupView(RateLimitMixin, CreateView):
    """User registration view using Django's built-in UserCreationForm."""

    form_class = UserCreationForm
    success_url = reverse_lazy("accounts:login")
    template_name: str = "registration/signup.html"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Simple profile update view for avatar uploads."""

    model = Profile
    form_class = ProfileForm
    template_name = "accounts/profile_form.html"

    def get_object(self, queryset=None):  # pragma: no cover - simple
        return self.request.user.profile

    def get_success_url(self):
        return reverse_lazy("accounts:index")
