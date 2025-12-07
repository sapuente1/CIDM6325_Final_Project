from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'auth'

urlpatterns = [
    # Registration and profile
    path('register/', views.RegistrationChoiceView.as_view(), name='register'),
    path('register/donor/', views.DonorRegistrationView.as_view(), name='donor_register'),
    path('register/pantry/', views.PantryRegistrationView.as_view(), name='pantry_register'),
    path('choose-role/', views.RegistrationChoiceView.as_view(), name='choose_role'),
    path('profile/', views.ProfileRedirectView.as_view(), name='profile'),
    
    # Django built-in auth views with custom templates
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Password management
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='authentication/password_change.html',
        success_url='/auth/profile/'
    ), name='password_change'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='authentication/password_reset.html'
    ), name='password_reset'),
]