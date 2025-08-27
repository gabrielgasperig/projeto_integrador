from django import forms
from django.core.exceptions import ValidationError
from . import models

class TicketForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = 'title', 'description', 'priority','user', 
