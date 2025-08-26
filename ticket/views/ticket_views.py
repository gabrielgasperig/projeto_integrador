from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from ticket.models import Ticket

# Create your views here.
def index(request):
    tickets = Ticket.objects.filter(show=True).order_by('-id')

    context = {
        'tickets': tickets,
        'site_title': 'All Tickets',
    }

    return render(
        request,
        'ticket/index.html',
        context
    )

def search(request):
    search_value = request.GET.get('q', '')

    if search_value == '':
        return redirect('ticket:index')

    tickets = Ticket.objects.filter(
        show=True
    ).filter(
        Q(title__icontains=search_value) | Q(description__icontains=search_value)
    ).order_by('-id')

    context = {
        'tickets': tickets,
        'site_title': f'Search for "{search_value}"',
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