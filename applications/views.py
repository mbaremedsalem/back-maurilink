from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Application
from .serializers import ApplicationSerializer
from jobs.models import JobOffer

class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        job_offer_id = self.request.data.get('job_offer')
        job_offer = JobOffer.objects.get(id=job_offer_id)
        
        # Vérifier si le candidat a déjà postulé
        if Application.objects.filter(job_offer=job_offer, candidate=self.request.user).exists():
            return Response(
                {"detail": "Vous avez déjà postulé à cette offre"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(candidate=self.request.user)

class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Application.objects.filter(candidate=self.request.user)

# class CompanyApplicationsView(generics.ListAPIView):
#     serializer_class = ApplicationSerializer
#     permission_classes = [permissions.IsAuthenticated]
    
#     def get_queryset(self):
#         # Vérifier si l'utilisateur est une entreprise
#         if hasattr(self.request.user, 'company_profile'):
#             return Application.objects.filter(job_offer__company=self.request.user.company_profile)
#         return Application.objects.none()

class CompanyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Récupérer toutes les entreprises de l'utilisateur
        companies = getattr(self.request.user, 'company_profile', None)
        
        if companies:
            # companies est un RelatedManager, on peut filtrer avec __in
            return Application.objects.filter(job_offer__company__in=companies.all())
        
        return Application.objects.none()

class UpdateApplicationStatusView(generics.UpdateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Seule l'entreprise propriétaire de l'offre peut modifier le statut
        if hasattr(self.request.user, 'company_profile'):
            return Application.objects.filter(job_offer__company=self.request.user.company_profile)
        return Application.objects.none()