from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator

from ticket.models import Ticket
from ticket.forms import TicketForm

def create(request):
    if request.method == 'POST':
        context = {
            'form': TicketForm(request.POST),
        }

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