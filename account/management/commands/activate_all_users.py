from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Ativa todos os usuários existentes no sistema (usar apenas para migração)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma a ativação de todos os usuários',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        if not options['confirm']:
            inactive_count = User.objects.filter(is_active=False).count()
            self.stdout.write(
                self.style.WARNING(
                    f'Este comando irá ativar {inactive_count} usuário(s) inativo(s).\n'
                    'Execute novamente com --confirm para confirmar.'
                )
            )
            return
        
        inactive_users = User.objects.filter(is_active=False)
        count = inactive_users.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('Nenhum usuário inativo encontrado.'))
            return
        
        inactive_users.update(is_active=True)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'{count} usuário(s) ativado(s) com sucesso!'
            )
        )
