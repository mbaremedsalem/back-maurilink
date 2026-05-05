# jobs/admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import JobOffer, RequestForProposal, Proposal

# ========== JOB OFFER ==========
class JobOfferResource(resources.ModelResource):
    class Meta:
        model = JobOffer
        fields = ('id', 'company__company_name', 'title', 'description', 'location', 
                 'salary_min', 'salary_max', 'contract_type', 'published_date', 'is_active')
        export_order = fields

@admin.register(JobOffer)
class JobOfferAdmin(ImportExportModelAdmin):
    resource_class = JobOfferResource
    list_display = ('title', 'company', 'location', 'contract_type', 'salary_min', 
                   'salary_max', 'published_date', 'is_active')
    list_filter = ('contract_type', 'is_active', 'published_date', 'company')
    search_fields = ('title', 'description', 'location', 'company__company_name')
    readonly_fields = ('published_date',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('company', 'title', 'description', 'criteria', 'is_active')
        }),
        ('Détails du poste', {
            'fields': ('location', 'contract_type', 'salary_min', 'salary_max')
        }),
        ('Document', {
            'fields': ('job_description_file',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('published_date',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_offers', 'deactivate_offers']
    
    def activate_offers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} offre(s) activée(s)")
    activate_offers.short_description = "Activer les offres sélectionnées"
    
    def deactivate_offers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} offre(s) désactivée(s)")
    deactivate_offers.short_description = "Désactiver les offres sélectionnées"


# ========== REQUEST FOR PROPOSAL ==========
class RequestForProposalResource(resources.ModelResource):
    class Meta:
        model = RequestForProposal
        fields = ('id', 'company__company_name', 'title', 'description', 'location',
                 'contract_type', 'budget_min', 'budget_max', 'submission_deadline',
                 'status', 'is_active', 'published_date')
        export_order = fields

@admin.register(RequestForProposal)
class RequestForProposalAdmin(ImportExportModelAdmin):
    resource_class = RequestForProposalResource
    list_display = ('title', 'company', 'location', 'contract_type', 'budget_min', 
                   'budget_max', 'submission_deadline', 'status', 'is_active')
    list_filter = ('contract_type', 'status', 'is_active', 'published_date', 'company')
    search_fields = ('title', 'description', 'requirements', 'company__company_name')
    readonly_fields = ('published_date',)
    date_hierarchy = 'submission_deadline'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('company', 'title', 'description', 'requirements', 'status', 'is_active')
        }),
        ('Détails du projet', {
            'fields': ('location', 'contract_type', 'budget_min', 'budget_max', 'duration')
        }),
        ('Calendrier', {
            'fields': ('submission_deadline', 'start_date', 'published_date')
        }),
        ('Critères et documents', {
            'fields': ('criteria', 'attachment'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['open_rfps', 'close_rfps', 'cancel_rfps']
    
    def open_rfps(self, request, queryset):
        queryset.update(status='open', is_active=True)
        self.message_user(request, f"{queryset.count()} appel(s) d'offre ouvert(s)")
    open_rfps.short_description = "Ouvrir les appels d'offre sélectionnés"
    
    def close_rfps(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, f"{queryset.count()} appel(s) d'offre fermé(s)")
    close_rfps.short_description = "Fermer les appels d'offre sélectionnés"
    
    def cancel_rfps(self, request, queryset):
        queryset.update(status='cancelled', is_active=False)
        self.message_user(request, f"{queryset.count()} appel(s) d'offre annulé(s)")
    cancel_rfps.short_description = "Annuler les appels d'offre sélectionnés"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Si ce n'est pas superuser, filtrer par ses entreprises
        companies = request.user.company_profile.all()
        if companies:
            return qs.filter(company__in=companies)
        return qs.none()


# ========== PROPOSAL ==========
class ProposalResource(resources.ModelResource):
    candidate_name = resources.Field(attribute='candidate__username', column_name='Candidat')
    candidate_email = resources.Field(attribute='candidate__email', column_name='Email')
    rfp_title = resources.Field(attribute='rfp__title', column_name='Appel offre')
    company_name = resources.Field(attribute='rfp__company__company_name', column_name='Entreprise')
    
    class Meta:
        model = Proposal
        fields = ('id', 'rfp_title', 'company_name', 'candidate_name', 'candidate_email',
                 'proposed_amount', 'proposed_timeline', 'status', 'submitted_date')
        export_order = fields

@admin.register(Proposal)
class ProposalAdmin(ImportExportModelAdmin):
    resource_class = ProposalResource
    list_display = ('id', 'candidate', 'rfp', 'proposed_amount', 'status', 'submitted_date')
    list_filter = ('status', 'submitted_date', 'rfp__contract_type')
    search_fields = ('candidate__username', 'candidate__email', 'rfp__title', 'cover_letter')
    readonly_fields = ('submitted_date',)
    date_hierarchy = 'submitted_date'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('rfp', 'candidate', 'status')
        }),
        ('Proposition', {
            'fields': ('cover_letter', 'proposed_amount', 'proposed_timeline', 'proposal_document')
        }),
        ('Notes internes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('submitted_date',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['accept_proposals', 'reject_proposals', 'shortlist_proposals', 'review_proposals']
    
    def accept_proposals(self, request, queryset):
        queryset.update(status='accepted')
        self.message_user(request, f"{queryset.count()} proposition(s) acceptée(s)")
    accept_proposals.short_description = "Accepter les propositions sélectionnées"
    
    def reject_proposals(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} proposition(s) refusée(s)")
    reject_proposals.short_description = "Refuser les propositions sélectionnées"
    
    def shortlist_proposals(self, request, queryset):
        queryset.update(status='shortlisted')
        self.message_user(request, f"{queryset.count()} proposition(s) présélectionnée(s)")
    shortlist_proposals.short_description = "Présélectionner les propositions"
    
    def review_proposals(self, request, queryset):
        queryset.update(status='reviewed')
        self.message_user(request, f"{queryset.count()} proposition(s) examinée(s)")
    review_proposals.short_description = "Marquer comme examinées"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Si entreprise, voir uniquement les propositions pour ses RFP
        companies = request.user.company_profile.all()
        if companies:
            return qs.filter(rfp__company__in=companies)
        # Si candidat, voir uniquement ses propositions
        return qs.filter(candidate=request.user)
    
    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            # Les entreprises ne peuvent modifier que status et notes
            if request.user.user_type == 'company':
                return ['rfp', 'candidate', 'cover_letter', 'proposed_amount', 
                       'proposed_timeline', 'proposal_document', 'submitted_date']
        return self.readonly_fields
    
    def has_change_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            if request.user.user_type == 'company':
                # Vérifier que l'entreprise possède le RFP
                return obj.rfp.company in request.user.company_profile.all()
            elif request.user.user_type == 'candidate':
                # Le candidat ne peut voir que ses propres propositions
                return obj.candidate == request.user
        return super().has_change_permission(request, obj)