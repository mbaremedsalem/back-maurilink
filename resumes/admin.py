from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Resume

class ResumeResource(resources.ModelResource):
    class Meta:
        model = Resume
        fields = ('id', 'user__username', 'title', 'skills', 'languages', 'is_default', 'created_at')
        export_order = fields

@admin.register(Resume)
class ResumeAdmin(ImportExportModelAdmin):
    resource_class = ResumeResource
    list_display = ('title', 'user', 'is_default', 'created_at', 'updated_at')
    list_filter = ('is_default', 'created_at', 'user')
    search_fields = ('title', 'user__username', 'user__email', 'skills')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations CV', {
            'fields': ('user', 'title', 'is_default')
        }),
        ('Contenu', {
            'fields': ('personal_info', 'experience', 'education', 'skills', 'languages')
        }),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )