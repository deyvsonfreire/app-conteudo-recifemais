"""
Cliente Gmail com OAuth2 para processamento de emails
"""
import os
import pickle
import base64
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..config import settings

logger = logging.getLogger(__name__)

class GmailClient:
    def __init__(self):
        self.service = None
        self.credentials = None
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        self.token_file = 'gmail_token.pickle'
        self.credentials_file = 'gmail_credentials.json'
    
    def get_authorization_url(self) -> str:
        """Gera URL de autorização OAuth"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GMAIL_CLIENT_ID,
                        "client_secret": settings.GMAIL_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [settings.GMAIL_REDIRECT_URI]
                    }
                },
                scopes=self.scopes
            )
            flow.redirect_uri = settings.GMAIL_REDIRECT_URI
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            return authorization_url
            
        except Exception as e:
            logger.error(f"Erro ao gerar URL de autorização: {e}")
            return None
    
    def handle_oauth_callback(self, authorization_code: str) -> bool:
        """Processa callback OAuth e salva credenciais"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GMAIL_CLIENT_ID,
                        "client_secret": settings.GMAIL_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [settings.GMAIL_REDIRECT_URI]
                    }
                },
                scopes=self.scopes
            )
            flow.redirect_uri = settings.GMAIL_REDIRECT_URI
            
            # Trocar código por token
            flow.fetch_token(code=authorization_code)
            
            # Salvar credenciais
            with open(self.token_file, 'wb') as token:
                pickle.dump(flow.credentials, token)
            
            self.credentials = flow.credentials
            logger.info("Credenciais OAuth salvas com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro no callback OAuth: {e}")
            return False
    
    def load_credentials(self) -> bool:
        """Carrega credenciais salvas"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
                
                # Verificar se precisa renovar
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    
                    # Salvar credenciais atualizadas
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(self.credentials, token)
                
                return self.credentials and self.credentials.valid
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao carregar credenciais: {e}")
            return False
    
    def authenticate(self) -> bool:
        """Autentica com Gmail"""
        try:
            if not self.load_credentials():
                logger.warning("Credenciais não encontradas ou inválidas")
                return False
            
            self.service = build('gmail', 'v1', credentials=self.credentials)
            
            # Testar conexão
            profile = self.service.users().getProfile(userId='me').execute()
            logger.info(f"Autenticado com Gmail: {profile.get('emailAddress')}")
            return True
            
        except Exception as e:
            logger.error(f"Erro na autenticação Gmail: {e}")
            return False
    
    def get_recent_emails(self, query: str = "", max_results: int = 50) -> List[Dict[str, Any]]:
        """Busca emails recentes"""
        if not self.service:
            logger.error("Serviço Gmail não autenticado")
            return []
        
        try:
            # Buscar emails dos últimos 7 dias por padrão
            if not query:
                week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d')
                query = f"after:{week_ago}"
            
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            logger.info(f"Encontrados {len(emails)} emails")
            return emails
            
        except HttpError as e:
            logger.error(f"Erro ao buscar emails: {e}")
            return []
    
    def get_emails_from_assessorias(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Busca emails específicos de assessorias de imprensa"""
        
        # Termos comuns em emails de assessoria
        assessoria_terms = [
            "assessoria",
            "imprensa", 
            "comunicação",
            "release",
            "nota à imprensa",
            "convite para cobertura",
            "evento",
            "prefeitura",
            "governo",
            "secretaria"
        ]
        
        # Construir query
        date_filter = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
        terms_query = " OR ".join([f'"{term}"' for term in assessoria_terms])
        query = f"after:{date_filter} AND ({terms_query})"
        
        return self.get_recent_emails(query, max_results=100)
    
    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Extrai detalhes completos de um email"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            # Extrair headers importantes
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Extrair corpo do email
            body = self._extract_email_body(message['payload'])
            
            # Converter data
            received_at = self._parse_email_date(date_str)
            
            return {
                'id': message_id,
                'sender': sender,
                'subject': subject,
                'body': body,
                'received_at': received_at,
                'thread_id': message.get('threadId'),
                'labels': message.get('labelIds', [])
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair detalhes do email {message_id}: {e}")
            return None
    
    def _extract_email_body(self, payload: Dict) -> str:
        """Extrai o corpo do email"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def _parse_email_date(self, date_str: str) -> datetime:
        """Converte string de data do email para datetime"""
        from email.utils import parsedate_to_datetime
        try:
            return parsedate_to_datetime(date_str)
        except:
            return datetime.now()
    
    def mark_as_processed(self, message_id: str) -> bool:
        """Marca email como processado (adiciona label)"""
        try:
            # Criar label "PROCESSED" se não existir
            self._ensure_processed_label()
            
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['PROCESSED']}
            ).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao marcar email como processado: {e}")
            return False
    
    def _ensure_processed_label(self):
        """Garante que o label PROCESSED existe"""
        try:
            labels = self.service.users().labels().list(userId='me').execute()
            
            for label in labels.get('labels', []):
                if label['name'] == 'PROCESSED':
                    return
            
            # Criar label
            label_object = {
                'name': 'PROCESSED',
                'messageListVisibility': 'hide',
                'labelListVisibility': 'labelShow'
            }
            
            self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
        except Exception as e:
            logger.error(f"Erro ao criar label PROCESSED: {e}")

# Instância global
gmail_client = GmailClient() 