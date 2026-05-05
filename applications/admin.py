from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Application

class ApplicationResource(resources.ModelResource):
    class Meta:
        model = Application
        fields = ('id', 'job_offer__title', 'candidate__username', 'resume__title', 'status', 'applied_date')
        export_order = fields

@admin.register(Application)
class ApplicationAdmin(ImportExportModelAdmin):
    resource_class = ApplicationResource
    list_display = ('job_offer', 'candidate', 'status', 'applied_date')
    list_filter = ('status', 'applied_date', 'job_offer__company')
    search_fields = ('job_offer__title', 'candidate__username', 'candidate__email', 'cover_letter')
    readonly_fields = ('applied_date',)
    
    fieldsets = (
        ('Informations candidature', {
            'fields': ('job_offer', 'candidate', 'resume', 'cover_letter', 'status')
        }),
        ('Dates', {'fields': ('applied_date',)}),
    )
    
    actions = ['mark_as_reviewed', 'mark_as_accepted', 'mark_as_rejected']
    
    def mark_as_reviewed(self, request, queryset):
        queryset.update(status='reviewed')
    mark_as_reviewed.short_description = "Marquer comme examinée"
    
    def mark_as_accepted(self, request, queryset):
        queryset.update(status='accepted')
    mark_as_accepted.short_description = "Marquer comme acceptée"
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_as_rejected.short_description = "Marquer comme refusée"