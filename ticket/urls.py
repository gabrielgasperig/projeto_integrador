from django.urls import path
from ticket import views

app_name = 'ticket'

urlpatterns = [
    path('', views.index, name='index'),
]
