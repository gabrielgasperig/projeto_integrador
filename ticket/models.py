from django.db import models
from django.conf import settings

class Ticket(models.Model):
    
    STATUS_CHOICES = [
        ('Aberto', 'Aberto'),
        ('Em Andamento', 'Em Andamento'),
        ('Fechado', 'Fechado'),
    ]
    # 1. ADICIONÁMOS AS ESCOLHAS DE PRIORIDADE AQUI
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