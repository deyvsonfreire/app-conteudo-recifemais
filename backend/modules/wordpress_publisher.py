"""
Publicador de conteúdo para WordPress
"""
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, Any, Optional, List

# Import com fallback para desenvolvimento e produção
try:
    from ..config import settings
except ImportError:
    from config import settings
import logging
import base64

logger = logging.getLogger(__name__)

class WordPressPublisher:
    def __init__(self):
        self.base_url = settings.WORDPRESS_URL.rstrip('/')
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.auth = HTTPBasicAuth(
            settings.secure_wordpress_username,
            settings.secure_wordpress_password
        )
    
    def test_connection(self) -> bool:
        """Testa conexão com WordPress"""
        try:
            response = requests.get(f"{self.api_url}/users/me", auth=self.auth)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao conectar com WordPress: {e}")
            return False
    
    def create_draft_post(self, content_data: Dict[str, Any]) -> Optional[Dict]:
        """Cria um rascunho no WordPress"""
        try:
            # Preparar dados do post
            post_data = {
                "title": content_data.get("titulo", "Post sem título"),
                "content": content_data.get("conteudo", ""),
                "status": "draft",  # Sempre como rascunho
                "excerpt": content_data.get("meta_descricao", ""),
                "meta": {
                    "_yoast_wpseo_metadesc": content_data.get("meta_descricao", ""),
                    "_ai_generated": "true",
                    "_ai_category": content_data.get("categoria", ""),
                    "_ai_relevance_score": content_data.get("relevancia_score", 0)
                }
            }
            
            # Adicionar tags se existirem
            if content_data.get("tags"):
                # Primeiro, criar/buscar tags
                tag_ids = []
                for tag_name in content_data["tags"]:
                    tag_id = self._get_or_create_tag(tag_name)
                    if tag_id:
                        tag_ids.append(tag_id)
                
                if tag_ids:
                    post_data["tags"] = tag_ids
            
            # Definir categoria se especificada
            category_id = self._get_category_id(content_data.get("categoria"))
            if category_id:
                post_data["categories"] = [category_id]
            
            # Criar post
            response = requests.post(
                f"{self.api_url}/posts",
                json=post_data,
                auth=self.auth,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                post_info = response.json()
                logger.info(f"Post criado com sucesso: ID {post_info['id']}")
                return {
                    "id": post_info["id"],
                    "url": post_info["link"],
                    "edit_url": f"{self.base_url}/wp-admin/post.php?post={post_info['id']}&action=edit",
                    "status": "draft"
                }
            else:
                logger.error(f"Erro ao criar post: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao criar post no WordPress: {e}")
            return None
    
    def update_post(self, post_id: int, content_data: Dict[str, Any]) -> bool:
        """Atualiza um post existente"""
        try:
            post_data = {
                "title": content_data.get("titulo"),
                "content": content_data.get("conteudo"),
                "excerpt": content_data.get("meta_descricao", "")
            }
            
            # Remover campos None
            post_data = {k: v for k, v in post_data.items() if v is not None}
            
            response = requests.post(
                f"{self.api_url}/posts/{post_id}",
                json=post_data,
                auth=self.auth,
                headers={"Content-Type": "application/json"}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Erro ao atualizar post {post_id}: {e}")
            return False
    
    def publish_post(self, post_id: int) -> bool:
        """Publica um post (muda status de draft para publish)"""
        try:
            response = requests.post(
                f"{self.api_url}/posts/{post_id}",
                json={"status": "publish"},
                auth=self.auth,
                headers={"Content-Type": "application/json"}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Erro ao publicar post {post_id}: {e}")
            return False
    
    def delete_post(self, post_id: int) -> bool:
        """Deleta um post"""
        try:
            response = requests.delete(
                f"{self.api_url}/posts/{post_id}",
                auth=self.auth
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Erro ao deletar post {post_id}: {e}")
            return False
    
    def get_post_info(self, post_id: int) -> Optional[Dict]:
        """Busca informações de um post"""
        try:
            response = requests.get(
                f"{self.api_url}/posts/{post_id}",
                auth=self.auth
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar post {post_id}: {e}")
            return None
    
    def _get_or_create_tag(self, tag_name: str) -> Optional[int]:
        """Busca ou cria uma tag"""
        try:
            # Buscar tag existente
            response = requests.get(
                f"{self.api_url}/tags",
                params={"search": tag_name},
                auth=self.auth
            )
            
            if response.status_code == 200:
                tags = response.json()
                for tag in tags:
                    if tag["name"].lower() == tag_name.lower():
                        return tag["id"]
            
            # Criar nova tag
            response = requests.post(
                f"{self.api_url}/tags",
                json={"name": tag_name},
                auth=self.auth,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                return response.json()["id"]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao gerenciar tag '{tag_name}': {e}")
            return None
    
    def _get_category_id(self, category_name: str) -> Optional[int]:
        """Busca ID da categoria pelo nome"""
        if not category_name:
            return None
        
        try:
            response = requests.get(
                f"{self.api_url}/categories",
                params={"search": category_name},
                auth=self.auth
            )
            
            if response.status_code == 200:
                categories = response.json()
                for category in categories:
                    if category["name"].lower() == category_name.lower():
                        return category["id"]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar categoria '{category_name}': {e}")
            return None
    
    def get_recent_posts(self, limit: int = 50) -> List[Dict]:
        """Busca posts recentes do WordPress"""
        try:
            url = f"{self.api_url}/posts"
            params = {
                'per_page': min(limit, 100),  # WordPress limita a 100 por página
                'status': 'publish',
                'orderby': 'date',
                'order': 'desc'
            }
            
            response = requests.get(url, params=params, auth=self.auth, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao buscar posts recentes: {e}")
            return []
    
    def extract_clean_content(self, html_content: str) -> str:
        """Extrai texto limpo do conteúdo HTML do WordPress"""
        try:
            from bs4 import BeautifulSoup
            
            # Remover HTML tags
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remover scripts e styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extrair texto
            text = soup.get_text()
            
            # Limpar espaços extras
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except ImportError:
            # Fallback simples sem BeautifulSoup
            import re
            # Remover tags HTML básicas
            clean = re.sub('<[^<]+?>', '', html_content)
            # Limpar espaços extras
            clean = ' '.join(clean.split())
            return clean
            
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo limpo: {e}")
            return html_content  # Retorna o original se falhar
    
    def get_posts_with_external_links(self, limit: int = 50) -> List[Dict]:
        """Busca posts que contêm links externos para análise de referências"""
        try:
            url = f"{self.api_url}/posts"
            params = {
                'per_page': min(limit, 100),
                'status': 'publish',
                'orderby': 'date',
                'order': 'desc',
                '_embed': True  # Inclui metadados completos
            }
            
            response = requests.get(url, params=params, auth=self.auth, timeout=30)
            response.raise_for_status()
            
            posts = response.json()
            posts_with_links = []
            
            for post in posts:
                content = post.get('content', {}).get('rendered', '')
                
                # Extrair links externos
                external_links = self.extract_external_links(content)
                
                if external_links:
                    post['external_links'] = external_links
                    posts_with_links.append(post)
            
            return posts_with_links
            
        except Exception as e:
            logger.error(f"Erro ao buscar posts com links externos: {e}")
            return []
    
    def extract_external_links(self, html_content: str) -> List[Dict]:
        """Extrai links externos do conteúdo HTML"""
        try:
            from bs4 import BeautifulSoup
            import urllib.parse
            
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            
            # Domínio do site WordPress
            wp_domain = urllib.parse.urlparse(self.base_url).netloc
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Verificar se é link externo
                if href.startswith('http') and wp_domain not in href:
                    links.append({
                        'url': href,
                        'text': link.get_text().strip(),
                        'title': link.get('title', '')
                    })
            
            return links
            
        except Exception as e:
            logger.error(f"Erro ao extrair links externos: {e}")
            return []
    
    def get_posts_by_category(self, category_slug: str, limit: int = 20) -> List[Dict]:
        """Busca posts por categoria específica"""
        try:
            # Primeiro, buscar ID da categoria
            cat_response = requests.get(
                f"{self.api_url}/categories",
                params={'slug': category_slug},
                auth=self.auth,
                timeout=30
            )
            
            if not cat_response.ok:
                logger.error(f"Categoria '{category_slug}' não encontrada")
                return []
            
            categories = cat_response.json()
            if not categories:
                return []
            
            category_id = categories[0]['id']
            
            # Buscar posts da categoria
            url = f"{self.api_url}/posts"
            params = {
                'categories': category_id,
                'per_page': min(limit, 100),
                'status': 'publish',
                'orderby': 'date',
                'order': 'desc',
                '_embed': True
            }
            
            response = requests.get(url, params=params, auth=self.auth, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao buscar posts por categoria: {e}")
            return []
    
    def get_post_analytics_data(self, post_id: int) -> Dict:
        """Busca dados analíticos básicos de um post via WordPress API"""
        try:
            url = f"{self.api_url}/posts/{post_id}"
            params = {
                '_embed': True,
                '_fields': 'id,title,link,date,modified,categories,tags,comment_status,_embedded'
            }
            
            response = requests.get(url, params=params, auth=self.auth, timeout=30)
            response.raise_for_status()
            
            post_data = response.json()
            
            # Extrair dados úteis para analytics
            analytics = {
                'post_id': post_data.get('id'),
                'title': post_data.get('title', {}).get('rendered', ''),
                'url': post_data.get('link', ''),
                'publish_date': post_data.get('date', ''),
                'last_modified': post_data.get('modified', ''),
                'categories': [cat.get('name', '') for cat in post_data.get('_embedded', {}).get('wp:term', [[]])[0]],
                'tags': [tag.get('name', '') for tag in post_data.get('_embedded', {}).get('wp:term', [[], []])[1]],
                'comments_enabled': post_data.get('comment_status') == 'open'
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados analíticos do post {post_id}: {e}")
            return {}

# Instância global
wp_publisher = WordPressPublisher() 