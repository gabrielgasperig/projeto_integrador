from django.shortcuts import render, get_object_or_404
from ticket.models import Ticket

# Create your views here.
def index(request):
    tickets = Ticket.objects.filter(show=True).order_by('-id')

    context = {
        'tickets': tickets,
    }

    return render(
        request,
        'ticket/index.html',
        context
    )


def ticket(request, ticket_id):
    single_ticket = get_object_or_404(Ticket, pk=ticket_id, show=True)

    context = {
        'ticket': single_ticket,
    }

    return render(
        request,
        'ticket/ticket.html',
        context
    )