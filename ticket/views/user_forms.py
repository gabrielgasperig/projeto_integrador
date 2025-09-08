from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.forms import AuthenticationForm


from ticket.forms import RegisterForm

def register(request):
    form = RegisterForm()
    messages.info(request, 'Conta criada com sucesso!')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('ticket:login')
        
    return render(
        request, 
        'ticket/register.html',
        {
            'form': form,
        }
    )

def login_view(request):
    form = AuthenticationForm(request)

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            messages.success(request, f'Bem vindo(a) {user.username}!')
            return redirect('ticket:index')
        messages.error(request, 'Usuário ou senha inválidos.')
        
    return render(
        request, 
        'ticket/login.html',
        {
            'form': form,
        }
    )

def logout_view(request):
    auth.logout(request)
    return redirect('ticket:login')