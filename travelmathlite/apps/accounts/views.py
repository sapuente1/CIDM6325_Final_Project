from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView


class IndexView(TemplateView):
    """Minimal index landing page for the Accounts app."""

    template_name: str = "accounts/index.html"


class SignupView(CreateView):
    """User registration view using Django's built-in UserCreationForm."""

    form_class = UserCreationForm
    success_url = reverse_lazy("accounts:login")
    template_name: str = "registration/signup.html"
