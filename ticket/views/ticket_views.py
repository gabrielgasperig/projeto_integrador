from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

# Importações locais
from ..models import Ticket, TicketEvent, TicketImage
from ..forms import (
    TicketForm, ConcludeTicketForm, DeleteTicketForm, RatingForm, TransferTicketForm
)

@login_required(login_url='account:login')
def my_tickets(request):
    """
    Página para o user padrão ver e gerir os seus próprios tickets.
    """
    if request.user.is_staff:
        # Se um admin aceder a esta página por engano, redireciona para o início dele
        return redirect('ticket:index')

    # Table 1: Tickets abertos ou em andamento criados pelo user
    open_tickets = Ticket.objects.filter(
        owner=request.user
    ).exclude(
        status='Fechado'
    ).order_by('-created_date')
    
    # Table 2: Tickets fechados criados pelo user
    closed_tickets = Ticket.objects.filter(
        owner=request.user, 
        status='Fechado'
    ).order_by('-closed_date')

    context = {
        'site_title': 'Meus Tickets',
        'open_tickets': open_tickets,
        'closed_tickets': closed_tickets,
    }
    return render(request, 'ticket/my_tickets.html', context)




@login_required(login_url='account:login')
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    is_owner = ticket.owner == request.user
    is_admin = request.user.is_staff
    if not (is_owner or is_admin):
        messages.error(request, 'Não tem permissão para ver este ticket.')
        return redirect('ticket:index')

    rating_form = RatingForm(instance=ticket)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_comment':
            comment_text = request.POST.get('comment_text', '').strip()
            if comment_text:
                TicketEvent.objects.create(
                    ticket=ticket, user=request.user, event_type='COMENTÁRIO', 
                    description=comment_text
                )
                messages.success(request, 'Comentário adicionado.')
        
        elif action == 'submit_rating' and is_owner and ticket.status == 'Fechado':
            rating_form = RatingForm(request.POST, instance=ticket)
            if rating_form.is_valid():
                rated_ticket = rating_form.save()
                
                TicketEvent.objects.create(
                    ticket=ticket, user=request.user, event_type='AVALIAÇÃO',
                    description=f"Utilizador avaliou o atendimento com: {rated_ticket.get_rating_display()}."
                )
                messages.success(request, 'Obrigado pelo seu feedback!')
            else:
                messages.error(request, 'Por favor, selecione uma avaliação válida.')

        return redirect('ticket:ticket_detail', ticket_id=ticket.id)

    context = {
        'ticket': ticket,
        'conclude_form': ConcludeTicketForm(),
        'delete_form': DeleteTicketForm(),
        'rating_form': rating_form,
        'transfer_form': TransferTicketForm(current_admin=ticket.assigned_to),
        'site_title': 'Ticket',
    }
    return render(request, 'ticket/ticket.html', context)

@login_required(login_url='account:login')
def create(request):
    form = TicketForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False)
        ticket.owner = request.user

        sla_times = {
            'Baixa': timedelta(hours=72),
            'Média': timedelta(hours=48),    
            'Alta': timedelta(hours=24),     
            'Urgente': timedelta(hours=8),     
        }
       
        sla_duration = sla_times.get(ticket.priority, timedelta(hours=48)) 
        ticket.sla_deadline = timezone.now() + sla_duration
        ticket.save()

        images = request.FILES.getlist('images')
        for img in images:
            TicketImage.objects.create(ticket=ticket, image=img)

        TicketEvent.objects.create(
            ticket=ticket, user=request.user, event_type='CRIAÇÃO',
            description=f'Ticket criado com {len(images)} anexo(s).'
        )
        
        messages.success(request, 'Ticket criado com sucesso!')
        return redirect('ticket:ticket_detail', ticket_id=ticket.pk)
    else:
        if request.method == 'POST':
            print("ERROS DE VALIDAÇÃO DO FORMULÁRIO:", form.errors)

    context = {
        'form': form,
        'site_title': 'Novo Ticket'
    }
    return render(request, 'ticket/create.html', context)


@login_required(login_url='account:login')
def update(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id, owner=request.user)
    form = TicketForm(request.POST or None, request.FILES or None, instance=ticket)

    if request.method == 'POST' and form.is_valid():
        
        if form.changed_data:
            changes_list = []
            for field_name in form.changed_data:
                field_label = form.fields[field_name].label or field_name.capitalize()
                changes_list.append(f"O campo '{field_label}' foi alterado.")
            
            description_of_changes = "\n".join(changes_list)

            TicketEvent.objects.create(
                ticket=ticket,
                user=request.user,
                event_type='EDIÇÃO',
                description=description_of_changes
            )
        
        form.save()

        images = request.FILES.getlist('images')
        if images:
            for img in images:
                TicketImage.objects.create(ticket=ticket, image=img)
            num_images = len(images)
            if num_images == 1:
                message_text = "1 nova imagem foi adicionada."
            else:
                message_text = f"{num_images} novas imagens foram adicionadas."
            
            messages.info(request, message_text)
        
        if form.changed_data or images:
            messages.success(request, 'Ticket atualizado com sucesso!')
        else:
            messages.info(request, 'Nenhuma alteração foi feita.')

        return redirect('ticket:ticket_detail', ticket_id=ticket.pk)
    
    context = {
        'form': form,
        'ticket': ticket,
        'site_title': 'Edição de Chamado',
    }
    
    return render(request, 'ticket/create.html', context)

@login_required(login_url='account:login')
def delete(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if not (ticket.owner == request.user or request.user.is_staff):
        messages.error(request, 'Não tem permissão para excluir este ticket.')
        return redirect('ticket:index')

    if request.method == 'POST':
        form = DeleteTicketForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            TicketEvent.objects.create(
                ticket=ticket, user=request.user, event_type='EXCLUSÃO', 
                description=f"Motivo: {reason}"
            )
            ticket.delete()
            messages.success(request, 'Ticket excluído com sucesso.')
            return redirect('ticket:index')
        else:
            messages.error(request, 'O motivo da exclusão é obrigatório.')
            return redirect('ticket:ticket_detail', ticket_id=ticket.id)


@login_required(login_url='account:login')
def conclude_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if not request.user.is_staff:
        messages.error(request, 'Não tem permissão para executar esta ação.')
        return redirect('ticket:ticket_detail', ticket_id=ticket.id)

    if request.method == 'POST':
        form = ConcludeTicketForm(request.POST)
        if form.is_valid():
            solution = form.cleaned_data['solution']
            ticket.status = 'Fechado'
            ticket.closed_date = timezone.now() 
            ticket.save()
            TicketEvent.objects.create(
                ticket=ticket, user=request.user, event_type='CONCLUSÃO', 
                description=f"Solução: {solution}"
            )
            messages.success(request, 'Ticket concluído com sucesso.')
        else:
            messages.error(request, 'A solução é obrigatória para concluir o ticket.')
    
    return redirect('ticket:ticket_detail', ticket_id=ticket.id)

@login_required(login_url='account:login')
def assign_ticket(request, ticket_id):
    if not request.user.is_staff:
        messages.error(request, 'Ação não permitida.')
        return redirect('ticket:index')
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    ticket.assigned_to = request.user
    ticket.status = 'Em Andamento'
    ticket.save()
    TicketEvent.objects.create(ticket=ticket, user=request.user, event_type='STATUS', description=f"Ticket atribuído a {request.user.get_full_name()}. Status alterado para 'Em Andamento'.")
    messages.success(request, 'Você capturou o ticket.')
    return redirect('ticket:ticket_detail', ticket_id=ticket.id)

@login_required(login_url='account:login')
def transfer_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    
    is_assigned_admin = request.user == ticket.assigned_to
    if not (request.user.is_superuser or is_assigned_admin):
        messages.error(request, 'Não tem permissão para transferir este ticket.')
        return redirect('ticket:ticket_detail', ticket_id=ticket.id)

    if request.method == 'POST':
        form = TransferTicketForm(request.POST, current_admin=ticket.assigned_to)
        if form.is_valid():
            old_admin_name = ticket.assigned_to.get_full_name() if ticket.assigned_to else "Ninguém"
            new_admin = form.cleaned_data['new_admin']
            
            ticket.assigned_to = new_admin
            ticket.save()

            TicketEvent.objects.create(
                ticket=ticket, user=request.user, event_type='TRANSFERÊNCIA',
                description=f"Ticket transferido de {old_admin_name} para {new_admin.get_full_name()}."
            )
            messages.success(request, f'Ticket transferido para {new_admin.get_full_name()}.')
    
    return redirect('ticket:ticket_detail', ticket_id=ticket.id)