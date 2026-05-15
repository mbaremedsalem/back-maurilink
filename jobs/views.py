from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from companies.models import Company
from .models import JobOffer
from .serializers import JobOfferSerializer

# class JobOfferListCreateView(generics.ListCreateAPIView):
#     serializer_class = JobOfferSerializer
#     filter_backends = [filters.SearchFilter, filters.OrderingFilter]
#     search_fields = ['title', 'description', 'location', 'contract_type']
#     ordering_fields = ['published_date', 'salary_min', 'salary_max']
    
#     def get_permissions(self):
#         """
#         Permissions différentes selon l'action :
#         - GET : tout le monde peut voir les offres (même non authentifié)
#         - POST : seulement les entreprises authentifiées
#         """
#         if self.request.method == 'GET':
#             return [permissions.AllowAny()]  # Tout le monde peut voir les offres
#         elif self.request.method == 'POST':
#             return [permissions.IsAuthenticated()]  # Authentification requise pour créer
#         return [permissions.IsAuthenticated()]
    
#     def get_queryset(self):
#         queryset = JobOffer.objects.filter(is_active=True)
        
#         # Filtrer par type de contrat
#         contract_type = self.request.query_params.get('contract_type')
#         if contract_type:
#             queryset = queryset.filter(contract_type=contract_type)
        
#         # Filtrer par localisation
#         location = self.request.query_params.get('location')
#         if location:
#             queryset = queryset.filter(location__icontains=location)
        
#         # Filtrer par salaire minimum
#         salary_min = self.request.query_params.get('salary_min')
#         if salary_min:
#             queryset = queryset.filter(salary_min__gte=salary_min)
        
#         # Filtrer par salaire maximum
#         salary_max = self.request.query_params.get('salary_max')
#         if salary_max:
#             queryset = queryset.filter(salary_max__lte=salary_max)
        
#         return queryset
    
#     def perform_create(self, serializer):
#         # Vérifier si l'utilisateur a un profil entreprise
#         if not hasattr(self.request.user, 'company_profile'):
#             raise PermissionDenied("Vous devez avoir un profil entreprise pour créer une offre")
        
#         # Vérifier si l'utilisateur est bien de type entreprise
#         if self.request.user.user_type != 'company':
#             raise PermissionDenied("Seuls les comptes entreprise peuvent créer des offres")
        
#         serializer.save(company=self.request.user.company_profile)


class JobOfferListCreateView(generics.ListCreateAPIView):
    serializer_class = JobOfferSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location', 'contract_type']
    ordering_fields = ['published_date', 'salary_min', 'salary_max']
    
    def get_permissions(self):
        """
        Permissions différentes selon l'action :
        - GET : tout le monde peut voir les offres (même non authentifié)
        - POST : seulement les entreprises authentifiées
        """
        if self.request.method == 'GET':
            return [permissions.AllowAny()]  # Tout le monde peut voir les offres
        elif self.request.method == 'POST':
            return [permissions.IsAuthenticated()]  # Authentification requise pour créer
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = JobOffer.objects.filter(is_active=True)
        
        # Filtrer par type de contrat
        contract_type = self.request.query_params.get('contract_type')
        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)
        
        # Filtrer par localisation
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Filtrer par salaire minimum
        salary_min = self.request.query_params.get('salary_min')
        if salary_min:
            queryset = queryset.filter(salary_min__gte=salary_min)
        
        # Filtrer par salaire maximum
        salary_max = self.request.query_params.get('salary_max')
        if salary_max:
            queryset = queryset.filter(salary_max__lte=salary_max)
        
        return queryset
    
    def perform_create(self, serializer):
        # Vérifier si l'utilisateur a un profil entreprise
        # Attention : company_profile est un RelatedManager, pas une instance unique
        companies = self.request.user.company_profile.all()
        
        if not companies.exists():
            raise PermissionDenied("Vous devez avoir un profil entreprise pour créer une offre")
        
        # Vérifier si l'utilisateur est bien de type entreprise
        if self.request.user.user_type != 'company':
            raise PermissionDenied("Seuls les comptes entreprise peuvent créer des offres")
        
        # Prendre la première entreprise associée (ou gérez selon votre logique métier)
        company_instance = companies.first()
        
        serializer.save(company=company_instance)

class JobOfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobOfferSerializer
    permission_classes = [permissions.AllowAny]  # Correction: pas de parenthèses
    # ou permission_classes = []  # Alternative: liste vide
    
    def get_queryset(self):
        # Retourne toutes les offres actives pour tout le monde
        return JobOffer.objects.filter(is_active=True)
    
    def perform_update(self, serializer):
        # Si tu veux garder une logique métier lors de la mise à jour
        # Par exemple, vérifier que l'utilisateur est bien le propriétaire
        if hasattr(self.request.user, 'user_type') and self.request.user.user_type == 'company':
            serializer.save()
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seules les entreprises peuvent modifier les offres")
    
    def perform_destroy(self, instance):
        # Logique pour la suppression
        if hasattr(self.request.user, 'user_type') and self.request.user.user_type == 'company':
            instance.delete()
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seules les entreprises peuvent supprimer les offres")

     
    
# jobs/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q
from .models import JobOffer
from .serializers import JobOfferSerializer
from applications.models import Application
from applications.serializers import ApplicationDetailSerializer

class CompanyJobOffersView(generics.ListAPIView):
    """
    API qui retourne toutes les offres d'emploi de l'entreprise connectée
    avec toutes les informations des candidatures pour chaque offre
    """
    serializer_class = JobOfferSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Vérifier que l'utilisateur est une entreprise
        if self.request.user.user_type != 'company':
            return JobOffer.objects.none()
        
        # Récupérer la première entreprise de l'utilisateur
        company = self.request.user.company_profile.first()
        if not company:
            return JobOffer.objects.none()
        
        # Retourner les offres de cette entreprise
        return JobOffer.objects.filter(company=company)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Récupérer toutes les offres avec leurs statistiques
        offers_data = []
        
        for job_offer in queryset:
            # Récupérer toutes les candidatures pour cette offre
            applications = Application.objects.filter(job_offer=job_offer).order_by('-applied_date')
            
            # Statistiques des candidatures
            stats = {
                'total': applications.count(),
                'pending': applications.filter(status='pending').count(),
                'reviewed': applications.filter(status='reviewed').count(),
                'accepted': applications.filter(status='accepted').count(),
                'rejected': applications.filter(status='rejected').count(),
            }
            
            # Sérialiser les candidatures avec toutes les informations
            applications_data = ApplicationDetailSerializer(
                applications, 
                many=True, 
                context={'request': request}
            ).data
            
            # Sérialiser l'offre
            offer_serializer = self.get_serializer(job_offer)
            
            offers_data.append({
                'offer_details': offer_serializer.data,
                'applications_stats': stats,
                'applications': applications_data
            })
        
        company = request.user.company_profile.first()
        
        return Response({
            'company_name': company.company_name if company else None,
            'total_offers': queryset.count(),
            'total_applications': sum(len(offer['applications']) for offer in offers_data),
            'offers': offers_data
        })

#----- appel doffre -----#
# jobs/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from .models import RequestForProposal, Proposal
from .serializers import RequestForProposalSerializer, ProposalSerializer

class RFPListCreateView(generics.ListCreateAPIView):
    """Liste tous les appels d'offres actifs ou crée un nouvel appel d'offre"""
    serializer_class = RequestForProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = RequestForProposal.objects.filter(is_active=True, status='open')
        
        # Filtrer par entreprise
        company_id = self.request.query_params.get('company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filtrer par type de contrat
        contract_type = self.request.query_params.get('contract_type')
        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)
        
        # Filtrer par localisation
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        return queryset
    
    def perform_create(self, serializer):
        companies = self.request.user.company_profile.all()
        
        if not companies.exists():
            raise PermissionDenied("Vous devez avoir au moins un profil entreprise")
        
        if self.request.user.user_type != 'company':
            raise PermissionDenied("Seuls les comptes entreprise peuvent créer des appels d'offres")
        
        company_id = self.request.data.get('company_id')
        
        if not company_id and companies.count() == 1:
            company = companies.first()
        elif company_id:
            try:
                company = companies.get(id=company_id)
            except Company.DoesNotExist:
                raise PermissionDenied("Entreprise non trouvée")
        else:
            raise PermissionDenied("Vous devez spécifier company_id")
        
        serializer.save(company=company)

class CompanyRFPListView(generics.ListAPIView):
    """Récupère tous les appels d'offres d'une entreprise spécifique"""
    serializer_class = RequestForProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        companies = self.request.user.company_profile.all()
        
        if not companies.exists():
            return RequestForProposal.objects.none()
        
        return RequestForProposal.objects.filter(company__in=companies)

# class RFPDetailView(generics.RetrieveUpdateDestroyAPIView):
#     """Détail, modification ou suppression d'un appel d'offre"""
#     serializer_class = RequestForProposalSerializer
#     permission_classes = [permissions.AllowAny] 
    
#     def get_queryset(self):
#         user = self.request.user
        
#         if user.user_type == 'company':
#             companies = user.company_profile.all()
#             return RequestForProposal.objects.filter(company__in=companies)
#         else:
#             return RequestForProposal.objects.filter(is_active=True, status='open')
    
#     def perform_update(self, serializer):
#         rfp = self.get_object()
        
#         # Vérifier que l'entreprise propriétaire fait la modification
#         if rfp.company not in self.request.user.company_profile.all():
#             raise PermissionDenied("Vous n'êtes pas autorisé à modifier cet appel d'offre")
        
#         serializer.save()
    
#     def perform_destroy(self, instance):
#         if instance.company not in self.request.user.company_profile.all():
#             raise PermissionDenied("Vous n'êtes pas autorisé à supprimer cet appel d'offre")
        
#         instance.is_active = False
#         instance.status = 'cancelled'
#         instance.save()


from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import RequestForProposal
from .serializers import RequestForProposalSerializer

class RFPDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification ou suppression d'un appel d'offre"""
    serializer_class = RequestForProposalSerializer
    permission_classes = [permissions.AllowAny] 
    
    def get_queryset(self):
        user = self.request.user
        
        # Vérifier si l'utilisateur est authentifié
        if user.is_authenticated and user.user_type == 'company':
            # Utilisateur connecté et de type entreprise
            companies = user.company_profile.all()
            return RequestForProposal.objects.filter(company__in=companies)
        else:
            # Utilisateur non connecté ou non entreprise
            # Retourner uniquement les RFPs actifs et ouverts
            return RequestForProposal.objects.filter(is_active=True, status='open')
    
    def perform_update(self, serializer):
        rfp = self.get_object()
        user = self.request.user
        
        # Vérifier que l'utilisateur est authentifié et est une entreprise
        if not user.is_authenticated or user.user_type != 'company':
            raise PermissionDenied("Vous devez être connecté en tant qu'entreprise pour modifier un appel d'offre")
        
        # Vérifier que l'entreprise propriétaire fait la modification
        if rfp.company not in user.company_profile.all():
            raise PermissionDenied("Vous n'êtes pas autorisé à modifier cet appel d'offre")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        user = self.request.user
        
        # Vérifier que l'utilisateur est authentifié et est une entreprise
        if not user.is_authenticated or user.user_type != 'company':
            raise PermissionDenied("Vous devez être connecté en tant qu'entreprise pour supprimer un appel d'offre")
        
        # Vérifier que l'entreprise propriétaire fait la suppression
        if instance.company not in user.company_profile.all():
            raise PermissionDenied("Vous n'êtes pas autorisé à supprimer cet appel d'offre")
        
        instance.is_active = False
        instance.status = 'cancelled'
        instance.save()

class ProposalCreateView(generics.CreateAPIView):
    """Postuler à un appel d'offre (pour les candidats)"""
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Vérifier que l'utilisateur est un candidat
        if self.request.user.user_type != 'candidate':
            raise PermissionDenied("Seuls les candidats peuvent postuler aux appels d'offres")
        
        rfp_id = self.request.data.get('rfp')
        
        try:
            rfp = RequestForProposal.objects.get(id=rfp_id, is_active=True, status='open')
        except RequestForProposal.DoesNotExist:
            raise ValidationError("Appel d'offre introuvable ou non disponible")
        
        # Vérifier la date limite
        if rfp.submission_deadline < timezone.now():
            raise ValidationError("La date limite de soumission est dépassée")
        
        # Vérifier si le candidat a déjà postulé
        if Proposal.objects.filter(rfp=rfp, candidate=self.request.user).exists():
            raise ValidationError("Vous avez déjà postulé à cet appel d'offre")
        
        serializer.save(rfp=rfp, candidate=self.request.user)

class CompanyProposalsListView(generics.ListAPIView):
    """Récupérer toutes les propositions reçues pour les appels d'offres d'une entreprise"""
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Vérifier que l'utilisateur est une entreprise
        if self.request.user.user_type != 'company':
            return Proposal.objects.none()
        
        companies = self.request.user.company_profile.all()
        
        if not companies.exists():
            return Proposal.objects.none()
        
        # Récupérer tous les RFP des entreprises de l'utilisateur
        rfps = RequestForProposal.objects.filter(company__in=companies)
        
        # Filtrer par RFP spécifique si demandé
        rfp_id = self.request.query_params.get('rfp_id')
        if rfp_id:
            rfps = rfps.filter(id=rfp_id)
        
        # Filtrer par statut
        status_filter = self.request.query_params.get('status')
        if status_filter:
            return Proposal.objects.filter(rfp__in=rfps, status=status_filter)
        
        return Proposal.objects.filter(rfp__in=rfps)

class ProposalDetailView(generics.RetrieveUpdateAPIView):
    """Détail et mise à jour du statut d'une proposition"""
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'company':
            # L'entreprise peut voir toutes les propositions de ses RFP
            companies = user.company_profile.all()
            rfps = RequestForProposal.objects.filter(company__in=companies)
            return Proposal.objects.filter(rfp__in=rfps)
        else:
            # Le candidat ne voit que ses propres propositions
            return Proposal.objects.filter(candidate=user)
    
    def perform_update(self, serializer):
        proposal = self.get_object()
        user = self.request.user
        
        # Seule l'entreprise peut changer le statut
        if user.user_type == 'company':
            # Vérifier que l'entreprise possède le RFP
            if proposal.rfp.company not in user.company_profile.all():
                raise PermissionDenied("Vous n'êtes pas autorisé à modifier cette proposition")
            
            # Permettre seulement la mise à jour du statut et des notes
            allowed_fields = ['status', 'notes']
            data = {k: v for k, v in self.request.data.items() if k in allowed_fields}
            
            serializer.save(**data)
        else:
            raise PermissionDenied("Seules les entreprises peuvent modifier le statut des propositions") 