"""
Aplicação FastAPI principal - RecifeMais Conteúdo
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import hashlib
from datetime import datetime

from .config import settings
from .database import db
from .modules.ai_processor import ai_processor
from .modules.wordpress_publisher import wp_publisher
from .modules.gmail_client import gmail_client

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

# Endpoints

@app.get("/")
async def root():
    """Endpoint raiz"""
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
    """Verificação de saúde do sistema"""
    checks = {
        "database": False,
        "wordpress": False,
        "gemini": False
    }
    
    try:
        # Testar Supabase
        db.get_system_config("health_check")
        checks["database"] = True
    except Exception as e:
        logger.error(f"Erro no health check database: {e}")
        checks["database"] = False
    
    try:
        # Testar WordPress
        checks["wordpress"] = wp_publisher.test_connection()
    except Exception as e:
        logger.error(f"Erro no health check WordPress: {e}")
        checks["wordpress"] = False
    
    try:
        # Testar Gemini (gerar embedding simples)
        test_embedding = ai_processor.generate_embedding("teste")
        checks["gemini"] = len(test_embedding) > 0
    except Exception as e:
        logger.error(f"Erro no health check Gemini: {e}")
        checks["gemini"] = False
    
    # Testar Gmail
    try:
        checks["gmail"] = gmail_client.authenticate()
    except Exception as e:
        logger.error(f"Erro no health check Gmail: {e}")
        checks["gmail"] = False
    
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
async def list_secure_configs():
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
async def set_secure_config_endpoint(key: str, value: str, description: str = ""):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 