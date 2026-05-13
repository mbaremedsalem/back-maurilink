from rest_framework import generics, permissions, status
from rest_framework.response import Response

from advertising import serializers
from .models import Application
from .serializers import ApplicationSerializer
from jobs.models import JobOffer

# applications/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError  # Ajoute cet import
from .models import Application
from .serializers import ApplicationSerializer
from jobs.models import JobOffer



class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    
    def get_parser_classes(self):
        if self.request and self.request.method == 'POST':
            content_type = self.request.content_type
            if content_type and 'multipart' in content_type:
                return [MultiPartParser, FormParser]
        return [JSONParser]
    
    def get_permissions(self):
        return [permissions.AllowAny()]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        job_offer_id = self.request.data.get('job_offer')
        
        try:
            job_offer = JobOffer.objects.get(id=job_offer_id)
        except JobOffer.DoesNotExist:
            raise ValidationError({"detail": "Cette offre d'emploi n'existe pas"})
        
        user = self.request.user
        
        # Cas 1: Utilisateur authentifié avec CV existant
        if user.is_authenticated:
            resume_id = self.request.data.get('resume')
            
            if not resume_id:
                raise ValidationError({"detail": "Vous devez sélectionner un CV"})
            
            # Vérifier si déjà postulé
            if Application.objects.filter(job_offer=job_offer, candidate=user).exists():
                raise ValidationError({"detail": "Vous avez déjà postulé à cette offre"})
            
            # Créer la candidature avec CV existant
            serializer.save(
                candidate=user,
                job_offer=job_offer
            )
        
        # Cas 2: Utilisateur non authentifié avec CV attaché
        else:
            # Vérifier les champs requis
            candidate_email = self.request.data.get('candidate_email')
            candidate_name = self.request.data.get('candidate_name')
            attached_cv = self.request.data.get('attached_cv')
            
            if not candidate_email:
                raise ValidationError({"detail": "L'email est requis"})
            if not candidate_name:
                raise ValidationError({"detail": "Le nom est requis"})
            if not attached_cv:
                raise ValidationError({"detail": "Vous devez joindre un CV"})
            
            # Vérifier si l'email n'a pas déjà postulé
            if Application.objects.filter(
                job_offer=job_offer, 
                candidate_email=candidate_email
            ).exists():
                raise ValidationError({"detail": "Cet email a déjà postulé à cette offre"})
            
            # Créer la candidature sans utilisateur
            serializer.save(
                candidate=None,
                job_offer=job_offer
            )
    
    def create(self, request, *args, **kwargs):
        try:
            # Validation de base avant la création
            if request.user.is_authenticated:
                if not request.data.get('resume'):
                    return Response(
                        {"detail": "Vous devez fournir un resume_id"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                if not request.data.get('attached_cv'):
                    return Response(
                        {"detail": "Vous devez joindre un fichier CV"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return super().create(request, *args, **kwargs)
        
        except ValidationError as e:
            return Response(
                {"detail": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Application.objects.filter(candidate=self.request.user)



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


from rest_framework.views import APIView
class UpdateApplicationStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, pk):
        
        # 1. Vérifier l'entreprise de l'utilisateur
        from companies.models import Company
        try:
            company = Company.objects.get(user=request.user)
        except Company.DoesNotExist:
            return Response({"detail": "Vous n'êtes pas associé à une entreprise"}, status=403)
        
        # 2. Vérifier la candidature
        from applications.models import Application
        try:
            app = Application.objects.get(id=pk)
        except Application.DoesNotExist:
            return Response({"detail": f"Candidature {pk} n'existe pas"}, status=404)
        
        # 3. Maintenant faire la vraie requête
        try:
            application = Application.objects.get(
                id=pk,
                job_offer__company=company
            )
        except Application.DoesNotExist:
            return Response(
                {"detail": f"La candidature {pk} n'appartient pas à votre entreprise"},
                status=404
            )
        
        # 4. Mettre à jour le statut
        new_status = request.data.get('status')
        if new_status:
            application.status = new_status
            application.save()
            print(f"Statut mis à jour: {new_status}")
        
        serializer = ApplicationSerializer(application)
        return Response(serializer.data)