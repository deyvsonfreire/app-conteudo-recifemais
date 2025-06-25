"""
Aplicação FastAPI principal - RecifeMais Conteúdo
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import hashlib
from datetime import datetime
import httpx
import os

from .config import settings
from .database import db
from .modules.ai_processor import ai_processor
from .modules.wordpress_publisher import wp_publisher
from .modules.gmail_client import gmail_client
from .modules.realtime_notifications import realtime_manager
from .modules.google_data_connector import google_connector
from .modules.auth_manager import auth_manager
from .modules.email_workflow import email_workflow

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema de automação inteligente de conteúdo para RecifeMais"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar arquivos estáticos (frontend)
# No Docker, o frontend está em /app/frontend
frontend_path = os.path.join("/app", "frontend")
if not os.path.exists(frontend_path):
    # Fallback para desenvolvimento local
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Modelos Pydantic
class EmailInput(BaseModel):
    sender: str
    subject: str
    content: str
    received_at: Optional[datetime] = None

class ProcessEmailResponse(BaseModel):
    success: bool
    message: str
    email_id: Optional[str] = None
    wordpress_post_id: Optional[int] = None
    processing_cost: Optional[float] = None

class ContentData(BaseModel):
    titulo: str
    conteudo: str
    categoria: Optional[str] = None
    meta_descricao: Optional[str] = None
    tags: Optional[List[str]] = None

# ==========================================
# AUTH MODELS
# ==========================================

class LoginRequest(BaseModel):
    email: str
    password: str

class CreateUserRequest(BaseModel):
    email: str
    password: str
    role: str = "viewer"
    metadata: Optional[Dict] = None

class UpdateUserRoleRequest(BaseModel):
    user_id: str
    new_role: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ==========================================
# EMAIL WORKFLOW MODELS
# ==========================================

class EmailWorkflowAction(BaseModel):
    action: str
    notes: Optional[str] = None
    metadata: Optional[Dict] = None

class ApproveContentRequest(BaseModel):
    rating: int = 5  # 1-5
    notes: Optional[str] = None
    modifications: Optional[Dict] = None

class PreparePublishRequest(BaseModel):
    titulo: str
    conteudo: str
    categoria: Optional[str] = None
    tags: Optional[List[str]] = None
    meta_descricao: Optional[str] = None

class RejectEmailRequest(BaseModel):
    reason: str

class UpdatePriorityRequest(BaseModel):
    priority: int  # 1=alta, 2=média, 3=baixa

class AssignEmailRequest(BaseModel):
    assigned_to: str

# No início do arquivo, após os imports, adicionar função helper
def get_service_key():
    """Helper para obter service key do Supabase"""
    return settings.secure_supabase_service_key or settings.SUPABASE_SERVICE_KEY

# Endpoints

@app.get("/")
async def root():
    """Serve a interface web principal"""
    # No Docker, o frontend está em /app/frontend
    frontend_path = os.path.join("/app", "frontend")
    if not os.path.exists(frontend_path):
        # Fallback para desenvolvimento local
        frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    
    index_path = os.path.join(frontend_path, "index.html")
    
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        # Fallback para JSON se frontend não estiver disponível
        return {
            "message": f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}",
            "status": "active",
            "description": "Sistema de automação inteligente de conteúdo",
            "endpoints": {
                "health": "/health",
                "gmail_auth": "/auth/gmail/redirect",
                "gmail_status": "/gmail/status",
                "docs": "/docs"
            }
        }

@app.get("/api")
async def api_info():
    """Informações da API"""
    return {
        "message": f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}",
        "status": "active",
        "description": "Sistema de automação inteligente de conteúdo",
        "endpoints": {
            "health": "/health",
            "gmail_auth": "/auth/gmail/redirect",
            "gmail_status": "/gmail/status",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check com verificação de todos os serviços"""
    checks = {}
    
    # Testar Supabase (consolidar em uma única consulta)
    try:
        # Usar uma consulta simples que testa conexão e RLS
        test_result = db.client.table("system_config").select("key").limit(1).execute()
        checks["database"] = True
    except Exception as e:
        logger.error(f"Erro no health check Supabase: {e}")
        checks["database"] = False
    
    # Testar WordPress
    try:
        checks["wordpress"] = wp_publisher.test_connection()
    except Exception as e:
        logger.error(f"Erro no health check WordPress: {e}")
        checks["wordpress"] = False
    
    # Testar Gemini (gerar embedding simples)
    try:
        test_embedding = ai_processor.generate_embedding("teste")
        checks["gemini"] = len(test_embedding) > 0
    except Exception as e:
        logger.error(f"Erro no health check Gemini: {e}")
        checks["gemini"] = False
    
    # Testar Gmail (verificar autenticação sem recarregar credenciais)
    try:
        checks["gmail"] = gmail_client.credentials is not None and gmail_client.credentials.valid
    except Exception as e:
        logger.error(f"Erro no health check Gmail: {e}")
        checks["gmail"] = False
    
    # Testar Google Data Connector
    try:
        gd_status = google_connector.test_connection()
        checks["google_data"] = gd_status.get("credentials_valid", False)
    except Exception as e:
        logger.error(f"Erro no health check Google Data: {e}")
        checks["google_data"] = False
    
    # Testar Auth Manager
    try:
        auth_stats = auth_manager.get_auth_stats()
        checks["auth"] = auth_stats.get("total_users", 0) > 0
    except Exception as e:
        logger.error(f"Erro no health check Auth: {e}")
        checks["auth"] = False
    
    all_healthy = all(checks.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/auth/gmail")
async def gmail_auth():
    """Inicia processo de autenticação Gmail"""
    try:
        auth_url = gmail_client.get_authorization_url()
        if auth_url:
            return {"authorization_url": auth_url}
        else:
            raise HTTPException(status_code=500, detail="Erro ao gerar URL de autorização")
    except Exception as e:
        logger.error(f"Erro na autenticação Gmail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/gmail/redirect")
async def gmail_auth_redirect():
    """Redireciona automaticamente para autenticação Gmail"""
    try:
        auth_url = gmail_client.get_authorization_url()
        if auth_url:
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=auth_url)
        else:
            raise HTTPException(status_code=500, detail="Erro ao gerar URL de autorização")
    except Exception as e:
        logger.error(f"Erro na autenticação Gmail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/callback")
async def gmail_callback(code: str):
    """Callback OAuth Gmail"""
    try:
        success = gmail_client.handle_oauth_callback(code)
        if success:
            from fastapi.responses import HTMLResponse
            html_content = """
            <html>
                <head>
                    <title>RecifeMais - Autenticação Gmail</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f2f5; }
                        .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                        .success { color: #28a745; font-size: 24px; margin-bottom: 20px; }
                        .info { color: #6c757d; margin-bottom: 20px; }
                        .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🎉 Autenticação Gmail Concluída!</h1>
                        <div class="success">✅ Sucesso!</div>
                        <div class="info">O RecifeMais agora pode acessar seus emails de assessoria.</div>
                        <div class="info">Você pode fechar esta janela e retornar ao sistema.</div>
                        <a href="/gmail/status" class="btn">Verificar Status</a>
                    </div>
                </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        else:
            raise HTTPException(status_code=400, detail="Erro no processo de autenticação")
    except Exception as e:
        logger.error(f"Erro no callback Gmail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gmail/status")
async def gmail_status():
    """Verifica status da autenticação Gmail"""
    try:
        is_authenticated = gmail_client.authenticate()
        return {
            "authenticated": is_authenticated,
            "message": "Gmail conectado" if is_authenticated else "Gmail não autenticado"
        }
    except Exception as e:
        logger.error(f"Erro ao verificar status Gmail: {e}")
        return {"authenticated": False, "message": f"Erro: {str(e)}"}

@app.post("/gmail/fetch-emails")
async def fetch_emails_from_gmail():
    """Busca emails de assessorias do Gmail"""
    try:
        if not gmail_client.authenticate():
            raise HTTPException(status_code=401, detail="Gmail não autenticado")
        
        emails = gmail_client.get_emails_from_assessorias(days_back=7)
        
        processed_count = 0
        for email in emails:
            # Processar cada email automaticamente
            email_data = EmailInput(
                sender=email['sender'],
                subject=email['subject'],
                content=email['body'],
                received_at=email['received_at']
            )
            
            # Usar a mesma lógica do process_email
            email_content = f"{email_data.sender}{email_data.subject}{email_data.content}"
            email_hash = hashlib.md5(email_content.encode()).hexdigest()
            
            # Verificar se já foi processado
            existing_email = db.get_email_by_hash(email_hash)
            if not existing_email:
                # Inserir no cache
                email_cache_data = {
                    "email_hash": email_hash,
                    "sender": email_data.sender,
                    "subject": email_data.subject,
                    "content_text": email_data.content,
                    "received_at": email_data.received_at or datetime.now(),
                    "status": "pending"
                }
                
                cached_email = db.insert_email_cache(email_cache_data)
                if cached_email:
                    processed_count += 1
                    # Marcar como processado no Gmail
                    gmail_client.mark_as_processed(email['id'])
        
        return {
            "total_found": len(emails),
            "new_processed": processed_count,
            "message": f"Processados {processed_count} novos emails de {len(emails)} encontrados"
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar emails do Gmail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-email", response_model=ProcessEmailResponse)
async def process_email(email_data: EmailInput, background_tasks: BackgroundTasks):
    """Processa um email de assessoria"""
    try:
        # Gerar hash do email para evitar duplicatas
        email_content = f"{email_data.sender}{email_data.subject}{email_data.content}"
        email_hash = hashlib.md5(email_content.encode()).hexdigest()
        
        # Verificar se já foi processado
        existing_email = db.get_email_by_hash(email_hash)
        if existing_email:
            return ProcessEmailResponse(
                success=True,
                message="Email já foi processado anteriormente",
                email_id=existing_email["id"],
                wordpress_post_id=existing_email.get("wordpress_post_id")
            )
        
        # Inserir email no cache
        email_cache_data = {
            "email_hash": email_hash,
            "sender": email_data.sender,
            "subject": email_data.subject,
            "content_text": email_data.content,
            "received_at": email_data.received_at or datetime.now(),
            "status": "processing"
        }
        
        cached_email = db.insert_email_cache(email_cache_data)
        if not cached_email:
            raise HTTPException(status_code=500, detail="Erro ao salvar email")
        
        # Processar com IA em background
        background_tasks.add_task(process_email_with_ai, cached_email["id"], email_data.content, email_hash)
        
        return ProcessEmailResponse(
            success=True,
            message="Email enviado para processamento",
            email_id=cached_email["id"]
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def process_email_with_ai(email_id: str, email_content: str, email_hash: str):
    """Processa email com IA (função background)"""
    try:
        # Processar com IA
        ai_result = ai_processor.process_email_content(email_content, email_hash)
        
        if not ai_result:
            db.update_email_cache(email_id, {
                "status": "error",
                "processed_at": datetime.now()
            })
            return
        
        # Atualizar cache com resultado da IA
        update_data = {
            "status": "processed",
            "processed_at": datetime.now(),
            "gemini_prompt": ai_result["prompt_used"],
            "gemini_response": ai_result["parsed_response"],
            "tokens_used_input": ai_result["tokens_input"],
            "tokens_used_output": ai_result["tokens_output"],
            "processing_cost_usd": ai_result["estimated_cost"],
            "detected_category": ai_result["parsed_response"].get("categoria")
        }
        
        # Criar rascunho no WordPress se o conteúdo for relevante
        relevance_score = ai_result["parsed_response"].get("relevancia_score", 0)
        if relevance_score >= 7.0:  # Threshold de relevância
            wp_result = wp_publisher.create_draft_post(ai_result["parsed_response"])
            if wp_result:
                update_data["wordpress_post_id"] = wp_result["id"]
                update_data["wordpress_status"] = "draft"
                logger.info(f"Rascunho criado no WordPress: {wp_result['edit_url']}")
        
        db.update_email_cache(email_id, update_data)
        
    except Exception as e:
        logger.error(f"Erro no processamento background: {e}")
        db.update_email_cache(email_id, {
            "status": "error",
            "processed_at": datetime.now()
        })

@app.get("/emails")
async def get_emails(status: Optional[str] = None, limit: int = 20):
    """Lista emails processados"""
    try:
        if status == "pending":
            emails = db.get_pending_emails(limit)
        else:
            emails = db.get_all_emails(limit)
        
        return {
            "emails": emails,
            "total": len(emails)
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emails/{email_id}")
async def get_email_details(email_id: str):
    """Busca detalhes de um email específico"""
    try:
        email = db.get_email_by_hash(email_id)  # Temporário, implementar busca por ID
        
        if not email:
            raise HTTPException(status_code=404, detail="Email não encontrado")
        
        return email
        
    except Exception as e:
        logger.error(f"Erro ao buscar email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/suggest-topics")
async def suggest_proactive_topics(seed_topics: Optional[List[str]] = None):
    """Sugere pautas proativas"""
    try:
        topics = ai_processor.suggest_proactive_topics(seed_topics)
        
        return {
            "success": True,
            "topics": topics,
            "total": len(topics)
        }
        
    except Exception as e:
        logger.error(f"Erro ao sugerir pautas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/wordpress/publish/{post_id}")
async def publish_wordpress_post(post_id: int):
    """Publica um post no WordPress"""
    try:
        success = wp_publisher.publish_post(post_id)
        
        if success:
            return {"success": True, "message": f"Post {post_id} publicado com sucesso"}
        else:
            raise HTTPException(status_code=400, detail="Erro ao publicar post")
            
    except Exception as e:
        logger.error(f"Erro ao publicar post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/wordpress/posts")
async def get_wordpress_posts(limit: int = 10):
    """Lista posts recentes do WordPress"""
    try:
        posts = wp_publisher.get_recent_posts(limit)
        
        return {
            "posts": posts,
            "total": len(posts)
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_system_stats():
    """Estatísticas do sistema"""
    try:
        # Implementar contadores básicos
        stats = {
            "emails_processed_today": 0,  # Implementar query
            "wordpress_posts_created": 0,  # Implementar query
            "total_cost_today": 0.0,  # Implementar query
            "avg_relevance_score": 0.0  # Implementar query
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para teste manual
@app.post("/test-email")
async def test_email_processing():
    """Endpoint para teste com email fictício"""
    test_email = EmailInput(
        sender="assessoria@exemplo.com",
        subject="Novo evento cultural em Recife",
        content="""
        Prezados jornalistas,
        
        Gostaríamos de divulgar o novo evento cultural "Recife Arte Viva" que acontecerá no próximo fim de semana no Bairro do Recife Antigo.
        
        O evento contará com apresentações de artistas locais, oficinas de arte e exposições.
        
        Data: 15 e 16 de dezembro
        Local: Marco Zero
        Horário: 14h às 22h
        
        Para mais informações, entre em contato.
        
        Atenciosamente,
        Assessoria Cultural
        """
    )
    
    background_tasks = BackgroundTasks()
    return await process_email(test_email, background_tasks)

@app.get("/admin/secure-config")
async def list_secure_configs(current_user: Dict = Depends(auth_manager.require_admin())):
    """Lista configurações seguras (apenas chaves, não valores)"""
    try:
        from .secure_config import secure_config
        keys = secure_config.get_all_keys()
        
        # Verificar quais estão definidas
        configs = []
        for key in keys:
            value = secure_config.get(key)
            configs.append({
                "key": key,
                "defined": value is not None,
                "masked_value": "****" if value else None
            })
        
        return {"configs": configs}
    except Exception as e:
        logger.error(f"Erro ao listar configurações: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/secure-config/{key}")
async def set_secure_config_endpoint(
    key: str, 
    value: str, 
    description: str = "",
    current_user: Dict = Depends(auth_manager.require_admin())
):
    """Define configuração segura"""
    try:
        from .secure_config import secure_config
        
        # Validar chave permitida
        allowed_keys = secure_config.get_all_keys()
        if key not in allowed_keys:
            raise HTTPException(status_code=400, detail=f"Chave não permitida. Chaves válidas: {allowed_keys}")
        
        result = secure_config.set(key, value, description)
        
        if result:
            return {"message": f"Configuração '{key}' definida com sucesso"}
        else:
            raise HTTPException(status_code=500, detail="Erro ao salvar configuração")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao definir configuração: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/migrate-credentials")
async def migrate_credentials_endpoint():
    """Migra credenciais do .env para o banco de dados"""
    try:
        from .secure_config import secure_config
        
        # Credenciais para migrar
        credentials_map = {
            "wordpress_username": settings.WORDPRESS_USERNAME,
            "wordpress_password": settings.WORDPRESS_PASSWORD,
            "gmail_client_id": settings.GMAIL_CLIENT_ID,
            "gmail_client_secret": settings.GMAIL_CLIENT_SECRET,
            "google_ai_api_key": settings.GOOGLE_AI_API_KEY,
            "supabase_service_key": settings.SUPABASE_SERVICE_KEY
        }
        
        success_count = 0
        results = []
        
        for key, value in credentials_map.items():
            if value:
                result = secure_config.set(key, value, f"Migrado automaticamente de .env")
                if result:
                    success_count += 1
                    results.append({"key": key, "status": "success"})
                else:
                    results.append({"key": key, "status": "error"})
            else:
                results.append({"key": key, "status": "empty"})
        
        return {
            "message": f"Migração concluída: {success_count}/{len(credentials_map)} credenciais",
            "results": results,
            "success_count": success_count,
            "total_count": len(credentials_map)
        }
        
    except Exception as e:
        logger.error(f"Erro na migração de credenciais: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/populate-knowledge-base")
async def populate_knowledge_base():
    """Popula a knowledge base com posts existentes do WordPress"""
    try:
        # Buscar posts recentes do WordPress
        posts = wp_publisher.get_recent_posts(limit=50)
        
        if not posts:
            return {"message": "Nenhum post encontrado no WordPress", "count": 0}
        
        populated_count = 0
        
        for post in posts:
            try:
                # Extrair conteúdo limpo
                content = wp_publisher.extract_clean_content(post.get('content', ''))
                
                if len(content) < 100:  # Ignorar posts muito pequenos
                    continue
                
                # Gerar embedding
                embedding = ai_processor.generate_embedding(content)
                
                if not embedding:
                    continue
                
                # Preparar dados para inserção
                kb_data = {
                    'content_text': content,
                    'embedding': embedding,
                    'source_url': post.get('link', ''),
                    'source_type': 'post',
                    'topic': post.get('title', '')[:100],
                    'category_recifemais': 'wordpress_existing',
                    'metadata': {
                        'wordpress_id': post.get('id'),
                        'title': post.get('title', ''),
                        'date': post.get('date', ''),
                        'categories': post.get('categories', [])
                    }
                }
                
                # Inserir na knowledge base
                result = db.client.table("knowledge_base").insert(kb_data).execute()
                
                if result.data:
                    populated_count += 1
                    
            except Exception as e:
                logger.error(f"Erro ao processar post {post.get('id')}: {e}")
                continue
        
        return {
            "message": f"Knowledge base populada com sucesso",
            "posts_processed": len(posts),
            "posts_added": populated_count
        }
        
    except Exception as e:
        logger.error(f"Erro ao popular knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Inicializar Realtime na startup
@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação"""
    try:
        # Conectar ao Realtime
        await realtime_manager.connect()
        
        # Registrar callback para logs
        def log_notification(event_type: str, notification: dict):
            logger.info(f"📡 Notificação Realtime: {event_type} - {notification.get('data', {}).get('subject', 'N/A')}")
        
        realtime_manager.subscribe("main_app", log_notification)
        
        logger.info("🚀 Aplicação iniciada com Realtime ativo")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpeza na finalização"""
    try:
        await realtime_manager.disconnect()
        logger.info("🔌 Aplicação finalizada")
    except Exception as e:
        logger.error(f"❌ Erro na finalização: {e}")

@app.get("/admin/stats/realtime")
async def get_realtime_stats():
    """Estatísticas do sistema em tempo real"""
    try:
        stats = await realtime_manager.get_system_stats()
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas realtime: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/wordpress/analyze-external-links")
async def analyze_external_links():
    """Analisa posts com links externos para insights"""
    try:
        posts_with_links = wp_publisher.get_posts_with_external_links(limit=30)
        
        analysis = {
            "total_posts_analyzed": len(posts_with_links),
            "posts_with_external_links": 0,
            "most_referenced_domains": {},
            "link_analysis": []
        }
        
        domain_count = {}
        
        for post in posts_with_links:
            external_links = post.get('external_links', [])
            if external_links:
                analysis["posts_with_external_links"] += 1
                
                post_analysis = {
                    "post_id": post.get('id'),
                    "title": post.get('title', {}).get('rendered', ''),
                    "link_count": len(external_links),
                    "domains": []
                }
                
                for link in external_links:
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(link['url']).netloc
                        domain_count[domain] = domain_count.get(domain, 0) + 1
                        post_analysis["domains"].append(domain)
                    except:
                        continue
                
                analysis["link_analysis"].append(post_analysis)
        
        # Top 10 domínios mais referenciados
        analysis["most_referenced_domains"] = dict(
            sorted(domain_count.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Erro na análise de links externos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/wordpress/category-analysis/{category_slug}")
async def analyze_category_content(category_slug: str):
    """Analisa conteúdo de uma categoria específica"""
    try:
        posts = wp_publisher.get_posts_by_category(category_slug, limit=20)
        
        if not posts:
            return {"message": f"Nenhum post encontrado na categoria '{category_slug}'"}
        
        # Processar posts para análise
        analysis = {
            "category": category_slug,
            "total_posts": len(posts),
            "posts_analyzed": [],
            "avg_word_count": 0,
            "common_keywords": {},
            "publishing_frequency": {}
        }
        
        total_words = 0
        all_keywords = {}
        
        for post in posts:
            # Extrair conteúdo limpo
            content = wp_publisher.extract_clean_content(
                post.get('content', {}).get('rendered', '')
            )
            
            word_count = len(content.split())
            total_words += word_count
            
            # Extrair data de publicação
            pub_date = post.get('date', '')[:10]  # YYYY-MM-DD
            analysis["publishing_frequency"][pub_date] = analysis["publishing_frequency"].get(pub_date, 0) + 1
            
            # Gerar embedding para análise futura
            try:
                embedding = ai_processor.generate_embedding(content)
                
                post_analysis = {
                    "id": post.get('id'),
                    "title": post.get('title', {}).get('rendered', ''),
                    "word_count": word_count,
                    "publish_date": pub_date,
                    "has_embedding": len(embedding) > 0 if embedding else False
                }
                
                analysis["posts_analyzed"].append(post_analysis)
                
            except Exception as e:
                logger.error(f"Erro ao processar post {post.get('id')}: {e}")
                continue
        
        # Calcular média de palavras
        analysis["avg_word_count"] = total_words // len(posts) if posts else 0
        
        return analysis
        
    except Exception as e:
        logger.error(f"Erro na análise de categoria: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/edge-functions/process-email")
async def process_email_via_edge(email_data: dict):
    """Processa email usando Edge Function para escalabilidade"""
    try:
        # URL da Edge Function
        edge_url = f"{settings.SUPABASE_URL}/functions/v1/email-processor"
        
        headers = {
            "Authorization": f"Bearer {get_service_key()}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                edge_url,
                json=email_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Enviar notificação realtime
                await realtime_manager.send_custom_notification(
                    "edge_processing_complete",
                    {
                        "email_id": email_data.get("email_id"),
                        "processing_result": result
                    }
                )
                
                return result
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Erro na Edge Function: {response.text}"
                )
                
    except Exception as e:
        logger.error(f"Erro ao processar via Edge Function: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/edge-functions/analyze-sentiment")
async def analyze_sentiment_via_edge(text_data: dict):
    """Analisa sentimento usando Edge Function"""
    try:
        edge_url = f"{settings.SUPABASE_URL}/functions/v1/sentiment-analyzer"
        
        headers = {
            "Authorization": f"Bearer {get_service_key()}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                edge_url,
                json=text_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Erro na análise de sentimento: {response.text}"
                )
                
    except Exception as e:
        logger.error(f"Erro na análise de sentimento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/database-functions/processing-stats")
async def get_processing_stats_from_db(days_back: int = 7):
    """Usa função do banco para estatísticas de processamento"""
    try:
        result = db.client.rpc('get_processing_stats', {'days_back': days_back}).execute()
        
        if result.data:
            stats = result.data[0]
            
            # Adicionar timestamp
            stats['generated_at'] = datetime.now().isoformat()
            
            return stats
        else:
            return {"message": "Nenhuma estatística encontrada"}
            
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do banco: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/database-functions/calculate-relevance")
async def calculate_content_relevance(content_data: dict):
    """Usa função do banco para calcular relevância do conteúdo"""
    try:
        content_text = content_data.get('content_text', '')
        keywords = content_data.get('keywords', [])
        
        if not content_text or not keywords:
            raise HTTPException(status_code=400, detail="content_text e keywords são obrigatórios")
        
        result = db.client.rpc('calculate_content_relevance', {
            'content_text': content_text,
            'target_keywords': keywords
        }).execute()
        
        if result.data:
            relevance_score = result.data[0] if isinstance(result.data, list) else result.data
            
            return {
                "content_length": len(content_text),
                "keywords_count": len(keywords),
                "relevance_score": relevance_score,
                "analysis_timestamp": datetime.now().isoformat()
            }
        else:
            return {"relevance_score": 0.0}
            
    except Exception as e:
        logger.error(f"Erro ao calcular relevância: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# GOOGLE DATA CONNECTOR ENDPOINTS
# ==========================================

@app.get("/auth/google")
async def google_data_auth():
    """Inicia autenticação com Google Data (GSC + GA4)"""
    try:
        auth_url = google_connector.get_authorization_url()
        if auth_url:
            return {"auth_url": auth_url}
        else:
            raise HTTPException(status_code=500, detail="Não foi possível gerar URL de autorização")
    except Exception as e:
        logger.error(f"Erro na autenticação Google Data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/google/callback")
async def google_data_callback(code: str):
    """Callback da autenticação Google Data"""
    try:
        success = google_connector.authenticate_google(code)
        if success:
            return {"message": "Autenticação Google Data concluída com sucesso"}
        else:
            raise HTTPException(status_code=400, detail="Falha na autenticação Google Data")
    except Exception as e:
        logger.error(f"Erro no callback Google Data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/google-data/status")
async def google_data_status():
    """Status da conexão com Google Data"""
    try:
        status = google_connector.test_connection()
        return status
    except Exception as e:
        logger.error(f"Erro ao verificar status Google Data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/google-data/gsc/performance")
async def get_gsc_performance(
    days_back: int = 30,
    dimensions: str = "query",
    limit: int = 100
):
    """Busca dados de performance do Google Search Console"""
    try:
        from datetime import date, timedelta
        
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=days_back)
        
        # Converter string de dimensões para lista
        dimensions_list = [d.strip() for d in dimensions.split(",")]
        
        performance_data = google_connector.get_gsc_performance(
            site_url=settings.secure_gsc_site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions_list,
            row_limit=limit
        )
        
        return performance_data
        
    except Exception as e:
        logger.error(f"Erro ao buscar performance GSC: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/google-data/ga4/report")
async def get_ga4_report(
    days_back: int = 30,
    metrics: str = "sessions,users,pageviews",
    dimensions: str = "pagePath",
    limit: int = 100
):
    """Busca relatório do Google Analytics 4"""
    try:
        property_id = settings.secure_ga4_property_id
        if not property_id:
            raise HTTPException(status_code=400, detail="GA4_PROPERTY_ID não configurado")
        
        # Converter strings para listas
        metrics_list = [m.strip() for m in metrics.split(",")]
        dimensions_list = [d.strip() for d in dimensions.split(",")]
        
        report_data = google_connector.get_ga4_report(
            property_id=property_id,
            start_date=f"{days_back}daysAgo",
            end_date="yesterday",
            metrics=metrics_list,
            dimensions=dimensions_list,
            limit=limit
        )
        
        return report_data
        
    except Exception as e:
        logger.error(f"Erro ao buscar relatório GA4: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/google-data/insights/content")
async def get_content_insights(days_back: int = 30):
    """Combina dados GSC + GA4 para insights de conteúdo"""
    try:
        property_id = settings.secure_ga4_property_id
        if not property_id:
            raise HTTPException(status_code=400, detail="GA4_PROPERTY_ID não configurado")
        
        insights = google_connector.get_content_insights(
            site_url=settings.secure_gsc_site_url,
            property_id=property_id,
            days_back=days_back
        )
        
        return insights
        
    except Exception as e:
        logger.error(f"Erro ao gerar insights de conteúdo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/google-data/configure")
async def configure_google_data(
    config_data: dict,
    current_user: Dict = Depends(auth_manager.require_permission("analytics"))
):
    """Configura parâmetros do Google Data (GA4 Property ID, etc.)"""
    try:
        updated_configs = []
        
        # Configurar GA4 Property ID
        if "ga4_property_id" in config_data:
            success = db.set_secure_config(
                "ga4_property_id",
                config_data["ga4_property_id"],
                "Google Analytics 4 Property ID"
            )
            if success:
                updated_configs.append("ga4_property_id")
        
        # Configurar GSC Site URL
        if "gsc_site_url" in config_data:
            success = db.set_secure_config(
                "gsc_site_url",
                config_data["gsc_site_url"],
                "Google Search Console Site URL"
            )
            if success:
                updated_configs.append("gsc_site_url")
        
        return {
            "message": "Configurações Google Data atualizadas",
            "updated_configs": updated_configs
        }
        
    except Exception as e:
        logger.error(f"Erro ao configurar Google Data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/google-data/dashboard")
async def get_google_data_dashboard(days_back: int = 30):
    """Dashboard completo com dados GSC + GA4"""
    try:
        property_id = settings.secure_ga4_property_id
        if not property_id:
            return {"error": "GA4_PROPERTY_ID não configurado"}
        
        from datetime import date, timedelta
        
        # Status da conexão
        connection_status = google_connector.test_connection()
        
        dashboard_data = {
            "connection_status": connection_status,
            "period": f"Last {days_back} days",
            "gsc_data": {},
            "ga4_data": {},
            "combined_insights": {}
        }
        
        if connection_status.get("gsc_connected"):
            # Dados GSC - Top Queries
            end_date = date.today() - timedelta(days=1)
            start_date = end_date - timedelta(days=days_back)
            
            gsc_queries = google_connector.get_gsc_performance(
                site_url=settings.secure_gsc_site_url,
                start_date=start_date,
                end_date=end_date,
                dimensions=['query'],
                row_limit=20
            )
            
            gsc_pages = google_connector.get_gsc_performance(
                site_url=settings.secure_gsc_site_url,
                start_date=start_date,
                end_date=end_date,
                dimensions=['page'],
                row_limit=20
            )
            
            dashboard_data["gsc_data"] = {
                "top_queries": gsc_queries.get("data", [])[:10],
                "top_pages": gsc_pages.get("data", [])[:10],
                "summary": gsc_queries.get("summary", {})
            }
        
        if connection_status.get("ga4_connected"):
            # Dados GA4 - Overview
            ga4_overview = google_connector.get_ga4_report(
                property_id=property_id,
                start_date=f"{days_back}daysAgo",
                end_date="yesterday",
                metrics=['sessions', 'users', 'pageviews', 'bounceRate'],
                dimensions=['pagePath'],
                limit=20
            )
            
            dashboard_data["ga4_data"] = {
                "overview": ga4_overview.get("totals", {}),
                "top_pages": ga4_overview.get("data", [])[:10]
            }
        
        # Insights combinados
        if connection_status.get("gsc_connected") and connection_status.get("ga4_connected"):
            combined_insights = google_connector.get_content_insights(
                site_url=settings.secure_gsc_site_url,
                property_id=property_id,
                days_back=days_back
            )
            
            dashboard_data["combined_insights"] = combined_insights.get("insights", [])[:10]
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard Google Data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================

@app.post("/auth/login")
async def login(login_data: LoginRequest):
    """Autentica usuário e retorna token JWT"""
    try:
        result = auth_manager.authenticate_user(
            email=login_data.email,
            password=login_data.password
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=401,
                detail=result.get("message", "Credenciais inválidas")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(status_code=500, detail="Erro interno de autenticação")

@app.post("/auth/refresh")
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Renova token de acesso"""
    try:
        result = auth_manager.refresh_token(refresh_data.refresh_token)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=401, detail="Token de refresh inválido")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao renovar token: {e}")
        raise HTTPException(status_code=500, detail="Erro ao renovar token")

@app.post("/auth/logout")
async def logout(current_user: Dict = Depends(auth_manager.get_current_user)):
    """Faz logout do usuário atual"""
    try:
        # O token está nas credenciais, mas para simplificar vamos apenas retornar sucesso
        # O frontend deve descartar o token localmente
        logger.info(f"🔒 Logout: {current_user.get('email')}")
        
        return {
            "success": True,
            "message": "Logout realizado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro no logout: {e}")
        raise HTTPException(status_code=500, detail="Erro no logout")

@app.get("/auth/me")
async def get_current_user_info(current_user: Dict = Depends(auth_manager.get_current_user)):
    """Retorna informações do usuário autenticado"""
    return {
        "user": current_user,
        "authenticated": True,
        "timestamp": datetime.now().isoformat()
    }

# ==========================================
# USER MANAGEMENT ENDPOINTS (ADMIN ONLY)
# ==========================================

@app.get("/admin/users")
async def list_users(current_user: Dict = Depends(auth_manager.require_admin())):
    """Lista todos os usuários do sistema (Admin apenas)"""
    try:
        users = auth_manager.list_users()
        return {
            "users": users,
            "total": len(users)
        }
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar usuários")

@app.post("/admin/users")
async def create_user(
    user_data: CreateUserRequest,
    current_user: Dict = Depends(auth_manager.require_admin())
):
    """Cria novo usuário (Admin apenas)"""
    try:
        result = auth_manager.create_user(
            email=user_data.email,
            password=user_data.password,
            role=user_data.role,
            metadata=user_data.metadata
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Erro ao criar usuário"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar usuário")

@app.put("/admin/users/role")
async def update_user_role(
    update_data: UpdateUserRoleRequest,
    current_user: Dict = Depends(auth_manager.require_admin())
):
    """Atualiza role de um usuário (Admin apenas)"""
    try:
        result = auth_manager.update_user_role(
            user_id=update_data.user_id,
            new_role=update_data.new_role
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Erro ao atualizar role"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar role: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar role")

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Dict = Depends(auth_manager.require_admin())
):
    """Remove um usuário (Admin apenas)"""
    try:
        # Não permitir que admin delete a si mesmo
        if user_id == current_user.get("user_id"):
            raise HTTPException(status_code=400, detail="Não é possível deletar seu próprio usuário")
        
        result = auth_manager.delete_user(user_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Erro ao remover usuário"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro ao remover usuário")

@app.get("/admin/auth/stats")
async def get_auth_stats(current_user: Dict = Depends(auth_manager.require_admin())):
    """Estatísticas do sistema de autenticação (Admin apenas)"""
    try:
        stats = auth_manager.get_auth_stats()
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de auth: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter estatísticas")

@app.post("/admin/setup/initial-admin")
async def create_initial_admin(user_data: CreateUserRequest):
    """
    Cria admin inicial do sistema
    Endpoint público usado apenas na configuração inicial
    """
    try:
        result = auth_manager.create_initial_admin(
            email=user_data.email,
            password=user_data.password
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Erro ao criar admin"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar admin inicial: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar admin inicial")

# ==========================================
# EMAIL WORKFLOW ENDPOINTS
# ==========================================

@app.get("/workflow/dashboard")
async def get_workflow_dashboard(
    days_back: int = 30,
    current_user: Dict = Depends(auth_manager.require_permission("content"))
):
    """Obter estatísticas do dashboard de workflow"""
    try:
        user_id = current_user.get("id") if current_user.get("role") != "admin" else None
        stats = email_workflow.get_dashboard_stats(user_id=user_id, days_back=days_back)
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Erro ao obter dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflow/emails")
async def list_workflow_emails(
    stage: Optional[str] = None,
    priority: Optional[int] = None,
    assigned_to: Optional[str] = None,
    is_auto_process: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict = Depends(auth_manager.require_permission("content"))
):
    """Listar emails do workflow com filtros"""
    try:
        # Se não for admin, mostrar apenas emails atribuídos ao usuário
        if current_user.get("role") != "admin" and not assigned_to:
            assigned_to = current_user.get("id")
        
        result = email_workflow.list_emails(
            stage=stage,
            priority=priority,
            assigned_to=assigned_to,
            is_auto_process=is_auto_process,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Erro ao listar emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflow/emails/{email_id}")
async def get_workflow_email_details(
    email_id: str,
    current_user: Dict = Depends(auth_manager.require_permission("content"))
):
    """Obter detalhes completos de um email do workflow"""
    try:
        email = email_workflow.get_email_details(email_id)
        
        if not email:
            raise HTTPException(status_code=404, detail="Email não encontrado")
        
        # Verificar permissões
        if current_user.get("role") != "admin" and email.get("assigned_to") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Acesso negado a este email")
        
        return {
            "success": True,
            "email": email
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter detalhes do email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflow/emails/{email_id}/analyze")
async def analyze_workflow_email(
    email_id: str,
    current_user: Dict = Depends(auth_manager.require_permission("content"))
):
    """Analisar email com IA (primeira etapa do workflow)"""
    try:
        result = email_workflow.analyze_email(email_id, current_user["id"])
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao analisar email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflow/emails/{email_id}/approve")
async def approve_workflow_content(
    email_id: str,
    approval_data: ApproveContentRequest,
    current_user: Dict = Depends(auth_manager.require_permission("content"))
):
    """Aprovar conteúdo gerado (segunda etapa)"""
    try:
        user_feedback = {
            "rating": approval_data.rating,
            "notes": approval_data.notes,
            "modifications": approval_data.modifications,
            "approved_at": datetime.now().isoformat(),
            "approved_by": current_user["email"]
        }
        
        result = email_workflow.approve_content(email_id, current_user["id"], user_feedback)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao aprovar conteúdo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflow/emails/{email_id}/prepare")
async def prepare_workflow_publish(
    email_id: str,
    publish_data: PreparePublishRequest,
    current_user: Dict = Depends(auth_manager.require_permission("content"))
):
    """Preparar email para publicação (terceira etapa)"""
    try:
        publish_dict = {
            "titulo": publish_data.titulo,
            "conteudo": publish_data.conteudo,
            "categoria": publish_data.categoria,
            "tags": publish_data.tags,
            "meta_descricao": publish_data.meta_descricao
        }
        
        result = email_workflow.prepare_for_publish(email_id, current_user["id"], publish_dict)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao preparar publicação: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflow/emails/{email_id}/publish")
async def publish_workflow_email(
    email_id: str,
    current_user: Dict = Depends(auth_manager.require_permission("wordpress"))
):
    """Publicar email no WordPress (etapa final)"""
    try:
        result = email_workflow.publish_to_wordpress(email_id, current_user["id"])
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao publicar email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflow/emails/{email_id}/reject")
async def reject_workflow_email(
    email_id: str,
    reject_data: RejectEmailRequest,
    current_user: Dict = Depends(auth_manager.require_permission("content"))
):
    """Rejeitar email em qualquer etapa"""
    try:
        result = email_workflow.reject_email(email_id, current_user["id"], reject_data.reason)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao rejeitar email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflow/emails/{email_id}/archive")
async def archive_workflow_email(
    email_id: str,
    current_user: Dict = Depends(auth_manager.require_admin())
):
    """Arquivar email (para emails antigos)"""
    try:
        result = email_workflow.archive_email(email_id, current_user["id"])
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao arquivar email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/workflow/emails/{email_id}/priority")
async def update_workflow_email_priority(
    email_id: str,
    priority_data: UpdatePriorityRequest,
    current_user: Dict = Depends(auth_manager.require_permission("content"))
):
    """Atualizar prioridade do email"""
    try:
        result = email_workflow.update_priority(email_id, current_user["id"], priority_data.priority)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar prioridade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/workflow/emails/{email_id}/assign")
async def assign_workflow_email(
    email_id: str,
    assign_data: AssignEmailRequest,
    current_user: Dict = Depends(auth_manager.require_admin())
):
    """Atribuir email a um usuário"""
    try:
        result = email_workflow.assign_email(email_id, assign_data.assigned_to, current_user["id"])
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atribuir email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 