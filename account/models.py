from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class EmailConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_confirmation')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Confirmação de E-mail'
        verbose_name_plural = 'Confirmações de E-mail'
    
    def __str__(self):
        return f'Confirmação de {self.user.email}'
    
    def is_valid(self):
        if self.confirmed_at:
            return True
        expiration = self.created_at + timezone.timedelta(hours=24)
        return timezone.now() < expiration
    
    def confirm(self):
        self.confirmed_at = timezone.now()
        self.user.is_active = True
        self.user.save()
        self.save()


class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Recuperação de Senha'
        verbose_name_plural = 'Recuperações de Senha'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Recuperação de senha para {self.user.email}'
    
    def is_valid(self):
        if self.used_at:
            return False
        expiration = self.created_at + timezone.timedelta(hours=1)
        return timezone.now() < expiration
    
    def mark_as_used(self):
        self.used_at = timezone.now()
        self.save()
