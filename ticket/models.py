from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import time, timedelta


def add_working_hours(start, hours):
    current = start
    hours_left = hours
    work_periods = [(time(8, 0), time(12, 0)), (time(14, 0), time(18, 0))]
    
    while hours_left > 0:
        if current.weekday() < 5: # Segunda a Sexta
            for period_start, period_end in work_periods:
                period_start_dt = current.replace(
                    hour=period_start.hour, 
                    minute=period_start.minute, 
                    second=0, 
                    microsecond=0
                )
                period_end_dt = current.replace(
                    hour=period_end.hour, 
                    minute=period_end.minute, 
                    second=0, 
                    microsecond=0
                )
                
                if current < period_start_dt:
                    current = period_start_dt
                    
                if period_start_dt <= current < period_end_dt:
                    available = (period_end_dt - current).total_seconds() / 3600
                    if hours_left <= available:
                        return current + timedelta(hours=hours_left)
                    else:
                        hours_left -= available
                        current = period_end_dt
                        
        current = (current + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    
    return current


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='subcategories',
        verbose_name="Categoria"
    )
    name = models.CharField(max_length=100, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")

    class Meta:
        verbose_name = 'Subcategoria'
        verbose_name_plural = 'Subcategorias'
        unique_together = ('category', 'name')
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Location(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = 'Local'
        verbose_name_plural = 'Locais'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ticket(models.Model):
    
    STATUS_CHOICES = [
        ('Aberto', 'Aberto'),
        ('Em Andamento', 'Em Andamento'),
        ('Fechado', 'Fechado'),
    ]

    PRIORITY_CHOICES = [
        ('A definir', 'A definir'),
        ('Baixa', 'Baixa'),
        ('Média', 'Média'),
        ('Alta', 'Alta'),
        ('Urgente', 'Urgente'),
    ]

    RATING_CHOICES = [
        (1, '1 estrela'),
        (2, '2 estrelas'),
        (3, '3 estrelas'),
        (4, '4 estrelas'),
        (5, '5 estrelas'),
    ]

    title = models.CharField(max_length=100, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        null=True,
        blank=True,
        related_name='tickets', 
        verbose_name='Categoria'
    )
    subcategory = models.ForeignKey(
        Subcategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='tickets', 
        verbose_name='Subcategoria'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name='Local'
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Aberto',
        verbose_name="Status"
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='A definir', 
        verbose_name="Prioridade"
    )
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='owned_tickets',
        verbose_name="Criador"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tickets',
        verbose_name="Responsável"
    )
    
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    sla_deadline = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Prazo de Resolução (SLA)"
    )
    closed_date = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Data de Fechamento"
    )
    
    rating = models.IntegerField(
        choices=RATING_CHOICES, 
        null=True, 
        blank=True, 
        verbose_name="Avaliação"
    )
    feedback = models.TextField(blank=True, null=True, verbose_name="Feedback do Utilizador")
    
    show = models.BooleanField(default=True, verbose_name="Visível")

    class Meta:
        ordering = ['-created_date']
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

    def __str__(self):
        return self.title

    @staticmethod
    def calculate_sla_deadline(start, priority):
        sla_times = {
            'A definir': None,
            'Baixa': 72,
            'Média': 48,
            'Alta': 24,
            'Urgente': 8,
        }
        hours = sla_times.get(priority, 48)
        if hours is None:
            return None
        return add_working_hours(start, hours)

    def get_working_time_delta(self, start, end):
        if start >= end:
            return timedelta(0)
        
        total = timedelta(0)
        current = start
        work_periods = [(time(8, 0), time(12, 0)), (time(14, 0), time(18, 0))]
        
        while current < end:
            if current.weekday() < 5: # Segunda a Sexta
                for period_start, period_end in work_periods:
                    period_start_dt = current.replace(
                        hour=period_start.hour, 
                        minute=period_start.minute, 
                        second=0, 
                        microsecond=0
                    )
                    period_end_dt = current.replace(
                        hour=period_end.hour, 
                        minute=period_end.minute, 
                        second=0, 
                        microsecond=0
                    )
                    
                    if period_end_dt <= period_start_dt:
                        period_end_dt += timedelta(days=1)
                    
                    period_real_start = max(current, period_start_dt)
                    period_real_end = min(end, period_end_dt)
                    
                    if period_real_start < period_real_end:
                        total += period_real_end - period_real_start
            
            next_day = (current + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            current = next_day
        
        return total

    @property
    def time_to_sla(self):
        if not self.sla_deadline or self.status == 'Fechado':
            return None
        now = timezone.localtime(timezone.now())
        deadline = timezone.localtime(self.sla_deadline)
        return self.get_working_time_delta(now, deadline)

    @property
    def sla_status(self):
        if self.status == 'Fechado':
            if self.closed_date and self.sla_deadline:
                return 'Cumprido' if self.closed_date <= self.sla_deadline else 'Violado'
            return 'Concluído'

        time_left = self.time_to_sla
        if not time_left:
            return 'Não Aplicável'

        if time_left.total_seconds() < 0:
            return 'Violado'
        elif time_left.days < 1:
            return 'Atenção'
        else:
            return 'No Prazo'


class TicketImage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='ticket_pictures/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Imagem do Ticket'
        verbose_name_plural = 'Imagens dos Tickets'

    def __str__(self):
        return f"Imagem para o ticket #{self.ticket.id}"


class TicketEvent(models.Model):
    
    EVENT_CHOICES = [
        ('CRIAÇÃO', 'Criação'),
        ('COMENTÁRIO', 'Comentário'),
        ('EDIÇÃO', 'Edição'),
        ('STATUS', 'Mudança de Status'),
        ('TRANSFERÊNCIA', 'Transferência'),
        ('CONCLUSÃO', 'Conclusão'),
        ('EXCLUSÃO', 'Exclusão'),
        ('AVALIAÇÃO', 'Avaliação'),
    ]
    
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='events')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES, verbose_name="Tipo")
    description = models.TextField(
        verbose_name="Descrição",
        help_text="Descreve o evento. Pode ser um comentário, a solução, o motivo da exclusão, etc."
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Data")

    class Meta:
        ordering = ['created_date']
        verbose_name = 'Evento do Ticket'
        verbose_name_plural = 'Eventos dos Tickets'

    def __str__(self):
        return f'{self.event_type} por {self.user.username if self.user else "Sistema"} em {self.ticket.title}'


class TicketEventImage(models.Model):
    event = models.ForeignKey(TicketEvent, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='ticket_pictures/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Imagem do Evento'
        verbose_name_plural = 'Imagens dos Eventos'

    def __str__(self):
        return f"Imagem para o evento #{self.event.id} do ticket #{self.event.ticket.id}"