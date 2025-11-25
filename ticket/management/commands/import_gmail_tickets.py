from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ticket.models import Ticket, TicketImage, TicketEvent, Location
from utils.gmail_integration import get_gmail_service
from django.conf import settings
from datetime import timedelta
from django.core.files.base import ContentFile
import base64
import email
import re

class Command(BaseCommand):
    help = 'Import Gmail emails and create tickets automatically.'

    def handle(self, *args, **options):
        service = get_gmail_service()
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
        messages = results.get('messages', [])
        User = get_user_model()
        # Palavras-chave para identificar e-mails de notificação do sistema
        notification_keywords = [
            'novo comentário no ticket',
            'avaliação recebida no ticket',
            'seu ticket foi fechado',
        ]
        for msg in messages:
            msg_id = msg['id']
            msg_data = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            payload = msg_data['payload']
            headers = payload.get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), None)
            # Ignora e-mails de notificação do sistema pelo assunto
            if any(keyword.lower() in subject.lower() for keyword in notification_keywords):
                self.stdout.write(self.style.WARNING(f'Email ignored (system notification): {subject}'))
                service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
                continue
            # Extrai o e-mail do remetente (pode vir como 'Nome <email@dominio.com>')
            email_match = re.search(r'<(.+?)>', from_email) if from_email else None
            sender_email = email_match.group(1) if email_match else (from_email or '').strip()
            # Verifica se o remetente está cadastrado
            user = User.objects.filter(email__iexact=sender_email).first()
            if not user:
                self.stdout.write(self.style.WARNING(f'Sender not registered: {sender_email}. Ticket not created.'))
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
            # Extrai categoria, subcategoria e local do corpo do e-mail
            category_name = None
            subcategory_name = None
            location_name = None
            category_match = re.search(r'^Categoria:\s*(.+)$', body, re.MULTILINE | re.IGNORECASE)
            subcategory_match = re.search(r'^Subcategoria:\s*(.+)$', body, re.MULTILINE | re.IGNORECASE)
            location_match = re.search(r'^Local:\s*(.+)$', body, re.MULTILINE | re.IGNORECASE)
            if category_match:
                category_name = category_match.group(1).strip()
            if subcategory_match:
                subcategory_name = subcategory_match.group(1).strip()
            if location_match:
                location_name = location_match.group(2).strip()
            # Remove linhas identificadoras do corpo para a descrição
            body_without_category = re.sub(r'^Categoria:.*\n?', '', body, flags=re.MULTILINE | re.IGNORECASE)
            body_without_category = re.sub(r'^Subcategoria:.*\n?', '', body_without_category, flags=re.MULTILINE | re.IGNORECASE)
            body_without_category = re.sub(r'^Local:.*\n?', '', body_without_category, flags=re.MULTILINE | re.IGNORECASE)
            # Busca categoria, subcategoria e local no banco de dados
            from ticket.models import Category, Subcategory
            categories_exist = Category.objects.exists()
            category_obj = None
            subcategory_obj = None
            location_obj = None
            if category_name:
                category_obj = Category.objects.filter(name__iexact=category_name).first()
            if subcategory_name and category_obj:
                subcategory_obj = Subcategory.objects.filter(name__iexact=subcategory_name, category=category_obj).first()
            if location_name:
                location_obj = Location.objects.filter(name__iexact=location_name, is_active=True).first()
            if not location_obj:
                active_locations = list(Location.objects.filter(is_active=True))
                detected = []
                for loc in active_locations:
                    pattern = r'\\b' + re.escape(loc.name) + r'\\b'
                    if re.search(pattern, subject, re.IGNORECASE) or re.search(pattern, body, re.IGNORECASE):
                        detected.append(loc)
                if len(detected) == 1:
                    location_obj = detected[0]

            # Só exige categoria se houver alguma cadastrada
            if categories_exist and not category_obj:
                self.stdout.write(self.style.WARNING(f"Category not found or not provided in email: '{category_name}'. Ticket not created."))
                service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
                continue
            # Define prioridade padrão e calcula o SLA
            priority = 'A definir'
            from django.utils import timezone
            sla_deadline = Ticket.calculate_sla_deadline(timezone.now(), priority)
            ticket = Ticket.objects.create(
                title=subject[:100],
                description=body_without_category.strip(),
                owner=user,
                priority=priority,
                sla_deadline=sla_deadline,
                category=category_obj,
                subcategory=subcategory_obj,
                location=location_obj,
            )
            # Cria evento de criação no histórico
            creation_desc = 'Ticket criado por e-mail.'
            if location_obj:
                creation_desc += f" Local detectado: {location_obj.name}."
            TicketEvent.objects.create(
                ticket=ticket,
                user=user,
                event_type='CRIAÇÃO',
                description=creation_desc
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
            self.stdout.write(self.style.SUCCESS(f'Ticket created: {ticket.title}'))