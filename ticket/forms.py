from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from . import models

class TicketForm(forms.ModelForm):
    picture = forms.ImageField(widget=forms.FileInput(attrs={'accept': 'image/*'}))
    class Meta:
        model = models.Ticket
        fields = 'title', 'description', 'priority','picture',

    def clean(self):
        cleaned_data = self.cleaned_data
        title = cleaned_data.get('title')
        description = cleaned_data.get('description')

        if title == description:
            msg = ValidationError(
                'Primeiro nome não pode ser igual ao segundo',
                code='invalid'
            )
            self.add_error('title', msg)
            self.add_error('description', msg)

        return super().clean()

    def clean_title(self):
        title = self.cleaned_data.get('title')

        if title == 'ABC':
            self.add_error(
                'title',
                ValidationError(
                    'Veio do add_error',
                    code='invalid'
                )
            )

        return title

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True, min_length=3)
    last_name = forms.CharField(required=True, min_length=3)
    email = forms.EmailField()
    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'email', 'username', 'password1', 'password2',
    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            self.add_error('email', ValidationError(
                'Email já cadastrado',
                code='invalid'
)) 

        return email