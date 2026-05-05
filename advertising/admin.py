from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Advertisement

class AdvertisementResource(resources.ModelResource):
    class Meta:
        model = Advertisement
        fields = ('id', 'company__company_name', 'title', 'link', 'start_date', 'end_date', 'is_active', 'views_count', 'clicks_count')
        export_order = fields

@admin.register(Advertisement)
class AdvertisementAdmin(ImportExportModelAdmin):
    resource_class = AdvertisementResource
    list_display = ('title', 'company', 'is_active', 'start_date', 'end_date', 'views_count', 'clicks_count')
    list_filter = ('is_active', 'start_date', 'end_date', 'company')
    search_fields = ('title', 'description', 'company__company_name')
    readonly_fields = ('views_count', 'clicks_count', 'created_at')
    
    fieldsets = (
        ('Informations publicité', {
            'fields': ('company', 'title', 'description', 'image', 'link', 'is_active')
        }),
        ('Période', {
            'fields': ('start_date', 'end_date')
        }),
        ('Statistiques', {
            'fields': ('views_count', 'clicks_count', 'created_at')
        }),
    )
    
    actions = ['activate_ads', 'deactivate_ads', 'reset_stats']
    
    def activate_ads(self, request, queryset):
        queryset.update(is_active=True)
    activate_ads.short_description = "Activer les publicités"
    
    def deactivate_ads(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_ads.short_description = "Désactiver les publicités"
    
    def reset_stats(self, request, queryset):
        queryset.update(views_count=0, clicks_count=0)
    reset_stats.short_description = "Réinitialiser les statistiques"