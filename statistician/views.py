from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ticket.models import Ticket
from django.db.models import Count, Avg, F
from django.utils import timezone

@login_required
def index(request):
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.filter(status='Aberto').count()
    in_progress_tickets = Ticket.objects.filter(status='Em Andamento').count()
    closed_tickets = Ticket.objects.filter(status='Fechado').count()
    
    tickets_by_status = Ticket.objects.values('status').annotate(count=Count('status'))
    tickets_by_priority = Ticket.objects.values('priority').annotate(count=Count('priority'))

    # Tempo Médio de Resolução
    avg_resolution_time = Ticket.objects.filter(status='Fechado', closed_date__isnull=False).aggregate(
        avg_time=Avg(F('closed_date') - F('created_date'))
    )['avg_time']

    # Conformidade com o SLA
    sla_compliance = Ticket.objects.filter(status='Fechado', closed_date__isnull=False, sla_deadline__isnull=False)
    sla_met = sla_compliance.filter(closed_date__lte=F('sla_deadline')).count()
    sla_total = sla_compliance.count()
    sla_compliance_percentage = (sla_met / sla_total * 100) if sla_total > 0 else 0

    # Média de Avaliação
    average_rating = Ticket.objects.filter(rating__isnull=False).aggregate(avg_rating=Avg('rating'))['avg_rating']

    # Tickets por Agente
    tickets_per_agent = Ticket.objects.filter(assigned_to__isnull=False).values('assigned_to__username').annotate(count=Count('id'))

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
        'tickets_per_agent': tickets_per_agent,
        'site_title':'Estatísticas de Tickets',
    }
    return render(request, 'statistician/index.html', context)