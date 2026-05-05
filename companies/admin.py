from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Company

class CompanyResource(resources.ModelResource):
    class Meta:
        model = Company
        fields = ('id', 'user__username', 'company_name', 'siret', 'website', 'description', 'address', 'created_at')
        export_order = fields

@admin.register(Company)
class CompanyAdmin(ImportExportModelAdmin):
    resource_class = CompanyResource
    list_display = ('company_name', 'user', 'siret', 'website', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('company_name', 'siret', 'user__username', 'user__email')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Informations entreprise', {
            'fields': ('user', 'company_name', 'siret', 'logo', 'website', 'description', 'address')
        }),
        ('Dates', {'fields': ('created_at',)}),
    )