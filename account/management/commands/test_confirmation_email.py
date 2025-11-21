from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from account.models import EmailConfirmation


class Command(BaseCommand):
    help = 'Testa o envio de e-mail de confirmação para um usuário específico'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nome de usuário para enviar e-mail de teste',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='E-mail para enviar e-mail de teste',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = options.get('username')
        email = options.get('email')
        
        if not username and not email:
            self.stdout.write(
                self.style.ERROR('Forneça --username ou --email')
            )
            return
        
        try:
            if username:
                user = User.objects.get(username=username)
            else:
                user = User.objects.get(email=email)
            
            self.stdout.write(f'Usuário encontrado: {user.username} ({user.email})')
            self.stdout.write(f'Ativo: {user.is_active}')
            
            confirmation, created = EmailConfirmation.objects.get_or_create(user=user)
            
            if created:
                self.stdout.write(self.style.SUCCESS('Token de confirmação criado'))
            else:
                self.stdout.write(f'Token existente: {confirmation.token}')
                self.stdout.write(f'Criado em: {confirmation.created_at}')
                self.stdout.write(f'Confirmado em: {confirmation.confirmed_at}')
                self.stdout.write(f'Válido: {confirmation.is_valid()}')
            
            confirmation_url = f'http://localhost:8000/account/confirm-email/{confirmation.token}/'
            
            self.stdout.write(f'\nURL de confirmação: {confirmation_url}\n')
            
            html_message = render_to_string('account/email/confirmation_email.html', {
                'user': user,
                'confirmation_url': confirmation_url,
            })
            plain_message = strip_tags(html_message)
            
            self.stdout.write('Enviando e-mail...')
            
            result = send_mail(
                subject='Confirme seu cadastro no Gesticket',
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            if result == 1:
                self.stdout.write(
                    self.style.SUCCESS(f'E-mail enviado com sucesso para {user.email}!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Falha ao enviar e-mail')
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Usuário não encontrado')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro: {str(e)}')
            )
            import traceback
            traceback.print_exc()
