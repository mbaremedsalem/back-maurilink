from django.db import models
from companies.models import Company

class JobOffer(models.Model):
    CONTRACT_TYPES = (
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
        ('FREELANCE', 'Freelance'),
        ('STAGE', 'Stage'),
        ('ALTERNANCE', 'Alternance'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_offers')
    title = models.CharField(max_length=200)
    description = models.TextField()
    criteria = models.JSONField(default=dict)  # Stocker les critères de recherche
    location = models.CharField(max_length=200)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES)
    published_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    # Ajouter ce champ pour le document PDF
    job_description_file = models.FileField(upload_to='job_descriptions/', blank=True, null=True, help_text="PDF contenant la description détaillée du poste")
    def __str__(self):
        return f"{self.title} - {self.company.company_name}"



class RequestForProposal(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Brouillon'),
        ('open', 'Ouvert'),
        ('closed', 'Fermé'),
        ('cancelled', 'Annulé'),
    )
    
    # Relations
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='rfps')
    
    # Informations générales
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(help_text="Prérequis et exigences pour les candidats")
    
    # Détails
    location = models.CharField(max_length=200)
    contract_type = models.CharField(max_length=20, choices=JobOffer.CONTRACT_TYPES)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Dates
    published_date = models.DateTimeField(auto_now_add=True)
    submission_deadline = models.DateTimeField(help_text="Date limite de soumission des candidatures")
    start_date = models.DateField(null=True, blank=True)
    duration = models.CharField(max_length=100, blank=True, help_text="Durée du contrat/mission")
    
    # Critères et statut
    criteria = models.JSONField(default=dict, help_text="Critères d'évaluation des candidats")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)
    
    # Documents
    attachment = models.FileField(upload_to='rfp_attachments/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} - {self.company.company_name}"
    
    class Meta:
        ordering = ['-published_date']
        verbose_name = "Appel d'offre"
        verbose_name_plural = "Appels d'offres"

class Proposal(models.Model):
    """Proposition de candidature pour un appel d'offre"""
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('reviewed', 'Examinée'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Refusée'),
        ('shortlisted', 'Présélectionnée'),
    )
    
    # Relations
    rfp = models.ForeignKey(RequestForProposal, on_delete=models.CASCADE, related_name='proposals')
    candidate = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='proposals')
    
    # Contenu de la proposition
    cover_letter = models.TextField()
    proposed_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Montant proposé")
    proposed_timeline = models.CharField(max_length=200, help_text="Délai proposé pour réaliser la mission")
    
    # Documents
    proposal_document = models.FileField(upload_to='proposals/', blank=True, null=True)
    
    # Métadonnées
    submitted_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, help_text="Notes internes de l'entreprise")
    
    class Meta:
        unique_together = ['rfp', 'candidate']  # Un candidat ne peut postuler qu'une fois par appel d'offre
        ordering = ['-submitted_date']
    
    def __str__(self):
        return f"{self.candidate.username} - {self.rfp.title}"