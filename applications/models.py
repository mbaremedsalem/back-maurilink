from django.db import models
from jobs.models import JobOffer
from accounts.models import User
from resumes.models import Resume

class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('reviewed', 'Examinée'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Refusée'),
    )
    
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        unique_together = ['job_offer', 'candidate']  # Un candidat ne peut postuler qu'une fois
    
    def __str__(self):
        return f"{self.candidate.username} - {self.job_offer.title}"    