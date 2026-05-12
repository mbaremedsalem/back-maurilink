# applications/email_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Count, Q
from .models import Application
from jobs.models import JobOffer
from services.emailjs_service import EmailJSService

class SendBatchApplicationsEmailView(APIView):
    """
    Envoyer les candidatures par email
    - Peut envoyer une ou plusieurs candidatures spécifiques
    - Vérifie que le statut est 'accepted' (ou autre selon paramètre)
    - Les IDs des candidatures sont passés dans le body
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Vérifier user_type
        if request.user.user_type != 'company':
            return Response(
                {'error': 'Seules les entreprises peuvent envoyer des emails'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Récupérer les données depuis le body
            application_ids = request.data.get('application_ids', [])
            to_email = request.data.get('email')
            status_filter = request.data.get('status', 'accepted')  # Par défaut 'accepted'
            
            # Validation des IDs
            if not application_ids:
                return Response(
                    {'error': 'Vous devez fournir au moins un ID de candidature (application_ids)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validation de l'email
            if not to_email:
                # Récupérer l'email de l'utilisateur connecté
                to_email = request.user.email
                if not to_email:
                    return Response(
                        {'error': 'Email non fourni et utilisateur sans email'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Récupérer les candidatures
            applications = Application.objects.filter(
                id__in=application_ids,
                job_offer__company__user=request.user  # Vérifier que l'entreprise possède les offres
            )
            
            # Vérifier que toutes les candidatures existent
            if len(applications) != len(application_ids):
                found_ids = list(applications.values_list('id', flat=True))
                missing_ids = [id for id in application_ids if id not in found_ids]
                return Response(
                    {'error': f'Candidatures non trouvées ou non autorisées: {missing_ids}'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Filtrer par statut si demandé
            if status_filter:
                applications = applications.filter(status=status_filter)
                if not applications.exists():
                    return Response(
                        {'error': f'Aucune candidature avec le statut "{status_filter}" trouvée'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Grouper par offre d'emploi pour l'envoi
            from collections import defaultdict
            applications_by_job = defaultdict(list)
            
            for app in applications:
                applications_by_job[app.job_offer].append(app)
            
            # Envoyer un email par offre
            email_service = EmailJSService()
            success_count = 0
            results = []
            
            for job_offer, job_applications in applications_by_job.items():
                success = email_service.send_applications_batch(
                    to_email=to_email,
                    job_offer=job_offer,
                    applications=job_applications
                )
                
                if success:
                    success_count += 1
                    results.append({
                        'job_offer_id': job_offer.id,
                        'job_title': job_offer.title,
                        'applications_count': len(job_applications),
                        'sent': True
                    })
                else:
                    results.append({
                        'job_offer_id': job_offer.id,
                        'job_title': job_offer.title,
                        'applications_count': len(job_applications),
                        'sent': False
                    })
            
            if success_count > 0:
                return Response({
                    'success': True,
                    'message': f'{success_count} email(s) envoyé(s) avec succès à {to_email}',
                    'total_applications': len(applications),
                    'results': results
                })
            else:
                return Response({
                    'error': 'Erreur lors de l\'envoi des emails',
                    'results': results
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response(
                {'error': f'Erreur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SendApplicationsByJobOfferView(APIView):
    """
    Envoyer toutes les candidatures d'une offre spécifique par email
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, job_offer_id):
        # Vérifier user_type
        if request.user.user_type != 'company':
            return Response(
                {'error': 'Seules les entreprises peuvent envoyer des emails'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Récupérer l'offre
            job_offer = JobOffer.objects.get(id=job_offer_id)
            company = request.user.company_profile.first()
            
            if not company or job_offer.company != company:
                return Response(
                    {'error': 'Offre non trouvée ou non autorisée'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Récupérer l'email de destination
            to_email = request.data.get('email')
            if not to_email:
                to_email = request.user.email
                if not to_email:
                    return Response(
                        {'error': 'Email non fourni'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Récupérer les candidatures avec filtre de statut optionnel
            status_filter = request.data.get('status', 'accepted')
            applications = Application.objects.filter(job_offer=job_offer)
            
            if status_filter:
                applications = applications.filter(status=status_filter)
            
            if not applications.exists():
                return Response(
                    {'error': f'Aucune candidature trouvée avec le statut "{status_filter}"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Envoyer l'email
            email_service = EmailJSService()
            success = email_service.send_applications_batch(
                to_email=to_email,
                job_offer=job_offer,
                applications=applications
            )
            
            if success:
                return Response({
                    'success': True,
                    'message': f'Email envoyé avec succès à {to_email}',
                    'job_offer': job_offer.title,
                    'applications_count': applications.count()
                })
            else:
                return Response(
                    {'error': 'Erreur lors de l\'envoi de l\'email'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except JobOffer.DoesNotExist:
            return Response(
                {'error': 'Offre d\'emploi non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SendAllJobOffersEmailView(APIView):
    """Envoyer les candidatures de toutes les offres de l'entreprise"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'company':
            return Response(
                {'error': 'Seules les entreprises peuvent envoyer des emails'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        company = request.user.company_profile.first()
        if not company:
            return Response(
                {'error': 'Profil entreprise non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Récupérer l'email de destination
        to_email = request.data.get('email')
        if not to_email:
            to_email = request.user.email
            if not to_email:
                return Response(
                    {'error': 'Email non fourni'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Récupérer le filtre de statut
        status_filter = request.data.get('status', 'accepted')
        
        # Récupérer toutes les offres avec candidatures
        job_offers = JobOffer.objects.filter(company=company)
        
        results = []
        email_service = EmailJSService()
        total_applications = 0
        
        for job_offer in job_offers:
            applications = Application.objects.filter(job_offer=job_offer)
            
            if status_filter:
                applications = applications.filter(status=status_filter)
            
            if applications.exists():
                total_applications += applications.count()
                success = email_service.send_applications_batch(
                    to_email=to_email,
                    job_offer=job_offer,
                    applications=applications
                )
                
                results.append({
                    'job_offer_id': job_offer.id,
                    'job_title': job_offer.title,
                    'applications_count': applications.count(),
                    'sent': success
                })
        
        if total_applications == 0:
            return Response(
                {'error': f'Aucune candidature trouvée avec le statut "{status_filter}"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'success': True,
            'sent_to': to_email,
            'total_applications': total_applications,
            'results': results
        })