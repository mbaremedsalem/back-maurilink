from django.db import models
from accounts.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200)
    personal_info = models.JSONField(default=dict)  # Nom, prénom, email, téléphone, adresse
    experience = models.JSONField(default=list)     # Liste d'expériences professionnelles
    education = models.JSONField(default=list)      # Liste de formations
    skills = models.JSONField(default=list)         # Liste de compétences
    languages = models.JSONField(default=list)      # Langues parlées
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"CV de {self.user.username} - {self.title}"


