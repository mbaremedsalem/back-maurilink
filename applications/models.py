# from django.db import models
# from jobs.models import JobOffer
# from accounts.models import User
# from resumes.models import Resume

# class Application(models.Model):
#     STATUS_CHOICES = (
#         ('pending', 'En attente'),
#         ('reviewed', 'Examinée'),
#         ('accepted', 'Acceptée'),
#         ('rejected', 'Refusée'),
#     )
    
#     job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='applications')
#     candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
#     resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='applications')
#     cover_letter = models.TextField()
#     applied_date = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
#     class Meta:
#         unique_together = ['job_offer', 'candidate']  # Un candidat ne peut postuler qu'une fois
    
#     def __str__(self):
#         return f"{self.candidate.username} - {self.job_offer.title}"    

# applications/models.py
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
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications', null=True, blank=True)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='applications', null=True, blank=True)
    cover_letter = models.TextField(blank=True)
    attached_cv = models.FileField(upload_to='applications/cvs/', null=True, blank=True)
    candidate_name = models.CharField(max_length=255, null=True, blank=True)
    candidate_email = models.EmailField(null=True, blank=True)
    candidate_phone = models.CharField(max_length=20, null=True, blank=True)
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        unique_together = ['job_offer', 'candidate']  # Uniquement si candidate existe
    
    def __str__(self):
        if self.candidate:
            return f"{self.candidate.username} - {self.job_offer.title}"
        return f"{self.candidate_name} - {self.job_offer.title}"