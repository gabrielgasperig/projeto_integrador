from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from ticket.models import Ticket
from django.core.paginator import Paginator

# Create your views here.
def index(request):
    tickets = Ticket.objects.filter(show=True).order_by('-id')

    paginator = Paginator(tickets, 10)  # Show 10 tickets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
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
        Q(title__icontains=search_value) | Q(description__icontains=search_value) | Q(user__icontains=search_value)
    ).order_by('-id')

    paginator = Paginator(tickets, 10)  # Show 10 tickets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'site_title': 'Search - ',
        'search_value': search_value,
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