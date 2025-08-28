from django import forms
from django.core.exceptions import ValidationError
from . import models

class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['title'].widget.attrs.update({'placeholder': 'Enter ticket title'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Enter ticket description'})
        self.fields['description'].help_text = 'Enter ticket description'
        self.fields['user'].widget.attrs.update({'placeholder': 'Select user'})

    class Meta:
        model = models.Ticket
        fields = 'title', 'description', 'priority','user', 

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
