from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from ticket.forms import TicketForm
from ticket.models import Ticket

def create(request):
    form_action = reverse('ticket:create')

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)

        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            ticket = form.save()
            return redirect('ticket:update', ticket_id=ticket.pk)

        return render(
            request,
            'ticket/create.html',
            context
        )

    context = {
        'form': TicketForm(),
        'form_action': form_action,
    }

    return render(
        request,
        'ticket/create.html',
        context
    )

def update(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id, show=True)
    form_action = reverse('ticket:update', args=(ticket_id,))

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)

        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            form.save()
            return redirect('ticket:update', ticket_id=ticket.pk)

        return render(
            request,
            'ticket/create.html',
            context
        )

    context = {
        'form': TicketForm(instance=ticket),
        'form_action': form_action,
    }

    return render(
        request,
        'ticket/create.html',
        context
    )

def delete(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id, show=True)

    confirmation = request.POST.get('confirmation', 'no')
    print('confirmation', confirmation)

    if confirmation == 'yes':
        ticket.delete()
        return redirect('ticket:index')
    
    return render(request, 'ticket/ticket.html', {'ticket': ticket, 'confirmation': confirmation})