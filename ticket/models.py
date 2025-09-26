from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Ticket(models.Model):
    
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
        (1, '⭐ Péssimo'),
        (2, '⭐⭐ Ruim'),
        (3, '⭐⭐⭐ Regular'),
        (4, '⭐⭐⭐⭐ Bom'),
        (5, '⭐⭐⭐⭐⭐ Ótimo'),
    ]
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True, verbose_name="Avaliação")
    feedback = models.TextField(blank=True, null=True, verbose_name="Feedback do Utilizador")

    def __str__(self):
        return self.title

    @property
    def time_to_sla(self):
        """Calcula o tempo restante para o fim do prazo de SLA."""
        if not self.sla_deadline or self.status == 'Fechado':
            return None
        return self.sla_deadline - timezone.now()

    @property
    def sla_status(self):
        """Retorna uma string descrevendo o status atual do SLA."""
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