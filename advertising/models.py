from django.db import models
from companies.models import Company

class Advertisement(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='advertisements')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    link = models.URLField()
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    clicks_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title    