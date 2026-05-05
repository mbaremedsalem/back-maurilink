from django.db import models

# Create your models here.

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