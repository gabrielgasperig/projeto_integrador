from django.urls import path
from ticket import views

app_name = 'ticket'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    
    # ticket (CRUD)
    path('ticket/<int:ticket_id>/detail/', views.ticket, name='ticket'),
    path('ticket/create/', views.create, name='create'),\
    path('ticket/<int:ticket_id>/update/', views.update, name='update'),
    path('ticket/<int:ticket_id>/delete/', views.delete, name='delete'),

    # user
    path('user/create/', views.register, name='register'),
    path('user/login/', views.login_view, name='login'),
    path('user/logout/', views.logout_view, name='logout'),
    path('user/update/', views.user_update, name='user_update'),
]