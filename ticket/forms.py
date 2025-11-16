from django import forms
from . import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from . import models

class TicketForm(forms.ModelForm):
    images = forms.ImageField(
        label="Anexar Imagens",
        widget=forms.FileInput(),
        required=False
    )
    class Meta:
        model = models.Ticket
        fields = 'title', 'description',

class AdminSetPriorityForm(forms.Form):
    priority = forms.ChoiceField(
        choices=models.Ticket.PRIORITY_CHOICES,
        label="Definir Prioridade",
        required=True
    )

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError('O título precisa ter pelo menos 5 caracteres.', code='invalid')
        return title

class ConcludeTicketForm(forms.Form):
    solution = forms.CharField(
        label="Solução do Problema",
        required=True,
        widget=forms.Textarea(
            attrs={
                'rows': 4,
                'placeholder': 'Descreva detalhadamente a solução aplicada para este ticket.'
            }
        )
    )

class DeleteTicketForm(forms.Form):
    reason = forms.CharField(
        label="Motivo da Exclusão",
        required=True,
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'placeholder': 'Descreva por que este ticket está sendo excluído.'
            }
        )
    )

class RatingForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
  
        fields = ['rating', 'feedback']

        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'feedback': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Deixe um comentário sobre o atendimento (opcional)...'}),
        }

        labels = {
            'rating': 'A sua avaliação sobre o atendimento',
            'feedback': 'Comentário Adicional',
        }

class TransferTicketForm(forms.Form):

    new_admin = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        label="Transferir para:",
        empty_label="Selecione um novo responsável",
        to_field_name=None
    )

    def __init__(self, *args, **kwargs):
        current_admin = kwargs.pop('current_admin', None)
        super().__init__(*args, **kwargs)
        if current_admin:
            self.fields['new_admin'].queryset = User.objects.filter(is_staff=True).exclude(pk=current_admin.pk)
        self.fields['new_admin'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}".strip() or obj.username

class TicketEventForm(forms.Form):
    comment_text = forms.CharField(
        label="Comentário",
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Digite o seu comentário aqui...'
        }),
        required=True
    )
    images = forms.ImageField(
        label="Anexar Imagens",
        widget=forms.FileInput(),
        required=False
    )