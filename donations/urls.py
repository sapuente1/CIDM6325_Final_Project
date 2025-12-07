# donations/urls.py
from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    # Public donation browsing
    path('', views.DonationListView.as_view(), name='list'),
    path('<uuid:pk>/', views.DonationDetailView.as_view(), name='detail'),
    path('search/', views.DonationSearchView.as_view(), name='search'),
    
    # Donor actions (authentication required)
    path('create/', views.DonationCreateView.as_view(), name='create'),
    path('<uuid:pk>/edit/', views.DonationUpdateView.as_view(), name='update'),
    path('<uuid:pk>/delete/', views.DonationDeleteView.as_view(), name='delete'),
    
    # Pantry actions
    path('<uuid:pk>/claim/', views.DonationClaimView.as_view(), name='claim'),
    path('<uuid:pk>/fulfill/', views.DonationFulfillView.as_view(), name='fulfill'),
    
    # Dashboard and management
    path('my-donations/', views.MyDonationsView.as_view(), name='my_donations'),
    path('my-claims/', views.ClaimedDonationsView.as_view(), name='my_claims'),
    path('claimed/', views.ClaimedDonationsView.as_view(), name='claimed'),
]
