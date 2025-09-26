from django.urls import path
from . import views

app_name = 'ticket'

urlpatterns = [
    # URLs PRINCIPAIS
    path('', views.index, name='index'),
    
    # URLs TICKET
    path('meus-tickets/', views.my_tickets, name='my_tickets'),
    path('todos-tickets/', views.all_tickets, name='all_tickets'),
    path('ticket/create/', views.create, name='create'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<int:ticket_id>/update/', views.update, name='update'),
    path('ticket/<int:ticket_id>/delete/', views.delete, name='delete'),
    path('ticket/<int:ticket_id>/assign/', views.assign_ticket, name='assign_ticket'),
    path('ticket/<int:ticket_id>/conclude/', views.conclude_ticket, name='conclude_ticket'),
    path('ticket/<int:ticket_id>/transfer/', views.transfer_ticket, name='transfer_ticket'),

    # URLs PERFIL
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_update, name='user_update'),
]