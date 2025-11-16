from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime
import re
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from django.db.models import Q, Prefetch
from django.core.paginator import Paginator

# Importações locais
from ..models import Ticket, TicketEvent, TicketImage
from ..forms import (
    TicketForm, ConcludeTicketForm, DeleteTicketForm, RatingForm, TransferTicketForm, TicketEventForm, AdminSetPriorityForm
)

@login_required
def my_tickets(request):
   
    if request.user.is_staff:
        return redirect('ticket:index')

    sort_by = request.GET.get('sort', '-created_date')
    open_tickets = Ticket.objects.filter(
        owner=request.user
    ).exclude(
        status='Fechado'
    ).order_by(sort_by)

    closed_sort_by = request.GET.get('sort_closed', '-closed_date')
    closed_tickets = Ticket.objects.filter(
        owner=request.user,
        status='Fechado'
    ).order_by(closed_sort_by)

    context = {
        'site_title': 'Meus Tickets',
        'open_tickets': open_tickets,
        'closed_tickets': closed_tickets,
        'current_sort': sort_by,
        'current_sort_closed': closed_sort_by,
    }
    return render(request, 'ticket/my_tickets.html', context)




@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    is_owner = ticket.owner == request.user
    is_admin = request.user.is_staff
    if not (is_owner or is_admin):
        messages.error(request, 'Não tem permissão para ver este ticket.')
        return redirect('ticket:index')


    rating_form = RatingForm(instance=ticket)
    comment_form = TicketEventForm()


    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_comment':
            comment_form = TicketEventForm(request.POST, request.FILES)
            if comment_form.is_valid():
                comment_text = comment_form.cleaned_data['comment_text']
                event = TicketEvent.objects.create(
                    ticket=ticket, user=request.user, event_type='COMENTÁRIO',
                    description=comment_text
                )
                images = request.FILES.getlist('images')
                for img in images:
                    from ..models import TicketEventImage
                    TicketEventImage.objects.create(event=event, image=img)
                if ticket.owner == request.user and ticket.assigned_to:
                    notify_ticket_responsible(
                        ticket,
                        subject=f'Novo comentário no ticket: {ticket.title}',
                        message=(
                            f'Usuário: {request.user.get_full_name()}\n'
                            f'Evento: Comentário\n'
                            f'Mensagem:\n{comment_text}'
                        )
                    )
                elif ticket.assigned_to == request.user:
                    notify_ticket_owner(
                        ticket,
                        subject=f'Novo comentário no ticket: {ticket.title}',
                        message=(
                            f'Usuário: {request.user.get_full_name()}\n'
                            f'Evento: Comentário\n'
                            f'Mensagem:\n{comment_text}'
                        )
                    )
                messages.success(request, 'Comentário adicionado.')
            else:
                messages.error(request, 'Erro ao adicionar comentário. Verifique o formulário.')

        elif action == 'submit_rating' and is_owner and ticket.status == 'Fechado':
            rating_form = RatingForm(request.POST, instance=ticket)
            if rating_form.is_valid():
                rated_ticket = rating_form.save()
                TicketEvent.objects.create(
                    ticket=ticket, user=request.user, event_type='AVALIAÇÃO',
                    description=f"Utilizador avaliou o atendimento com: {rated_ticket.get_rating_display()}."
                )
                if ticket.assigned_to:
                    notify_ticket_responsible(
                        ticket,
                        subject=f'Avaliação recebida no ticket: {ticket.title}',
                        message=(
                            f'Usuário: {request.user.get_full_name()}\n'
                            f'Evento: Avaliação\n'
                            f'Mensagem: {rated_ticket.get_rating_display()}'
                        )
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
        'comment_form': comment_form,
        # Exibe formulário de prioridade apenas enquanto estiver "A definir"
        'priority_form': AdminSetPriorityForm() if (request.user.is_staff and ticket.status != 'Fechado' and ticket.priority == 'A definir') else None,
        'site_title': 'Ticket',
    }
    return render(request, 'ticket/ticket.html', context)

@login_required
def create(request):

    form = TicketForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False)
        ticket.owner = request.user

        from ticket.models import Ticket
        ticket.sla_deadline = Ticket.calculate_sla_deadline(timezone.now(), ticket.priority)
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


@login_required
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

        if 'priority' in form.changed_data:
            new_priority = form.cleaned_data.get('priority') or ticket.priority
            new_deadline = Ticket.calculate_sla_deadline(timezone.now(), new_priority)
            ticket.sla_deadline = new_deadline
            ticket.save(update_fields=['sla_deadline'])

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

@login_required
def delete(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if not (ticket.owner == request.user):
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


@login_required
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
            if ticket.assigned_to == request.user:
                notify_ticket_owner(
                    ticket,
                    subject=f'Seu ticket foi fechado: {ticket.title}',
                    message=(
                        f'Usuário: {request.user.get_full_name()}\n'
                        f'Evento: Fechamento\n'
                        f'Mensagem: {solution}'
                    )
                )
            messages.success(request, 'Ticket concluído com sucesso.')
        else:
            messages.error(request, 'A solução é obrigatória para concluir o ticket.')
    
    return redirect('ticket:ticket_detail', ticket_id=ticket.id)

@login_required
def assign_ticket(request, ticket_id):
    if not request.user.is_staff:
        messages.error(request, 'Ação não permitida.')
        return redirect('ticket:index')
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    
    if request.method == 'POST':
        form = AdminSetPriorityForm(request.POST)
        if form.is_valid():
            priority = form.cleaned_data['priority']
            ticket.assigned_to = request.user
            ticket.status = 'Em Andamento'
            ticket.priority = priority
            ticket.sla_deadline = Ticket.calculate_sla_deadline(timezone.now(), priority)
            ticket.save()
            TicketEvent.objects.create(
                ticket=ticket, 
                user=request.user, 
                event_type='STATUS', 
                description=f"Ticket atribuído a {request.user.get_full_name()}. Status alterado para 'Em Andamento'. Prioridade definida como '{priority}'."
            )
            messages.success(request, 'Ticket em andamento.')
            return redirect('ticket:ticket_detail', ticket_id=ticket.id)
        else:
            messages.error(request, 'É necessário definir a prioridade para atender o ticket.')
    
    return redirect('ticket:ticket_detail', ticket_id=ticket.id)

@login_required
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

@login_required
def set_priority(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if not request.user.is_staff:
        messages.error(request, 'Ação não permitida.')
        return redirect('ticket:ticket_detail', ticket_id=ticket.id)
    
    # Bloqueia alteração se já definida ou ticket fechado
    if ticket.status == 'Fechado' or ticket.priority != 'A definir':
        messages.error(request, 'Prioridade já definida ou ticket fechado; não é possível alterar.')
        return redirect('ticket:ticket_detail', ticket_id=ticket.id)

    if request.method == 'POST':
        form = AdminSetPriorityForm(request.POST)
        if form.is_valid():
            new_priority = form.cleaned_data['priority']
            ticket.priority = new_priority
            ticket.sla_deadline = Ticket.calculate_sla_deadline(timezone.now(), new_priority)
            ticket.save(update_fields=['priority', 'sla_deadline'])
            TicketEvent.objects.create(
                ticket=ticket,
                user=request.user,
                event_type='STATUS',
                description=f"Prioridade alterada para: {new_priority}."
            )
            messages.success(request, 'Prioridade atualizada e SLA recalculado.')
        else:
            messages.error(request, 'Selecione uma prioridade válida.')

    return redirect('ticket:ticket_detail', ticket_id=ticket.id)

@login_required
def solutions(request):
    """
    Página para exibir um banco de soluções de tickets fechados, com filtros.
    Apenas administradores podem acessar esta página.
    """
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado. Você não tem permissão para acessar esta página.')
        return redirect('ticket:my_tickets')
    query = request.GET.get('q', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    sort = request.GET.get('sort', '-closed_date')

    resolved_tickets_list = Ticket.objects.filter(status='Fechado').prefetch_related(
        Prefetch('events', queryset=TicketEvent.objects.filter(event_type='CONCLUSÃO'), to_attr='conclusion_events')
    )

    if query:
        resolved_tickets_list = resolved_tickets_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(assigned_to__first_name__icontains=query) |
            Q(assigned_to__last_name__icontains=query)
        ).distinct()

    if start_date:
        resolved_tickets_list = resolved_tickets_list.filter(closed_date__gte=start_date)

    if end_date:
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        resolved_tickets_list = resolved_tickets_list.filter(closed_date__lt=end_date_dt)

    allowed_sorts = ['title', '-title', 'closed_date', '-closed_date']
    if sort in allowed_sorts:
        resolved_tickets_list = resolved_tickets_list.order_by(sort)
    else:
        resolved_tickets_list = resolved_tickets_list.order_by('-closed_date')

    paginator = Paginator(resolved_tickets_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'site_title': 'Banco de Soluções',
        'page_obj': page_obj,
        'search_value': query,
        'start_date': start_date,
        'end_date': end_date,
        'current_sort': sort,
    }
    return render(request, 'ticket/solutions.html', context)

def notify_ticket_owner(ticket, subject, message):
    if ticket.owner and ticket.owner.email:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [ticket.owner.email],
            fail_silently=True,
        )

def notify_ticket_responsible(ticket, subject, message):
    if ticket.assigned_to and ticket.assigned_to.email:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [ticket.assigned_to.email],
            fail_silently=True,
        )