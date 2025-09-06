from django.shortcuts import render, redirect
from django.contrib import messages


from ticket.forms import RegisterForm

def register(request):
    form = RegisterForm()
    messages.info(request, 'Conta criada com sucesso!')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.info(request, 'Conta criada com sucesso!')
            return redirect('ticket:index')
        
    return render(
        request, 
        'ticket/register.html',
        {
            'form': form,
        }
    )