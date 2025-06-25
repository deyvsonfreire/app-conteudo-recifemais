"""
Email Workflow Manager - Gerencia o fluxo de aprovação de emails
Controla as etapas: recebido → analisado → aprovado → pronto → publicado
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json

import sys
import os

# Adicionar diretório pai ao path
backend_dir = os.path.dirname(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    # Tentar import relativo primeiro (produção)
    from ..database import db
    from .ai_processor import ai_processor
    from .wordpress_publisher import wp_publisher
except ImportError:
    # Fallback para import absoluto (desenvolvimento)
    from database import db
    from modules.ai_processor import ai_processor
    from modules.wordpress_publisher import wp_publisher

logger = logging.getLogger(__name__)

class WorkflowStage(Enum):
    RECEIVED = "received"
    ANALYZED = "analyzed"
    APPROVED_CONTENT = "approved_content"
    READY_PUBLISH = "ready_publish"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class Priority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

class EmailWorkflowManager:
    """Gerenciador do workflow de aprovação de emails"""
    
    def __init__(self):
        self.db = db
        logger.info("📋 Email Workflow Manager inicializado")
    
    # ==========================================
    # DASHBOARD E LISTAGEM
    # ==========================================
    
    def get_dashboard_stats(self, user_id: Optional[str] = None, days_back: int = 30) -> Dict:
        """Obter estatísticas para o dashboard"""
        try:
            result = self.db.client.rpc('get_email_workflow_stats', {
                'p_user_id': user_id,
                'p_days_back': days_back
            }).execute()
            
            if result.data:
                return result.data[0] if result.data else {}
            
            return {}
            
        except Exception as e:
            logger.error(f"Erro ao obter stats do dashboard: {e}")
            return {}
    
    def list_emails(self, 
                   stage: Optional[str] = None,
                   priority: Optional[int] = None,
                   assigned_to: Optional[str] = None,
                   is_auto_process: Optional[bool] = None,
                   limit: int = 50,
                   offset: int = 0) -> Dict:
        """Listar emails com filtros"""
        try:
            query = self.db.client.from_("email_dashboard").select("*")
            
            if stage:
                query = query.eq("workflow_stage", stage)
            if priority:
                query = query.eq("priority", priority)
            if assigned_to:
                query = query.eq("assigned_to", assigned_to)
            if is_auto_process is not None:
                query = query.eq("is_auto_process", is_auto_process)
            
            result = query.range(offset, offset + limit - 1).execute()
            
            return {
                "emails": result.data if result.data else [],
                "total": len(result.data) if result.data else 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao listar emails: {e}")
            return {"emails": [], "total": 0}
    
    def get_email_details(self, email_id: str) -> Optional[Dict]:
        """Obter detalhes completos de um email"""
        try:
            # Buscar email
            email_result = self.db.client.from_("email_cache").select("*").eq("id", email_id).single().execute()
            
            if not email_result.data:
                return None
            
            email = email_result.data
            
            # Buscar histórico
            history_result = self.db.client.from_("email_workflow_history").select("*").eq("email_id", email_id).order("created_at", desc=True).execute()
            
            email["history"] = history_result.data if history_result.data else []
            
            return email
            
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do email: {e}")
            return None
    
    # ==========================================
    # PROCESSAMENTO E ANÁLISE
    # ==========================================
    
    def analyze_email(self, email_id: str, user_id: str) -> Dict:
        """Analisar email com IA (primeira etapa do workflow)"""
        try:
            # Buscar email
            email = self.get_email_details(email_id)
            if not email:
                return {"success": False, "error": "Email não encontrado"}
            
            if email["workflow_stage"] != WorkflowStage.RECEIVED.value:
                return {"success": False, "error": "Email já foi analisado"}
            
            # Analisar com IA
            content = f"{email['subject']}\n\n{email['content_text']}"
            
            # Análise de categoria e relevância
            analysis = ai_processor.analyze_email_content(content)
            
            # Gerar conteúdo inicial se relevante
            generated_content = None
            if analysis.get("is_relevant", False):
                generated_content = ai_processor.generate_content_from_email(content)
            
            # Preparar dados da análise
            ai_analysis = {
                "category": analysis.get("category", "geral"),
                "confidence": analysis.get("confidence", 0.5),
                "is_relevant": analysis.get("is_relevant", False),
                "topics": analysis.get("topics", []),
                "generated_content": generated_content,
                "analysis_date": datetime.now().isoformat()
            }
            
            # Atualizar email
            update_result = self.db.client.from_("email_cache").update({
                "workflow_stage": WorkflowStage.ANALYZED.value,
                "ai_analysis": ai_analysis,
                "updated_at": datetime.now().isoformat()
            }).eq("id", email_id).execute()
            
            # Registrar ação
            self._log_workflow_action(
                email_id=email_id,
                user_id=user_id,
                action="analyze",
                from_stage=WorkflowStage.RECEIVED,
                to_stage=WorkflowStage.ANALYZED,
                notes="Análise automática por IA concluída"
            )
            
            logger.info(f"📊 Email {email_id} analisado com sucesso")
            
            return {
                "success": True,
                "analysis": ai_analysis,
                "message": "Email analisado com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar email: {e}")
            return {"success": False, "error": str(e)}
    
    def approve_content(self, email_id: str, user_id: str, user_feedback: Dict) -> Dict:
        """Aprovar conteúdo gerado (segunda etapa)"""
        try:
            email = self.get_email_details(email_id)
            if not email:
                return {"success": False, "error": "Email não encontrado"}
            
            if email["workflow_stage"] != WorkflowStage.ANALYZED.value:
                return {"success": False, "error": "Email precisa estar analisado"}
            
            # Atualizar com feedback do usuário
            update_result = self.db.client.from_("email_cache").update({
                "workflow_stage": WorkflowStage.APPROVED_CONTENT.value,
                "user_feedback": user_feedback,
                "assigned_to": user_id,
                "updated_at": datetime.now().isoformat()
            }).eq("id", email_id).execute()
            
            # Registrar ação
            self._log_workflow_action(
                email_id=email_id,
                user_id=user_id,
                action="approve_content",
                from_stage=WorkflowStage.ANALYZED,
                to_stage=WorkflowStage.APPROVED_CONTENT,
                notes=user_feedback.get("notes", "Conteúdo aprovado pelo usuário"),
                metadata=user_feedback
            )
            
            logger.info(f"✅ Conteúdo do email {email_id} aprovado")
            
            return {"success": True, "message": "Conteúdo aprovado com sucesso"}
            
        except Exception as e:
            logger.error(f"Erro ao aprovar conteúdo: {e}")
            return {"success": False, "error": str(e)}
    
    def prepare_for_publish(self, email_id: str, user_id: str, publish_data: Dict) -> Dict:
        """Preparar para publicação (terceira etapa)"""
        try:
            email = self.get_email_details(email_id)
            if not email:
                return {"success": False, "error": "Email não encontrado"}
            
            if email["workflow_stage"] != WorkflowStage.APPROVED_CONTENT.value:
                return {"success": False, "error": "Conteúdo precisa estar aprovado"}
            
            # Preparar dados para publicação
            ai_analysis = email.get("ai_analysis", {})
            generated_content = ai_analysis.get("generated_content", {})
            
            # Merge com dados do usuário
            final_content = {
                **generated_content,
                **publish_data,
                "prepared_by": user_id,
                "prepared_at": datetime.now().isoformat()
            }
            
            # Atualizar email
            updated_analysis = {**ai_analysis, "final_content": final_content}
            
            update_result = self.db.client.from_("email_cache").update({
                "workflow_stage": WorkflowStage.READY_PUBLISH.value,
                "ai_analysis": updated_analysis,
                "updated_at": datetime.now().isoformat()
            }).eq("id", email_id).execute()
            
            # Registrar ação
            self._log_workflow_action(
                email_id=email_id,
                user_id=user_id,
                action="prepare_publish",
                from_stage=WorkflowStage.APPROVED_CONTENT,
                to_stage=WorkflowStage.READY_PUBLISH,
                notes="Preparado para publicação",
                metadata=publish_data
            )
            
            logger.info(f"📝 Email {email_id} preparado para publicação")
            
            return {"success": True, "message": "Email preparado para publicação"}
            
        except Exception as e:
            logger.error(f"Erro ao preparar para publicação: {e}")
            return {"success": False, "error": str(e)}
    
    def publish_to_wordpress(self, email_id: str, user_id: str) -> Dict:
        """Publicar no WordPress (etapa final)"""
        try:
            email = self.get_email_details(email_id)
            if not email:
                return {"success": False, "error": "Email não encontrado"}
            
            if email["workflow_stage"] != WorkflowStage.READY_PUBLISH.value:
                return {"success": False, "error": "Email não está pronto para publicação"}
            
            # Obter conteúdo final
            ai_analysis = email.get("ai_analysis", {})
            final_content = ai_analysis.get("final_content", {})
            
            if not final_content:
                return {"success": False, "error": "Conteúdo final não encontrado"}
            
            # Publicar no WordPress
            publish_result = wp_publisher.publish_post(
                title=final_content.get("titulo", email["subject"]),
                content=final_content.get("conteudo", ""),
                category=final_content.get("categoria"),
                tags=final_content.get("tags", []),
                meta_description=final_content.get("meta_descricao")
            )
            
            if publish_result.get("success"):
                # Atualizar email como publicado
                update_result = self.db.client.from_("email_cache").update({
                    "workflow_stage": WorkflowStage.PUBLISHED.value,
                    "wordpress_post_id": publish_result.get("post_id"),
                    "updated_at": datetime.now().isoformat()
                }).eq("id", email_id).execute()
                
                # Registrar ação
                self._log_workflow_action(
                    email_id=email_id,
                    user_id=user_id,
                    action="publish",
                    from_stage=WorkflowStage.READY_PUBLISH,
                    to_stage=WorkflowStage.PUBLISHED,
                    notes=f"Publicado no WordPress - Post ID: {publish_result.get('post_id')}",
                    metadata={"wordpress_post_id": publish_result.get("post_id")}
                )
                
                logger.info(f"🚀 Email {email_id} publicado no WordPress")
                
                return {
                    "success": True,
                    "message": "Email publicado com sucesso",
                    "wordpress_post_id": publish_result.get("post_id")
                }
            else:
                return {"success": False, "error": publish_result.get("error", "Erro na publicação")}
                
        except Exception as e:
            logger.error(f"Erro ao publicar no WordPress: {e}")
            return {"success": False, "error": str(e)}
    
    # ==========================================
    # AÇÕES DE CONTROLE
    # ==========================================
    
    def reject_email(self, email_id: str, user_id: str, reason: str) -> Dict:
        """Rejeitar email em qualquer etapa"""
        try:
            email = self.get_email_details(email_id)
            if not email:
                return {"success": False, "error": "Email não encontrado"}
            
            current_stage = email["workflow_stage"]
            
            # Atualizar como rejeitado
            update_result = self.db.client.from_("email_cache").update({
                "workflow_stage": WorkflowStage.REJECTED.value,
                "user_feedback": {"rejection_reason": reason, "rejected_at": datetime.now().isoformat()},
                "updated_at": datetime.now().isoformat()
            }).eq("id", email_id).execute()
            
            # Registrar ação
            self._log_workflow_action(
                email_id=email_id,
                user_id=user_id,
                action="reject",
                from_stage=WorkflowStage(current_stage),
                to_stage=WorkflowStage.REJECTED,
                notes=f"Rejeitado: {reason}"
            )
            
            logger.info(f"❌ Email {email_id} rejeitado")
            
            return {"success": True, "message": "Email rejeitado"}
            
        except Exception as e:
            logger.error(f"Erro ao rejeitar email: {e}")
            return {"success": False, "error": str(e)}
    
    def archive_email(self, email_id: str, user_id: str) -> Dict:
        """Arquivar email (para emails antigos)"""
        try:
            update_result = self.db.client.from_("email_cache").update({
                "workflow_stage": WorkflowStage.ARCHIVED.value,
                "is_auto_process": False,
                "updated_at": datetime.now().isoformat()
            }).eq("id", email_id).execute()
            
            # Registrar ação
            self._log_workflow_action(
                email_id=email_id,
                user_id=user_id,
                action="archive",
                from_stage=None,
                to_stage=WorkflowStage.ARCHIVED,
                notes="Email arquivado"
            )
            
            return {"success": True, "message": "Email arquivado"}
            
        except Exception as e:
            logger.error(f"Erro ao arquivar email: {e}")
            return {"success": False, "error": str(e)}
    
    def update_priority(self, email_id: str, user_id: str, priority: int) -> Dict:
        """Atualizar prioridade do email"""
        try:
            if priority not in [1, 2, 3]:
                return {"success": False, "error": "Prioridade deve ser 1, 2 ou 3"}
            
            update_result = self.db.client.from_("email_cache").update({
                "priority": priority,
                "updated_at": datetime.now().isoformat()
            }).eq("id", email_id).execute()
            
            priority_names = {1: "Alta", 2: "Média", 3: "Baixa"}
            
            # Registrar ação
            self._log_workflow_action(
                email_id=email_id,
                user_id=user_id,
                action="update_priority",
                from_stage=None,
                to_stage=None,
                notes=f"Prioridade alterada para {priority_names[priority]}"
            )
            
            return {"success": True, "message": f"Prioridade alterada para {priority_names[priority]}"}
            
        except Exception as e:
            logger.error(f"Erro ao atualizar prioridade: {e}")
            return {"success": False, "error": str(e)}
    
    def assign_email(self, email_id: str, assigned_to: str, user_id: str) -> Dict:
        """Atribuir email a um usuário"""
        try:
            update_result = self.db.client.from_("email_cache").update({
                "assigned_to": assigned_to,
                "updated_at": datetime.now().isoformat()
            }).eq("id", email_id).execute()
            
            # Registrar ação
            self._log_workflow_action(
                email_id=email_id,
                user_id=user_id,
                action="assign",
                from_stage=None,
                to_stage=None,
                notes=f"Email atribuído ao usuário {assigned_to}"
            )
            
            return {"success": True, "message": "Email atribuído com sucesso"}
            
        except Exception as e:
            logger.error(f"Erro ao atribuir email: {e}")
            return {"success": False, "error": str(e)}
    
    # ==========================================
    # HELPERS
    # ==========================================
    
    def _log_workflow_action(self, email_id: str, user_id: str, action: str, 
                           from_stage: Optional[WorkflowStage], to_stage: Optional[WorkflowStage],
                           notes: Optional[str] = None, metadata: Optional[Dict] = None):
        """Registrar ação no histórico do workflow"""
        try:
            self.db.client.rpc('log_workflow_action', {
                'p_email_id': email_id,
                'p_user_id': user_id,
                'p_action': action,
                'p_from_stage': from_stage.value if from_stage else None,
                'p_to_stage': to_stage.value if to_stage else None,
                'p_notes': notes,
                'p_metadata': metadata
            }).execute()
        except Exception as e:
            logger.error(f"Erro ao registrar ação do workflow: {e}")

# Instância global
email_workflow = EmailWorkflowManager() 