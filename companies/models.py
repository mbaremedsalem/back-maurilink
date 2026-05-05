from django.db import models
from accounts.models import User

class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=200)
    siret = models.CharField(max_length=14, unique=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    description = models.TextField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.company_name    