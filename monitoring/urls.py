from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('health/detailed/', views.health_check_detailed, name='health_detailed'),
]