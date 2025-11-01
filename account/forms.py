from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True, min_length=3, label='Nome')
    last_name = forms.CharField(required=True, min_length=3, label='Sobrenome')
    email = forms.EmailField(required=True, label='E-mail')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.help_text = None

    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'email', 'username',
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este e-mail já está cadastrado.', code='invalid')
        return email
    
class RegisterUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        min_length=3, max_length=30, required=True, label='Nome'
    )
    last_name = forms.CharField(
        min_length=3, max_length=30, required=True, label='Sobrenome'
    )
    email = forms.EmailField(required=True)

    password = forms.CharField(
        label="Nova Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Deixe em branco para não alterar.",
        required=False,
    )

    password2 = forms.CharField(
        label="Confirmação da Nova Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        required=False,
    )
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'username',
        )
    def save(self, commit=True):
        user = super().save(commit=False)       
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password != password2:
            self.add_error('password2', ValidationError('As senhas não conferem.'))
        return cleaned_data
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance and self.instance.pk:
            if email != self.instance.email and User.objects.filter(email=email).exists():
                raise ValidationError('Este e-mail já está em uso por outra conta.')
        return email