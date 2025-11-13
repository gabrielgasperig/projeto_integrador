from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ticket.models import Ticket
from django.db.models import Count, Avg, F, Q, ExpressionWrapper, DurationField
from django.utils import timezone
from django.contrib.auth.models import User

@login_required
def index(request):
    # Obter parâmetros de filtro
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    assigned_to = request.GET.get('assigned_to')
    priority = request.GET.get('priority')

    # Construir filtros base
    filters = Q()
    if start_date:
        filters &= Q(created_date__gte=start_date)
    if end_date:
        filters &= Q(created_date__lte=end_date + ' 23:59:59')
    if assigned_to:
        filters &= Q(assigned_to_id=assigned_to)
    if priority:
        filters &= Q(priority=priority)

    # Aplicar filtros em todas as consultas
    tickets = Ticket.objects.filter(filters)
    total_tickets = tickets.count()
    open_tickets = tickets.filter(status='Aberto').count()
    in_progress_tickets = tickets.filter(status='Em Andamento').count()
    closed_tickets = tickets.filter(status='Fechado').count()
    
    tickets_by_status = tickets.values('status').annotate(count=Count('status'))
    tickets_by_priority = tickets.values('priority').annotate(count=Count('priority'))

    # Tempo Médio de Resolução
    avg_resolution = tickets.filter(status='Fechado', closed_date__isnull=False).annotate(
        resolution_time=ExpressionWrapper(F('closed_date') - F('created_date'), output_field=DurationField())
    ).aggregate(avg_time=Avg('resolution_time'))['avg_time']

    # Converte para horas (float) se existir
    if avg_resolution:
        avg_resolution_time = avg_resolution.total_seconds() / 3600
    else:
        avg_resolution_time = None

    # Conformidade com o SLA
    sla_compliance = tickets.filter(status='Fechado', closed_date__isnull=False, sla_deadline__isnull=False)
    sla_met = sla_compliance.filter(closed_date__lte=F('sla_deadline')).count()
    sla_total = sla_compliance.count()
    sla_compliance_percentage = (sla_met / sla_total * 100) if sla_total > 0 else 0

    # Média de Avaliação
    average_rating = tickets.filter(rating__isnull=False).aggregate(avg_rating=Avg('rating'))['avg_rating']

    # Tickets em Atraso (SLA)
    now = timezone.now()
    overdue_tickets = tickets.filter(
        status__in=['Aberto', 'Em Andamento'],
        sla_deadline__isnull=False,
        sla_deadline__lt=now
    ).count()

    # Tickets por Agente
    tickets_per_agent = tickets.filter(assigned_to__isnull=False).values(
        'assigned_to__first_name', 'assigned_to__last_name'
    ).annotate(count=Count('id'))

    # Dados para os filtros (apenas admins)
    agents = User.objects.filter(is_active=True, is_staff=True).order_by('first_name', 'last_name')
    priorities = Ticket._meta.get_field('priority').choices

    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'closed_tickets': closed_tickets,
        'tickets_by_status': tickets_by_status,
        'tickets_by_priority': tickets_by_priority,
        'avg_resolution_time': avg_resolution_time,
        'sla_compliance_percentage': sla_compliance_percentage,
        'average_rating': average_rating,
        'overdue_tickets': overdue_tickets,
        'tickets_per_agent': tickets_per_agent,
        'site_title': 'Dashboard de Estatísticas',
        # Dados para os filtros
        'agents': agents,
        'priorities': priorities,
    }
    return render(request, 'statistician/index.html', context)