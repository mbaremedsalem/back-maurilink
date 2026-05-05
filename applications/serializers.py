from rest_framework import serializers
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
        read_only_fields = ['candidate', 'applied_date']  # Retirer 'status' d'ici
        extra_kwargs = {
            'cover_letter': {'required': False},
        }