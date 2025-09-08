from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.forms import AuthenticationForm
from ticket.forms import RegisterForm, RegisterUpdateForm
from django.contrib.auth.decorators import login_required


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

@login_required(login_url='ticket:login')
def user_update(request):
    form = RegisterUpdateForm(instance=request.user)

    if request.method != 'POST':
        return render(
            request, 
            'ticket/register.html',
            {
                'form': form,
            }
        )
    
    form = RegisterUpdateForm(request.POST, instance=request.user)

    if not form.is_valid():
        return render(
            request, 
            'ticket/register.html',
            {
                'form': form,
            }
        )
    
    form.save()
    messages.success(request, 'Dados atualizados com sucesso!')
    return redirect('ticket:user_update')

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

@login_required(login_url='ticket:login')
def logout_view(request):
    auth.logout(request)
    return redirect('ticket:login')