from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

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
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not first_name.replace(' ', '').isalpha():
            raise ValidationError('O nome deve conter apenas letras.')
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not last_name.replace(' ', '').isalpha():
            raise ValidationError('O sobrenome deve conter apenas letras.')
        return last_name
    
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
    email = forms.EmailField(required=True, label='E-mail')
    
    username = forms.CharField(
        label='Nome de Usuário',
        disabled=True,
        help_text='O nome de usuário não pode ser alterado.'
    )

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
        if self.instance and self.instance.pk:
            user.username = self.instance.username
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
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not first_name.replace(' ', '').isalpha():
            raise ValidationError('O nome deve conter apenas letras.')
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not last_name.replace(' ', '').isalpha():
            raise ValidationError('O sobrenome deve conter apenas letras.')
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance and self.instance.pk:
            if email != self.instance.email and User.objects.filter(email=email).exists():
                raise ValidationError('Este e-mail já está em uso por outra conta.')
        return email


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Digite seu e-mail cadastrado'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email, is_active=True).exists():
            raise ValidationError('Nenhuma conta ativa encontrada com este e-mail.')
        return email


class PasswordResetConfirmForm(forms.Form):
    password = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Digite sua nova senha'
        })
    )
    password2 = forms.CharField(
        label='Confirme a Senha',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Digite a senha novamente'
        })
    )
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        
        if password and password2 and password != password2:
            raise ValidationError('As senhas não conferem.')
        
        return cleaned_data