from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ticket.models import Ticket, TicketImage, TicketEvent
from utils.gmail_integration import get_gmail_service
from django.conf import settings
from django.core.files.base import ContentFile
import base64
import email
import re

class Command(BaseCommand):
    help = 'Importa e-mails do Gmail e cria tickets automaticamente.'

    def handle(self, *args, **options):
        service = get_gmail_service()
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
        messages = results.get('messages', [])
        User = get_user_model()
        for msg in messages:
            msg_id = msg['id']
            msg_data = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            payload = msg_data['payload']
            headers = payload.get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sem título')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), None)
            # Extrai o e-mail do remetente (pode vir como 'Nome <email@dominio.com>')
            email_match = re.search(r'<(.+?)>', from_email) if from_email else None
            sender_email = email_match.group(1) if email_match else (from_email or '').strip()
            # Verifica se o remetente está cadastrado
            user = User.objects.filter(email__iexact=sender_email).first()
            if not user:
                self.stdout.write(self.style.WARNING(f'Remetente não cadastrado: {sender_email}. Ticket não criado.'))
                # Marca o e-mail como lido mesmo assim para não processar novamente
                service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
                continue
            # Corpo do e-mail
            body = ''
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
            else:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            # Cria o ticket
            ticket = Ticket.objects.create(
                title=subject[:100],
                description=body,
                owner=user,
            )
            # Cria evento de criação no histórico
            TicketEvent.objects.create(
                ticket=ticket,
                user=user,
                event_type='CRIAÇÃO',
                description='Ticket criado por e-mail.'
            )
            # Salva anexos (imagens)
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['filename'] and 'image' in part['mimeType']:
                        file_data = part['body'].get('data')
                        if not file_data and 'attachmentId' in part['body']:
                            att_id = part['body']['attachmentId']
                            att = service.users().messages().attachments().get(userId='me', messageId=msg_id, id=att_id).execute()
                            file_data = att['data']
                        if file_data:
                            file_content = base64.urlsafe_b64decode(file_data)
                            TicketImage.objects.create(
                                ticket=ticket,
                                image=ContentFile(file_content, name=part['filename'])
                            )
            # Marca o e-mail como lido
            service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
            self.stdout.write(self.style.SUCCESS(f'Ticket criado: {ticket.title}'))
