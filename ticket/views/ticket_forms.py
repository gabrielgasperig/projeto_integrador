from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator

from ticket.models import Ticket
from ticket.forms import TicketForm

def create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)

        context = {
            'form': form
        }

        if form.is_valid():
            form.save()
            return redirect('ticket:create')

        return render(
            request,
            'ticket/create.html',
            context
        )

    context = {
        'form': TicketForm(),
    }

    return render(
        request,
        'ticket/create.html',
        context
    )