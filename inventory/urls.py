from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/<str:asset_type>/', views.create_asset, name='create_asset'),
]