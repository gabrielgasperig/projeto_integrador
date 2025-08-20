from django.db import models
from django.utils import timezone
# Create your models here.

class Ticket(models.Model):
    title = models.CharField(max_length=50)
    priority = models.CharField(max_length=50)
    description = models.TextField()
    user = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, blank=True)
    ceated_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f'{self.title} | {self.description} | {self.priority}'
