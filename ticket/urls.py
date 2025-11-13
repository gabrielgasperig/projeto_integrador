from django.urls import path
from .views import ticket_views, admin_views

app_name = 'ticket'

urlpatterns = [
    path('', admin_views.index, name='index'),
    
    path('meus-tickets/', ticket_views.my_tickets, name='my_tickets'),
    path('todos-tickets/', admin_views.all_tickets, name='all_tickets'),
    path('solutions/', ticket_views.solutions, name='solutions'),
    path('ticket/create/', ticket_views.create, name='create'),
    path('ticket/<int:ticket_id>/', ticket_views.ticket_detail, name='ticket_detail'),
    path('ticket/<int:ticket_id>/update/', ticket_views.update, name='update'),
    path('ticket/<int:ticket_id>/delete/', ticket_views.delete, name='delete'),
    path('ticket/<int:ticket_id>/assign/', ticket_views.assign_ticket, name='assign_ticket'),
    path('ticket/<int:ticket_id>/conclude/', ticket_views.conclude_ticket, name='conclude_ticket'),
    path('ticket/<int:ticket_id>/transfer/', ticket_views.transfer_ticket, name='transfer_ticket'),
]