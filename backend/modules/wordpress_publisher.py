"""
Publicador de conteúdo para WordPress
"""
import requests
from requests.auth import HTTPBasicAuth
from config import settings
from typing import Dict, Any, Optional, List
import logging
import base64

logger = logging.getLogger(__name__)

class WordPressPublisher:
    def __init__(self):
        self.base_url = settings.WORDPRESS_URL.rstrip('/')
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.auth = HTTPBasicAuth(
            settings.WORDPRESS_USERNAME,
            settings.WORDPRESS_PASSWORD
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
    
    def get_recent_posts(self, limit: int = 10) -> List[Dict]:
        """Busca posts recentes"""
        try:
            response = requests.get(
                f"{self.api_url}/posts",
                params={
                    "per_page": limit,
                    "orderby": "date",
                    "order": "desc"
                },
                auth=self.auth
            )
            
            if response.status_code == 200:
                return response.json()
            
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar posts recentes: {e}")
            return []

# Instância global
wp_publisher = WordPressPublisher() 