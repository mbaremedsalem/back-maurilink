from rest_framework import serializers  # C'est important !
from .models import Application
from jobs.serializers import JobOfferSerializer
from resumes.serializers import ResumeSerializer
from accounts.serializers import UserSerializer

class ApplicationSerializer(serializers.ModelSerializer):
    job_details = JobOfferSerializer(source='job_offer', read_only=True)
    candidate_details = UserSerializer(source='candidate', read_only=True)
    resume_details = ResumeSerializer(source='resume', read_only=True)
    
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['candidate', 'applied_date', 'status']
        extra_kwargs = {
            'cover_letter': {'required': False},
            'attached_cv': {'required': False},
            'resume': {'required': False},
            'candidate_name': {'required': False},
            'candidate_email': {'required': False},
            'candidate_phone': {'required': False},
        }
    
    def validate_resume(self, value):
        """Validation spécifique pour le resume"""
        request = self.context.get('request')
        
        if request and request.user and request.user.is_authenticated:
            if value and value.user != request.user:
                raise serializers.ValidationError(  # Maintenant ça fonctionne
                    f"Ce CV n'appartient pas à l'utilisateur connecté"
                )
        return value
    
    def validate(self, data):
        request = self.context.get('request')
        
        # Vérifier si request existe et si l'utilisateur est authentifié
        if request and request.user and request.user.is_authenticated:
            # Utilisateur authentifié - doit fournir un resume
            resume = data.get('resume')
            
            if not resume:
                raise serializers.ValidationError({
                    "resume": "Vous devez sélectionner un CV"
                })
            
            # S'assurer que les champs non authentifiés sont vides
            data.pop('attached_cv', None)
            data.pop('candidate_name', None)
            data.pop('candidate_email', None)
            data.pop('candidate_phone', None)
        
        else:
            # Utilisateur non authentifié - doit fournir CV fichier + infos
            attached_cv = data.get('attached_cv')
            candidate_name = data.get('candidate_name')
            candidate_email = data.get('candidate_email')
            
            if not attached_cv:
                raise serializers.ValidationError({
                    "attached_cv": "Vous devez joindre un CV"
                })
            if not candidate_name:
                raise serializers.ValidationError({
                    "candidate_name": "Le nom est requis"
                })
            if not candidate_email:
                raise serializers.ValidationError({
                    "candidate_email": "L'email est requis"
                })
            
            # S'assurer que resume est None pour les non authentifiés
            data['resume'] = None
        
        return data
    

    # applications/serializers.py
from rest_framework import serializers
from .models import Application
from jobs.serializers import JobOfferSerializer
from resumes.serializers import ResumeSerializer
from accounts.serializers import UserSerializer

class ApplicationDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les applications avec toutes les informations"""
    
    # Informations du job
    job_details = JobOfferSerializer(source='job_offer', read_only=True)
    
    # Informations du candidat (si connecté)
    candidate_details = UserSerializer(source='candidate', read_only=True)
    
    # Informations du CV (si existe)
    resume_details = ResumeSerializer(source='resume', read_only=True)
    
    # Ajouter l'URL du CV attaché
    attached_cv_url = serializers.SerializerMethodField()
    
    # Ajouter le statut en texte lisible
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id',
            'job_offer',
            'job_details',
            'candidate',
            'candidate_details',
            'candidate_name',
            'candidate_email',
            'candidate_phone',
            'resume',
            'resume_details',
            'attached_cv',
            'attached_cv_url',
            'cover_letter',
            'applied_date',
            'status',
            'status_display',
        ]
        read_only_fields = ['applied_date']
    
    def get_attached_cv_url(self, obj):
        """Retourne l'URL du CV attaché s'il existe"""
        if obj.attached_cv:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attached_cv.url)
            return obj.attached_cv.url
        return None


class ApplicationListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des applications"""
    candidate_name_display = serializers.SerializerMethodField()
    candidate_email_display = serializers.SerializerMethodField()
    has_resume = serializers.BooleanField(read_only=True)
    has_attached_cv = serializers.BooleanField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id',
            'candidate_name_display',
            'candidate_email_display',
            'applied_date',
            'status',
            'status_display',
            'has_resume',
            'has_attached_cv',
        ]
    
    def get_candidate_name_display(self, obj):
        """Retourne le nom du candidat (compte ou anonyme)"""
        if obj.candidate:
            return obj.candidate.get_full_name() or obj.candidate.username
        return obj.candidate_name or "Candidat anonyme"
    
    def get_candidate_email_display(self, obj):
        """Retourne l'email du candidat (compte ou anonyme)"""
        if obj.candidate:
            return obj.candidate.email
        return obj.candidate_email or "Email non fourni"