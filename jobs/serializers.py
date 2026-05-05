from rest_framework import serializers
from .models import JobOffer, RequestForProposal, Proposal
from companies.serializers import CompanySerializer
from companies.models import Company



class JobOfferSerializer(serializers.ModelSerializer):
    company_details = CompanySerializer(source='company', read_only=True)
    
    class Meta:
        model = JobOffer
        fields = '__all__'
        read_only_fields = ['company', 'published_date']



class RequestForProposalSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    company_logo = serializers.SerializerMethodField(read_only=True)
    company_id = serializers.IntegerField(source='company.id', read_only=True)
    remaining_days = serializers.SerializerMethodField()
    proposals_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = RequestForProposal
        fields = '__all__'
        read_only_fields = ('company', 'published_date')
    
    def get_remaining_days(self, obj):
        from django.utils import timezone
        if obj.submission_deadline:
            delta = obj.submission_deadline - timezone.now()
            return max(0, delta.days)
        return None
    
    def get_company_logo(self, obj):
        """Retourne l'URL complète du logo de l'entreprise"""
        if obj.company.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.company.logo.url)
            return obj.company.logo.url
        return None
       

# jobs/serializers.py
from rest_framework import serializers
from .models import RequestForProposal, Proposal

class ProposalSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.username', read_only=True)
    candidate_email = serializers.CharField(source='candidate.email', read_only=True)
    rfp_title = serializers.CharField(source='rfp.title', read_only=True)
    
    class Meta:
        model = Proposal
        fields = '__all__'
        read_only_fields = ('candidate', 'submitted_date')
        extra_kwargs = {
            'cover_letter': {'required': False},
            'proposed_amount': {'required': False},
            'proposed_timeline': {'required': False},
            'rfp': {'required': False},
            'proposal_document': {'required': False},
        }
    
    def update(self, instance, validated_data):
        # Pour les entreprises, ne mettre à jour que status et notes
        if 'status' in validated_data or 'notes' in validated_data:
            instance.status = validated_data.get('status', instance.status)
            instance.notes = validated_data.get('notes', instance.notes)
            instance.save()
            return instance
        return super().update(instance, validated_data)