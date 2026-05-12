from django.urls import path

from applications.email_views import SendAllJobOffersEmailView, SendApplicationsByJobOfferView, SendBatchApplicationsEmailView
from . import views

urlpatterns = [
    path('apply/', views.ApplicationCreateView.as_view(), name='apply'),
    path('my-applications/', views.MyApplicationsView.as_view(), name='my-applications'),
    path('company-applications/', views.CompanyApplicationsView.as_view(), name='company-applications'),
    path('applications/<int:pk>/update-status/', views.UpdateApplicationStatusView.as_view(), name='update-status'),

   # Envoyer des candidatures spécifiques (par IDs)
    path('send-batch/', SendBatchApplicationsEmailView.as_view(), name='send-batch'),
    
    # Envoyer toutes les candidatures d'une offre
    path('send-batch/<int:job_offer_id>/', SendApplicationsByJobOfferView.as_view(), name='send-batch-by-job'),
    
    # Envoyer toutes les candidatures de toutes les offres
    path('send-all/', SendAllJobOffersEmailView.as_view(), name='send-all'),
]