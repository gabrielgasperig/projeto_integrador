from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import timedelta, datetime

# Importações locais
from ..models import Ticket

def is_admin(user):
    return user.is_staff

@login_required
def index(request):
    if not request.user.is_staff:
        return redirect('ticket:my_tickets')

    sort_by_unassigned = request.GET.get('sort_unassigned', '-created_date')
    unassigned_tickets = Ticket.objects.filter(
        status__in=['Aberto', 'Em Andamento'],
        assigned_to=None
    ).order_by(sort_by_unassigned)

    sort_by_assigned = request.GET.get('sort_assigned', 'sla_deadline')
    assigned_to_me = Ticket.objects.filter(
        assigned_to=request.user
    ).exclude(
        status='Fechado'
    ).order_by(sort_by_assigned)

    context = {
        'site_title': 'Fila de Atendimento',
        'unassigned_tickets': unassigned_tickets,
        'assigned_to_me': assigned_to_me,
        'current_sort_unassigned': sort_by_unassigned,
        'current_sort_assigned': sort_by_assigned,
    }
    return render(request, 'ticket/index.html', context)

@login_required
@user_passes_test(is_admin, login_url='ticket:index')
def all_tickets(request):
    tickets_list = Ticket.objects.all()

    search_value = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    subcategory_filter = request.GET.get('subcategory', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    sort_by = request.GET.get('sort', '-id')

    if search_value:
        tickets_list = tickets_list.filter(
            Q(title__icontains=search_value) |
            Q(description__icontains=search_value) |
            Q(owner__first_name__icontains=search_value) |
            Q(owner__last_name__icontains=search_value)
        ).distinct()
    if status_filter:
        tickets_list = tickets_list.filter(status__iexact=status_filter)
    if priority_filter:
        tickets_list = tickets_list.filter(priority__iexact=priority_filter)
    if category_filter:
        tickets_list = tickets_list.filter(category_id=category_filter)
    if subcategory_filter:
        tickets_list = tickets_list.filter(subcategory_id=subcategory_filter)

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%d-%m-%Y').date()
            tickets_list = tickets_list.filter(created_date__gte=start_date)
        except ValueError:
            pass
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%d-%m-%Y').date()
            end_date_inclusive = end_date + timedelta(days=1)
            tickets_list = tickets_list.filter(created_date__lt=end_date_inclusive)
        except ValueError:
            pass

    tickets_list = tickets_list.order_by(sort_by)
    
    paginator = Paginator(tickets_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    from ..models import Category, Subcategory
    categories = Category.objects.all().order_by('name')
    subcategories = Subcategory.objects.all().order_by('category__name', 'name')

    context = {
        'site_title': 'Todos os Tickets',
        'page_obj': page_obj,
        'status_choices': Ticket.STATUS_CHOICES,
        'priorities': Ticket.PRIORITY_CHOICES,
        'categories': categories,
        'subcategories': subcategories,
        'search_value': search_value,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'current_sort': sort_by,
    }
    return render(request, 'ticket/all_tickets.html', context)