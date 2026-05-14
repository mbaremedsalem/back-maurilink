
from datetime import datetime, timedelta

import random
import secrets 
from django.db import models
from django.utils import timezone  # ⚠️ IMPORTANT: Utilisez timezone au lieu de datetime



from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('candidate', 'Candidat'),
        ('company', 'Entreprise'),
        ('admin', 'Administrateur'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='candidate')
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='cover_images/', blank=True, null=True)
    def __str__(self):
        return f"{self.username} - {self.user_type}"



class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Utilisez timezone.now() au lieu de datetime.now()
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        # Utilisez timezone.now() pour comparer avec expires_at
        return not self.is_used and timezone.now() < self.expires_at
    
    @staticmethod
    def generate_otp():
        """Génère un code OTP à 4 chiffres"""
        return f"{secrets.randbelow(9000) + 1000}"
    
    def __str__(self):
        return f"{self.user.email} - {self.otp_code} - Expires: {self.expires_at}"     