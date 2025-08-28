from django import forms
from django.core.exceptions import ValidationError
from . import models

class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['title'].widget.attrs.update({'placeholder': 'Enter ticket title'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Enter ticket description'})
        self.fields['priority'].help_text = 'Select priority level'
        self.fields['picture'].help_text = 'Upload a picture'

    class Meta:
        model = models.Ticket
        fields = 'title', 'description', 'priority','picture', 

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


    '''
    def clean(self):
        cleaned_data = self.cleaned_data
        title = cleaned_data.get('title')
        description = cleaned_data.get('description')

        if title == description:
            msg = ValidationError(
                'Título não pode ser igual à descrição',
                code='invalid'
            )
            self.add_error('title', msg)
            self.add_error('description', msg)

        return super().clean()
    '''