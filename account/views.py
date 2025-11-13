from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Importações locais
from .forms import RegisterForm, RegisterUpdateForm

def register_view(request):
    # Se o usuário está autenticado, desloga antes de mostrar a tela de cadastro
    if request.user.is_authenticated:
        auth.logout(request)
        messages.info(request, 'Você foi desconectado para criar uma nova conta.')
    
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Conta criada com sucesso! Por favor, faça o login.')
        return redirect('account:login')
    context = {
        'form': form,
        'site_title': 'Cadastro',
    }
    return render(request, 'account/register.html', context)

@login_required(login_url='account:login')
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
    # Se o usuário já está autenticado, redireciona para o sistema
    if request.user.is_authenticated:
        messages.info(request, 'Você já está logado!')
        return redirect('ticket:index')
    
    form = AuthenticationForm(request, data=request.POST or None)
    
    if request.method == 'POST' and not form.is_valid():
        messages.error(request, 'Usuário ou senha inválidos. Por favor, tente novamente.')

    if form.is_valid():
        user = form.get_user()
        auth.login(request, user)
        messages.success(request, f'Bem-vindo(a), {user.first_name}!')
        return redirect('ticket:index')
        
    context = {
        'form': form,
        'site_title': 'Login',
    }
    return render(request, 'account/login.html', context)

@login_required(login_url='coaccountnta:login')
def logout_view(request):
    auth.logout(request)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('account:login')