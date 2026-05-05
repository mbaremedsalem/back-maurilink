from django.urls import path
from . import views

urlpatterns = [
    path('offers/', views.JobOfferListCreateView.as_view(), name='job-offers-list'),
    path('offers/<int:pk>/', views.JobOfferDetailView.as_view(), name='job-offer-detail'),

        # Appels d'offres
    path('rfps/', views.RFPListCreateView.as_view(), name='rfp-list-create'),
    path('rfps/my/', views.CompanyRFPListView.as_view(), name='company-rfps'),
    path('rfps/<int:pk>/', views.RFPDetailView.as_view(), name='rfp-detail'),
    
    # Propositions
    path('proposals/', views.ProposalCreateView.as_view(), name='proposal-create'),
    path('proposals/company/', views.CompanyProposalsListView.as_view(), name='company-proposals'),
    path('proposals/<int:pk>/', views.ProposalDetailView.as_view(), name='proposal-detail'),
]