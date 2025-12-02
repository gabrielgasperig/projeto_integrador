from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_update, name='user_update'),
    path('confirm-email/<uuid:token>/', views.confirm_email_view, name='confirm_email'),
    path('resend-confirmation/<int:user_id>/', views.resend_confirmation_email, name='resend_confirmation'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('reset-password/<uuid:token>/', views.password_reset_confirm, name='password_reset_confirm'),
]