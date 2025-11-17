from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from . import models


class TicketForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=models.Category.objects.all(),
        required=False,
        label="Categoria",
        empty_label="Selecione a categoria"
    )
    subcategory = forms.ModelChoiceField(
        queryset=models.Subcategory.objects.none(),
        required=False,
        label="Subcategoria",
        empty_label="Selecione a subcategoria"
    )
    images = forms.ImageField(
        label="Anexar Imagens",
        widget=forms.FileInput(),
        required=False
    )
    
    class Meta:
        model = models.Ticket
        fields = ('title', 'description', 'category', 'subcategory')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        has_categories = models.Category.objects.exists()
        
        if not has_categories:
            self.fields['category'].widget = forms.HiddenInput()
            self.fields['category'].required = False
            self.fields['subcategory'].widget = forms.HiddenInput()
            self.fields['subcategory'].required = False
        else:
            self.fields['category'].required = True
            
            category_id = None
            
            if 'category' in self.data:
                try:
                    category_id = int(self.data.get('category'))
                except (ValueError, TypeError):
                    pass
            elif self.instance.pk and self.instance.category:
                category_id = self.instance.category.id
                
            if category_id:
                subcats = models.Subcategory.objects.filter(category_id=category_id)
                self.fields['subcategory'].queryset = subcats
                if subcats.exists():
                    self.fields['subcategory'].required = True
                else:
                    self.fields['subcategory'].required = False
            else:
                self.fields['subcategory'].queryset = models.Subcategory.objects.all()
                self.fields['subcategory'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')
        
        if models.Category.objects.exists() and not category:
            self.add_error('category', 'Por favor, selecione uma categoria.')
        
        if category:
            has_subcategories = models.Subcategory.objects.filter(category=category).exists()
            if has_subcategories and not subcategory:
                self.add_error('subcategory', 'Por favor, selecione uma subcategoria.')
        
        return cleaned_data


class PriorityForm(forms.Form):
    priority = forms.ChoiceField(
        choices=models.Ticket.PRIORITY_CHOICES,
        label="Definir Prioridade",
        required=True
    )


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
            'feedback': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Deixe um comentário sobre o atendimento (opcional)...'
            }),
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
