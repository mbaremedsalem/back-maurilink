from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from .models import User

class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'username','image','cover_image','email', 'first_name', 'last_name', 'user_type', 'phone', 'is_active', 'date_joined')
        export_order = fields
        
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        # Hasher les mots de passe lors de l'import
        for row in dataset:
            if 'password' in row and row['password']:
                from django.contrib.auth.hashers import make_password
                row['password'] = make_password(row['password'])

@admin.register(User)
class CustomUserAdmin(UserAdmin, ImportExportModelAdmin):
    resource_class = UserResource
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'phone', 'is_active', 'date_joined', 'display_image', 'display_cover_image')
    list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    readonly_fields = ('last_login', 'date_joined', 'display_image_in_form')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'phone', 'user_type', 'image', 'cover_image', 'display_image_in_form')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'image', 'cover_image'),
        }),
    )
    
    actions = ['make_active', 'make_inactive', 'export_as_csv']
    
    def display_image(self, obj):
        """Affiche une miniature de l'image dans la liste"""
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />', obj.image.url)
        return format_html('<span style="color: gray;">Aucune image</span>')
    display_image.short_description = 'Image'
    
    def display_cover_image(self, obj):
        """Affiche une miniature de l'image de couverture dans la liste"""
        if obj.cover_image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />', obj.cover_image.url)
        return format_html('<span style="color: gray;">Aucune image de couverture</span>')
    display_cover_image.short_description = 'Image de couverture'
    
    def display_image_in_form(self, obj):
        """Affiche l'image en grand dans le formulaire d'édition"""
        if obj.image:
            return format_html('<img src="{}" width="150" height="150" style="border-radius: 10px; object-fit: cover;" /><br><span style="color: gray;">Image actuelle</span>', obj.image.url)
        return format_html('<span style="color: gray;">Aucune image téléchargée</span>')
    display_image_in_form.short_description = 'Aperçu de l\'image'
    
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Désactiver les utilisateurs sélectionnés"
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Username', 'Email', 'First Name', 'Last Name', 'Type', 'Phone', 'Active'])
        for user in queryset:
            writer.writerow([user.id, user.username, user.email, user.first_name, user.last_name, user.user_type, user.phone, user.is_active])
        return response
    export_as_csv.short_description = "Exporter en CSV"