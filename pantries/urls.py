# pantries/urls.py
from django.urls import path
from . import views

app_name = 'pantries'
urlpatterns = [
    path('<int:pk>/', views.PantryDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PantryUpdateView.as_view(), name='update'),
]
