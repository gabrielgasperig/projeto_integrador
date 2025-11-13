def add_working_hours(start, hours):
    from datetime import timedelta, time
    current = start
    hours_left = hours
    work_periods = [(time(8, 0), time(12, 0)), (time(14, 0), time(18, 0))]
    while hours_left > 0:
        if current.weekday() < 5:
            for period_start, period_end in work_periods:
                period_start_dt = current.replace(hour=period_start.hour, minute=period_start.minute, second=0, microsecond=0)
                period_end_dt = current.replace(hour=period_end.hour, minute=period_end.minute, second=0, microsecond=0)
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
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import time, timedelta

class Ticket(models.Model):
    @staticmethod
    def calculate_sla_deadline(start, priority):
        """Calcula o deadline de SLA somando horas úteis conforme a prioridade."""
        sla_times = {
            'Baixa': 72,
            'Média': 48,
            'Alta': 24,
            'Urgente': 8,
        }
        horas = sla_times.get(priority, 48)
        return add_working_hours(start, horas)
    
    STATUS_CHOICES = [
        ('Aberto', 'Aberto'),
        ('Em Andamento', 'Em Andamento'),
        ('Fechado', 'Fechado'),
    ]

    PRIORITY_CHOICES = [
        ('Baixa', 'Baixa'),
        ('Média', 'Média'),
        ('Alta', 'Alta'),
        ('Urgente', 'Urgente'),
    ]

    title = models.CharField(max_length=100, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_tickets')
    created_date = models.DateTimeField(auto_now_add=True)
    show = models.BooleanField(default=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Média', verbose_name="Prioridade")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Aberto')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    sla_deadline = models.DateTimeField(null=True, blank=True, verbose_name="Prazo de Resolução (SLA)")
    closed_date = models.DateTimeField(null=True, blank=True, verbose_name="Data de Fechamento")

    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True, verbose_name="Avaliação")
    feedback = models.TextField(blank=True, null=True, verbose_name="Feedback do Utilizador")

    def __str__(self):
        return self.title


    def get_working_time_delta(self, start, end):
        if start >= end:
            return timedelta(0)
        total = timedelta(0)
        current = start
        work_periods = [(time(8, 0), time(12, 0)), (time(14, 0), time(18, 0))]
        while current < end:
            if current.weekday() < 5: 
                for period_start, period_end in work_periods:
                    period_start_dt = current.replace(hour=period_start.hour, minute=period_start.minute, second=0, microsecond=0)
                    period_end_dt = current.replace(hour=period_end.hour, minute=period_end.minute, second=0, microsecond=0)
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
        """Calcula o tempo útil restante para o fim do prazo de SLA."""
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
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    description = models.TextField(help_text="Descreve o evento. Pode ser um comentário, a solução, o motivo da exclusão, etc.")
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_date']

    def __str__(self):
        return f'{self.event_type} por {self.user.username} em {self.ticket.title}'

class TicketEventImage(models.Model):
    event = models.ForeignKey(TicketEvent, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='ticket_pictures/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imagem para o evento #{self.event.id} do ticket #{self.event.ticket.id}"