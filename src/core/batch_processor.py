import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

from src.types.schemas import Message, MessageDirection


@dataclass
class MessageBatch:
    """
    Representa um lote de mensagens de um usuário em uma janela de tempo
    """
    user_id: str
    messages: List[Message] = field(default_factory=list)
    first_message_time: Optional[datetime] = None
    last_message_time: Optional[datetime] = None
    timer_task: Optional[asyncio.Task] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: Message) -> None:
        """Adiciona uma mensagem ao lote"""
        self.messages.append(message)
        
        if self.first_message_time is None:
            self.first_message_time = message.timestamp
        
        self.last_message_time = message.timestamp
    
    def get_combined_content(self) -> str:
        """Combina o conteúdo de todas as mensagens do lote"""
        user_messages = [
            msg.content for msg in self.messages 
            if msg.message_direction == MessageDirection.INBOUND
        ]
        return "\n".join(user_messages)
    
    def get_latest_message(self) -> Optional[Message]:
        """Retorna a mensagem mais recente do lote"""
        if not self.messages:
            return None
        return max(self.messages, key=lambda m: m.timestamp)


class BatchProcessor:
    """
    Processa mensagens em lotes com janela de tempo configurável
    """
    
    def __init__(
        self, 
        batch_window_seconds: int = 180,  # 3 minutos padrão
        min_batch_window_seconds: int = 120,  # 2 minutos mínimo
        max_batch_window_seconds: int = 300   # 5 minutos máximo
    ):
        self.batch_window_seconds = max(
            min_batch_window_seconds, 
            min(batch_window_seconds, max_batch_window_seconds)
        )
        self.batches: Dict[str, MessageBatch] = {}
        self.processing_callbacks: List[callable] = []
        self._lock = asyncio.Lock()
    
    def add_processing_callback(self, callback: callable) -> None:
        """
        Adiciona um callback que será chamado quando um lote for processado
        
        Args:
            callback: Função async que recebe (user_id: str, batch: MessageBatch)
        """
        self.processing_callbacks.append(callback)
    
    async def add_message(self, message: Message) -> bool:
        """
        Adiciona uma mensagem ao sistema de batch
        
        Args:
            message: Mensagem a ser adicionada
            
        Returns:
            bool: True se mensagem foi adicionada ao lote, False se foi processada imediatamente
        """
        # Só processa mensagens de entrada (do usuário)
        if message.message_direction != MessageDirection.INBOUND:
            return False
        
        async with self._lock:
            user_id = message.user_id
            
            # Se não existe lote para este usuário, cria um novo
            if user_id not in self.batches:
                self.batches[user_id] = MessageBatch(user_id=user_id)
            
            batch = self.batches[user_id]
            
            # Cancela timer anterior se existir
            if batch.timer_task and not batch.timer_task.done():
                batch.timer_task.cancel()
            
            # Adiciona mensagem ao lote
            batch.add_message(message)
            batch.metadata.update(message.metadata or {})
            
            # Cria novo timer para processar o lote
            batch.timer_task = asyncio.create_task(
                self._schedule_batch_processing(user_id)
            )
            
            print(f"📦 Mensagem adicionada ao lote do usuário {user_id}. "
                  f"Total no lote: {len(batch.messages)} mensagens")
            
            return True
    
    async def _schedule_batch_processing(self, user_id: str) -> None:
        """
        Agenda o processamento de um lote após a janela de tempo
        """
        try:
            await asyncio.sleep(self.batch_window_seconds)
            await self._process_batch(user_id)
        except asyncio.CancelledError:
            print(f"⏰ Timer do lote para {user_id} foi cancelado (nova mensagem recebida)")
        except Exception as e:
            print(f"❌ Erro no timer do lote para {user_id}: {e}")
    
    async def _process_batch(self, user_id: str) -> None:
        """
        Processa um lote de mensagens
        """
        async with self._lock:
            if user_id not in self.batches:
                return
            
            batch = self.batches[user_id]
            
            # Remove o lote da lista ativa
            del self.batches[user_id]
        
        print(f"🔄 Processando lote para {user_id} com {len(batch.messages)} mensagens")
        print(f"📝 Conteúdo combinado: {batch.get_combined_content()[:100]}...")
        
        # Chama todos os callbacks registrados
        for callback in self.processing_callbacks:
            try:
                await callback(user_id, batch)
            except Exception as e:
                print(f"❌ Erro no callback de processamento: {e}")
    
    async def force_process_batch(self, user_id: str) -> bool:
        """
        Força o processamento imediato de um lote
        
        Args:
            user_id: ID do usuário
            
        Returns:
            bool: True se lote foi processado, False se não existia
        """
        async with self._lock:
            if user_id not in self.batches:
                return False
            
            batch = self.batches[user_id]
            
            # Cancela o timer se existir
            if batch.timer_task and not batch.timer_task.done():
                batch.timer_task.cancel()
        
        # Processa o lote
        await self._process_batch(user_id)
        return True
    
    async def get_batch_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna informações sobre o lote ativo de um usuário
        """
        async with self._lock:
            if user_id not in self.batches:
                return None
            
            batch = self.batches[user_id]
            
            return {
                "user_id": user_id,
                "message_count": len(batch.messages),
                "first_message_time": batch.first_message_time.isoformat() if batch.first_message_time else None,
                "last_message_time": batch.last_message_time.isoformat() if batch.last_message_time else None,
                "time_remaining": self.batch_window_seconds,
                "combined_content": batch.get_combined_content()
            }
    
    async def cleanup_expired_batches(self) -> int:
        """
        Remove lotes expirados (não deve acontecer normalmente, mas é uma segurança)
        
        Returns:
            int: Número de lotes removidos
        """
        expired_users = []
        now = datetime.utcnow()
        
        async with self._lock:
            for user_id, batch in self.batches.items():
                if batch.last_message_time:
                    time_diff = now - batch.last_message_time
                    if time_diff > timedelta(seconds=self.batch_window_seconds * 2):
                        expired_users.append(user_id)
        
        # Remove lotes expirados
        for user_id in expired_users:
            await self.force_process_batch(user_id)
        
        return len(expired_users)