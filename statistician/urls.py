from django.urls import path
from . import views

app_name = 'statistician'

urlpatterns = [
    path('', views.index, name='index'),
]