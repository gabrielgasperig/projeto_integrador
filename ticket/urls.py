from django.urls import path
from ticket import views

app_name = 'ticket'

urlpatterns = [
    path('<int:ticket_id>/', views.ticket, name='ticket'),
    path('', views.index, name='index'),
    
]
