from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from .forms import RegisterForm, RegisterUpdateForm
from .models import EmailConfirmation

def register_view(request):
    if request.user.is_authenticated:
        auth.logout(request)
        messages.info(request, 'Você foi desconectado para criar uma nova conta.')
    
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        try:
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            confirmation = EmailConfirmation.objects.create(user=user)
            
            confirmation_url = request.build_absolute_uri(
                f'/account/confirm-email/{confirmation.token}/'
            )
            
            html_message = render_to_string('account/email/confirmation_email.html', {
                'user': user,
                'confirmation_url': confirmation_url,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject='Confirme seu cadastro no Gesticket',
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(request, 'Cadastro realizado! Verifique seu e-mail para confirmar sua conta.')
            return redirect('account:login')
        except Exception as e:
            if 'user' in locals():
                user.delete()
            messages.error(request, f'Erro ao enviar e-mail de confirmação. Por favor, verifique seu e-mail e tente novamente. Erro: {str(e)}')
    context = {
        'form': form,
        'site_title': 'Cadastro',
    }
    return render(request, 'account/register.html', context)

@login_required
def user_update(request):
    form = RegisterUpdateForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Dados atualizados com sucesso!')
        return redirect('account:user_update')
    context = {
        'form': form,
        'site_title': 'Meu Perfil'
    }
    return render(request, 'account/user_update.html', context)

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'Você já está logado!')
        return redirect('ticket:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username:
            User = auth.get_user_model()
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    if not user.is_active:
                        messages.error(request, 'Sua conta ainda não foi confirmada. Verifique seu e-mail para ativar sua conta.')
                        context = {
                            'form': AuthenticationForm(request),
                            'site_title': 'Login',
                            'show_resend': True,
                            'user_id': user.id,
                        }
                        return render(request, 'account/login.html', context)
            except User.DoesNotExist:
                pass
        
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            messages.success(request, f'Bem-vindo(a), {user.first_name}!')
            return redirect('ticket:index')
        else:
            messages.error(request, 'Usuário ou senha inválidos. Por favor, tente novamente.')
    else:
        form = AuthenticationForm(request)
        
    context = {
        'form': form,
        'site_title': 'Login',
    }
    return render(request, 'account/login.html', context)

@login_required
def logout_view(request):
    auth.logout(request)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('account:login')

def confirm_email_view(request, token):
    """View para confirmar o e-mail do usuário através do token"""
    confirmation = get_object_or_404(EmailConfirmation, token=token)
    
    if confirmation.confirmed_at:
        messages.info(request, 'Este e-mail já foi confirmado anteriormente.')
        return redirect('account:login')
    
    if not confirmation.is_valid():
        messages.error(request, 'Este link de confirmação expirou. Solicite um novo e-mail de confirmação.')
        return render(request, 'account/confirmation_expired.html', {
            'user': confirmation.user,
            'site_title': 'Link Expirado'
        })
    
    confirmation.confirm()
    messages.success(request, 'E-mail confirmado com sucesso! Você já pode fazer login.')
    return redirect('account:login')

from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def resend_confirmation_email(request, user_id):
    """View para reenviar e-mail de confirmação"""
    user = get_object_or_404(auth.get_user_model(), id=user_id)

    if user.is_active:
        messages.info(request, 'Esta conta já está ativa.')
        return redirect('account:login')

    if request.method == "POST":
        try:
            confirmation, created = EmailConfirmation.objects.get_or_create(user=user)

            if not created and confirmation.confirmed_at:
                messages.info(request, 'Esta conta já foi confirmada.')
                return redirect('account:login')

            if not confirmation.is_valid():
                confirmation.delete()
                confirmation = EmailConfirmation.objects.create(user=user)

            confirmation_url = request.build_absolute_uri(
                f'/account/confirm-email/{confirmation.token}/'
            )

            html_message = render_to_string('account/email/confirmation_email.html', {
                'user': user,
                'confirmation_url': confirmation_url,
            })
            plain_message = strip_tags(html_message)

            send_mail(
                subject='Confirme seu cadastro no Gesticket',
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            messages.success(request, 'E-mail de confirmação reenviado! Verifique sua caixa de entrada.')
        except Exception as e:
            messages.error(request, f'Erro ao enviar e-mail. Por favor, tente novamente mais tarde. Erro: {str(e)}')
        return redirect('account:login')

    return redirect('account:login')