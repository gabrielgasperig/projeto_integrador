from django import forms
from django.core.exceptions import ValidationError
from . import models

class TicketForm(forms.ModelForm):
    picture = forms.ImageField(widget=forms.FileInput(attrs={'accept': 'image/*'}))
    class Meta:
        model = models.Ticket
        fields = 'title', 'description', 'priority','picture', 