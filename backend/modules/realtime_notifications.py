"""
Módulo para notificações em tempo real usando Supabase Realtime
Versão simplificada para produção
"""

import asyncio
import json
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RealtimeNotificationManager:
    """Gerenciador de notificações em tempo real - Versão simplificada"""
    
    def __init__(self):
        self.subscribers: Dict[str, Callable] = {}
        self.is_connected = False
        self.notifications_log = []
        
    async def connect(self):
        """Conecta ao sistema de notificações (versão simplificada)"""
        try:
            # Por enquanto, usar sistema de notificações local
            # Em versões futuras, implementar Realtime quando supabase-py suportar async
            self.is_connected = True
            logger.info("✅ Sistema de notificações ativo (modo local)")
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar notificações: {e}")
            self.is_connected = False
    
    def _broadcast_notification(self, event_type: str, notification: Dict[str, Any]):
        """Envia notificação para todos os subscribers"""
        # Salvar no log local
        self.notifications_log.append({
            'event_type': event_type,
            'notification': notification,
            'timestamp': datetime.now().isoformat()
        })
        
        # Manter apenas últimas 100 notificações
        if len(self.notifications_log) > 100:
            self.notifications_log = self.notifications_log[-100:]
        
        # Enviar para subscribers
        for subscriber_id, callback in self.subscribers.items():
            try:
                callback(event_type, notification)
            except Exception as e:
                logger.error(f"Erro ao enviar notificação para {subscriber_id}: {e}")
    
    def subscribe(self, subscriber_id: str, callback: Callable):
        """Registra um subscriber para receber notificações"""
        self.subscribers[subscriber_id] = callback
        logger.info(f"📡 Subscriber registrado: {subscriber_id}")
    
    def unsubscribe(self, subscriber_id: str):
        """Remove um subscriber"""
        if subscriber_id in self.subscribers:
            del self.subscribers[subscriber_id]
            logger.info(f"📡 Subscriber removido: {subscriber_id}")
    
    async def send_custom_notification(self, notification_type: str, data: Dict[str, Any]):
        """Envia notificação customizada"""
        try:
            notification_data = {
                'type': notification_type,
                'data': data,
                'created_at': datetime.now().isoformat()
            }
            
            # Broadcast para subscribers
            self._broadcast_notification(notification_type, notification_data)
            
            logger.info(f"📢 Notificação enviada: {notification_type}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação customizada: {e}")
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        try:
            stats = {
                'realtime_connected': self.is_connected,
                'active_subscribers': len(self.subscribers),
                'total_notifications': len(self.notifications_log),
                'recent_notifications': self.notifications_log[-5:] if self.notifications_log else [],
                'timestamp': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                'realtime_connected': self.is_connected,
                'active_subscribers': len(self.subscribers),
                'error': str(e)
            }
    
    async def disconnect(self):
        """Desconecta do sistema de notificações"""
        try:
            self.is_connected = False
            self.subscribers.clear()
            
            logger.info("🔌 Sistema de notificações desconectado")
            
        except Exception as e:
            logger.error(f"Erro ao desconectar: {e}")

# Instância global
realtime_manager = RealtimeNotificationManager() 