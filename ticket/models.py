from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Priority(models.Model):
    class Meta:
        verbose_name = 'Priority'
        verbose_name_plural = 'Priorities'        

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    title = models.CharField(max_length=50)
    priority = models.ForeignKey(
        Priority, 
        on_delete=models.SET_NULL, 
        blank=True, null=True)
    user = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    show = models.BooleanField(default=True)
    picture = models.ImageField(blank=True, upload_to='pictures/%Y/%m/')
    owner = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, null=True)
    
    def __str__(self):
        return f'{self.title} | {self.description} | {self.priority}'
