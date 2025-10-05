from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import timedelta, datetime

# Importações locais
from ..models import Ticket

def is_admin(user):
    return user.is_staff

@login_required(login_url='account:login')
def index(request):
    """
    Página principal da aplicação.
    - Para Admins: Mostra a "Fila de Atendimento".
    - Para Users Padrão: Redireciona para "Meus Tickets".
    """
    if not request.user.is_staff:
        # Se não for admin, o "início" é a página "Meus Tickets"
        return redirect('ticket:my_tickets')
    
    # Table 1: Tickets na fila, abertos e sem ninguém responsável
    unassigned_tickets = Ticket.objects.filter(
        status__in=['Aberto', 'Em Andamento'], 
        assigned_to=None
    ).order_by('-created_date') # Do mais novo para o mais antigo

    # Table 2: Tickets que estão sob a responsabilidade do admin logado
    assigned_to_me = Ticket.objects.filter(
        assigned_to=request.user
    ).exclude(
        status='Fechado'
    ).order_by('sla_deadline') # Os com SLA mais próximo primeiro

    context = {
        'site_title': 'Fila de Atendimento',
        'unassigned_tickets': unassigned_tickets,
        'assigned_to_me': assigned_to_me,
    }
    return render(request, 'ticket/index.html', context)

@login_required(login_url='account:login')
@user_passes_test(is_admin, login_url='ticket:index')
def all_tickets(request):
    """
    Página para o admin ver todos os tickets do sistema, com filtros e paginação.
    """
    tickets_list = Ticket.objects.all()

    # Captura os parâmetros de filtro da URL
    search_value = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    # Aplica os filtros de texto e select
    if search_value:
        tickets_list = tickets_list.filter(Q(title__icontains=search_value) | Q(description__icontains=search_value))
    if status_filter:
        tickets_list = tickets_list.filter(status__iexact=status_filter)
    if priority_filter:
        tickets_list = tickets_list.filter(priority__iexact=priority_filter)

    if start_date_str:
        try:
            # Filtra a partir do início do dia selecionado
            start_date = datetime.strptime(start_date_str, '%d-%m-%Y').date()
            tickets_list = tickets_list.filter(created_date__gte=start_date)
        except ValueError:
            pass # Ignora data inválida
    
    if end_date_str:
        try:
            # Filtra até ao final do dia selecionado
            end_date = datetime.strptime(end_date_str, '%d-%m-%Y').date()
            end_date_inclusive = end_date + timedelta(days=1)
            tickets_list = tickets_list.filter(created_date__lt=end_date_inclusive)
        except ValueError:
            pass # Ignora data inválida


    tickets_list = tickets_list.order_by('-id')
    
    paginator = Paginator(tickets_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'site_title': 'Todos os Tickets',
        'page_obj': page_obj,
        'status_choices': Ticket.STATUS_CHOICES,
        'priorities': Ticket.PRIORITY_CHOICES,
        'search_value': search_value,
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    return render(request, 'ticket/all_tickets.html', context)