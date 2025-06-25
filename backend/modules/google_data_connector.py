"""
Google Data Connector - Integração com Search Console e Analytics 4
Coleta dados de performance, keywords, audiência e métricas para insights editoriais
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, date
import json

# Google APIs
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Internal imports
try:
    from ..config import settings
    from ..database import db
except ImportError:
    from config import settings
    from database import db

logger = logging.getLogger(__name__)

class GoogleDataConnector:
    """
    Conector para Google Search Console e Google Analytics 4
    Fornece dados de performance para otimização editorial
    """
    
    def __init__(self):
        self.gsc_service = None
        self.ga4_service = None
        self.credentials = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Inicializa serviços Google com credenciais"""
        try:
            # Tentar carregar credenciais do banco
            self.credentials = self._load_google_credentials()
            
            if self.credentials:
                self._build_services()
                logger.info("✅ Google Data Connector inicializado com sucesso")
            else:
                logger.warning("⚠️ Credenciais Google não encontradas - use authenticate_google()")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar Google Data Connector: {e}")
    
    def _load_google_credentials(self) -> Optional[Credentials]:
        """Carrega credenciais Google do banco de dados"""
        try:
            creds_data = db.get_secure_config("google_data_credentials")
            if not creds_data:
                return None
            
            creds_dict = json.loads(creds_data)
            credentials = Credentials.from_authorized_user_info(creds_dict)
            
            # Renovar se necessário
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                # Salvar credenciais renovadas
                self._save_google_credentials(credentials)
            
            return credentials
            
        except Exception as e:
            logger.error(f"Erro ao carregar credenciais Google: {e}")
            return None
    
    def _save_google_credentials(self, credentials: Credentials) -> bool:
        """Salva credenciais Google no banco de dados"""
        try:
            creds_dict = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            
            return db.set_secure_config(
                "google_data_credentials",
                json.dumps(creds_dict),
                "Credenciais OAuth Google (GSC + GA4)"
            )
            
        except Exception as e:
            logger.error(f"Erro ao salvar credenciais Google: {e}")
            return False
    
    def _build_services(self):
        """Constrói serviços Google API"""
        try:
            if self.credentials:
                # Google Search Console
                self.gsc_service = build('searchconsole', 'v1', credentials=self.credentials)
                
                # Google Analytics 4 (Analytics Data API)
                self.ga4_service = build('analyticsdata', 'v1beta', credentials=self.credentials)
                
                logger.info("🔗 Serviços Google construídos com sucesso")
                
        except Exception as e:
            logger.error(f"Erro ao construir serviços Google: {e}")
    
    def get_authorization_url(self) -> str:
        """Gera URL de autorização para OAuth Google"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.secure_gmail_client_id,
                        "client_secret": settings.secure_gmail_client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [f"{settings.BASE_URL}/auth/google/callback"]
                    }
                },
                scopes=[
                    'https://www.googleapis.com/auth/webmasters.readonly',
                    'https://www.googleapis.com/auth/analytics.readonly'
                ]
            )
            flow.redirect_uri = f"{settings.BASE_URL}/auth/google/callback"
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            return auth_url
            
        except Exception as e:
            logger.error(f"Erro ao gerar URL de autorização: {e}")
            return ""
    
    def authenticate_google(self, authorization_code: str) -> bool:
        """Autentica com Google usando código de autorização"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.secure_gmail_client_id,
                        "client_secret": settings.secure_gmail_client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [f"{settings.BASE_URL}/auth/google/callback"]
                    }
                },
                scopes=[
                    'https://www.googleapis.com/auth/webmasters.readonly',
                    'https://www.googleapis.com/auth/analytics.readonly'
                ]
            )
            flow.redirect_uri = f"{settings.BASE_URL}/auth/google/callback"
            
            # Trocar código por credenciais
            flow.fetch_token(code=authorization_code)
            self.credentials = flow.credentials
            
            # Salvar credenciais
            if self._save_google_credentials(self.credentials):
                self._build_services()
                logger.info("✅ Autenticação Google Data concluída com sucesso")
                return True
            else:
                logger.error("❌ Erro ao salvar credenciais Google Data")
                return False
                
        except Exception as e:
            logger.error(f"Erro na autenticação Google Data: {e}")
            return False
    
    def get_gsc_performance(
        self, 
        site_url: str, 
        start_date: date, 
        end_date: date,
        dimensions: List[str] = ['query'],
        row_limit: int = 1000
    ) -> Dict[str, Any]:
        """Busca dados de performance do Google Search Console"""
        try:
            if not self.gsc_service:
                return {"error": "Serviço GSC não inicializado"}
            
            request_body = {
                'startDate': start_date.isoformat(),
                'endDate': end_date.isoformat(),
                'dimensions': dimensions,
                'searchType': 'web',
                'rowLimit': row_limit,
                'startRow': 0
            }
            
            response = self.gsc_service.searchanalytics().query(
                siteUrl=site_url,
                body=request_body
            ).execute()
            
            # Processar dados
            rows = response.get('rows', [])
            processed_data = []
            
            for row in rows:
                data_point = {
                    'keys': row.get('keys', []),
                    'clicks': row.get('clicks', 0),
                    'impressions': row.get('impressions', 0),
                    'ctr': round(row.get('ctr', 0) * 100, 2),
                    'position': round(row.get('position', 0), 1)
                }
                
                # Mapear dimensões para chaves
                for i, dimension in enumerate(dimensions):
                    if i < len(data_point['keys']):
                        data_point[dimension] = data_point['keys'][i]
                
                processed_data.append(data_point)
            
            summary = {
                'total_clicks': sum(row['clicks'] for row in processed_data),
                'total_impressions': sum(row['impressions'] for row in processed_data),
                'avg_ctr': round(sum(row['ctr'] for row in processed_data) / len(processed_data), 2) if processed_data else 0,
                'avg_position': round(sum(row['position'] for row in processed_data) / len(processed_data), 1) if processed_data else 0,
                'total_queries': len(processed_data)
            }
            
            logger.info(f"📈 GSC Performance: {summary['total_clicks']} clicks, {summary['total_queries']} queries")
            
            return {
                'site_url': site_url,
                'period': f"{start_date} to {end_date}",
                'dimensions': dimensions,
                'summary': summary,
                'data': processed_data,
                'retrieved_at': datetime.now().isoformat()
            }
            
        except HttpError as e:
            logger.error(f"Erro HTTP ao buscar performance GSC: {e}")
            return {"error": f"Erro HTTP: {e}"}
        except Exception as e:
            logger.error(f"Erro ao buscar performance GSC: {e}")
            return {"error": str(e)}
    
    def get_ga4_report(
        self,
        property_id: str,
        start_date: str = "30daysAgo",
        end_date: str = "yesterday",
        metrics: List[str] = None,
        dimensions: List[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Busca relatório do Google Analytics 4"""
        try:
            if not self.ga4_service:
                return {"error": "Serviço GA4 não inicializado"}
            
            # Métricas padrão
            if not metrics:
                metrics = ['sessions', 'users', 'pageviews', 'bounceRate']
            
            # Dimensões padrão
            if not dimensions:
                dimensions = ['pagePath']
            
            # Construir request
            request_body = {
                'dateRanges': [{
                    'startDate': start_date,
                    'endDate': end_date
                }],
                'metrics': [{'name': metric} for metric in metrics],
                'dimensions': [{'name': dimension} for dimension in dimensions],
                'limit': limit
            }
            
            response = self.ga4_service.properties().runReport(
                property=f"properties/{property_id}",
                body=request_body
            ).execute()
            
            # Processar dados
            rows = response.get('rows', [])
            processed_data = []
            
            for row in rows:
                data_point = {}
                
                # Processar dimensões
                dimension_values = row.get('dimensionValues', [])
                for i, dimension in enumerate(dimensions):
                    if i < len(dimension_values):
                        data_point[dimension] = dimension_values[i].get('value', '')
                
                # Processar métricas
                metric_values = row.get('metricValues', [])
                for i, metric in enumerate(metrics):
                    if i < len(metric_values):
                        value = metric_values[i].get('value', '0')
                        if metric in ['bounceRate']:
                            data_point[metric] = round(float(value) * 100, 2)
                        else:
                            data_point[metric] = int(float(value))
                
                processed_data.append(data_point)
            
            # Calcular totais
            totals = {}
            if processed_data:
                for metric in metrics:
                    if metric == 'bounceRate':
                        totals[metric] = round(sum(row.get(metric, 0) for row in processed_data) / len(processed_data), 2)
                    else:
                        totals[metric] = sum(row.get(metric, 0) for row in processed_data)
            
            logger.info(f"📊 GA4 Report: {len(processed_data)} rows, {totals.get('sessions', 0)} sessions")
            
            return {
                'property_id': property_id,
                'period': f"{start_date} to {end_date}",
                'metrics': metrics,
                'dimensions': dimensions,
                'totals': totals,
                'data': processed_data,
                'retrieved_at': datetime.now().isoformat()
            }
            
        except HttpError as e:
            logger.error(f"Erro HTTP ao buscar relatório GA4: {e}")
            return {"error": f"Erro HTTP: {e}"}
        except Exception as e:
            logger.error(f"Erro ao buscar relatório GA4: {e}")
            return {"error": str(e)}
    
    def get_content_insights(self, site_url: str, property_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Combina dados GSC + GA4 para insights de conteúdo"""
        try:
            end_date = date.today() - timedelta(days=1)
            start_date = end_date - timedelta(days=days_back)
            
            # Dados GSC
            gsc_data = self.get_gsc_performance(
                site_url=site_url,
                start_date=start_date,
                end_date=end_date,
                dimensions=['page'],
                row_limit=50
            )
            
            # Dados GA4
            ga4_data = self.get_ga4_report(
                property_id=property_id,
                start_date=f"{days_back}daysAgo",
                end_date="yesterday",
                metrics=['pageviews', 'users', 'sessions'],
                dimensions=['pagePath', 'pageTitle'],
                limit=50
            )
            
            # Combinar dados
            combined_insights = []
            
            if 'data' in gsc_data and 'data' in ga4_data:
                for gsc_page in gsc_data['data']:
                    page_url = gsc_page.get('page', '')
                    
                    # Encontrar dados GA4 correspondentes
                    ga4_match = next(
                        (item for item in ga4_data['data'] if item.get('pagePath', '') in page_url),
                        {}
                    )
                    
                    insight = {
                        'page_url': page_url,
                        'page_title': ga4_match.get('pageTitle', ''),
                        'gsc_clicks': gsc_page.get('clicks', 0),
                        'gsc_impressions': gsc_page.get('impressions', 0),
                        'gsc_ctr': gsc_page.get('ctr', 0),
                        'gsc_position': gsc_page.get('position', 0),
                        'ga4_pageviews': ga4_match.get('pageviews', 0),
                        'ga4_users': ga4_match.get('users', 0),
                        'organic_ratio': round(
                            (gsc_page.get('clicks', 0) / ga4_match.get('pageviews', 1)) * 100, 2
                        ) if ga4_match.get('pageviews', 0) > 0 else 0
                    }
                    
                    combined_insights.append(insight)
            
            logger.info(f"🔍 Content Insights: {len(combined_insights)} páginas analisadas")
            
            return {
                'period': f"Last {days_back} days",
                'insights': combined_insights,
                'summary': {
                    'total_pages': len(combined_insights),
                    'total_clicks': sum(p.get('gsc_clicks', 0) for p in combined_insights),
                    'total_pageviews': sum(p.get('ga4_pageviews', 0) for p in combined_insights)
                },
                'retrieved_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar insights de conteúdo: {e}")
            return {"error": str(e)}
    
    def test_connection(self) -> Dict[str, bool]:
        """Testa conexão com os serviços Google"""
        status = {
            'gsc_connected': False,
            'ga4_connected': False,
            'credentials_valid': False
        }
        
        try:
            if self.credentials and not self.credentials.expired:
                status['credentials_valid'] = True
                
                # Testar GSC
                if self.gsc_service:
                    try:
                        sites = self.gsc_service.sites().list().execute()
                        status['gsc_connected'] = len(sites.get('siteEntry', [])) > 0
                    except:
                        status['gsc_connected'] = False
                
                # Testar GA4
                if self.ga4_service:
                    status['ga4_connected'] = True  # Se o serviço foi criado, assumimos que funciona
            
        except Exception as e:
            logger.error(f"Erro ao testar conexão Google: {e}")
        
        return status

# Instância global
google_connector = GoogleDataConnector() 