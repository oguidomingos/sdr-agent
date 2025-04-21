from datetime import datetime
from typing import Optional, Dict, Any, List
import asyncio

from src.types.schemas import WebhookData, Message, WhatsAppMessage
from src.config.settings import settings
from src.core.whatsapp import WhatsAppSender
from src.config.prompts import RESPONSES


class MessageHandler:
    """
    Manipula o processamento inicial das mensagens recebidas via webhook
    """
    
    def __init__(self):
        self._validate_settings()
        self.whatsapp = WhatsAppSender()

    async def send_greeting(self, user_id: str, name: str, instance: Optional[str] = None) -> None:
        """
        Envia mensagem de saudação dividida em partes
        """
        # Envia apenas as duas primeiras partes da saudação
        greeting_parts = [
            (RESPONSES['greeting_part1'].format(name=name), 5),  # curta
            (RESPONSES['greeting_part2'], 7)   # média
        ]

        for part, typing_duration in greeting_parts:
            try:
                # Envia efeito "digitando"
                await self.whatsapp.send_typing_status(
                    number=user_id,
                    duration=typing_duration,
                    instance=instance
                )

                # Envia a mensagem
                message = WhatsAppMessage(
                    number=user_id,
                    message=part.strip(),
                    metadata={"instance": instance} if instance else None
                )
                
                await self.whatsapp.send_message(
                    message=message,
                    typing_duration=0,  # já enviamos o efeito separadamente
                    cooldown=2  # 2 segundos entre partes
                )
                
                # Pequena pausa entre mensagens
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Erro ao enviar parte da saudação: {str(e)}")
                continue

    def _validate_settings(self) -> None:
        """
        Valida se todas as configurações necessárias estão presentes
        """
        required_settings = [
            'EVOLUTION_API_URL',
            'WEBHOOK_SECRET'
        ]
        
        missing_settings = [
            setting for setting in required_settings 
            if not getattr(settings, setting, None)
        ]
        
        if missing_settings:
            raise ValueError(
                f"Configurações ausentes: {', '.join(missing_settings)}"
            )

    async def extract_message_data(
        self, 
        webhook_data: WebhookData
    ) -> Optional[Message]:
        """
        Extrai dados relevantes do webhook e cria um objeto Message
        
        Args:
            webhook_data: Dados recebidos do webhook
            
        Returns:
            Message: Objeto Message processado ou None se dados inválidos
        """
        try:
            # Verifica se é uma mensagem válida
            if webhook_data.type != "Message_Upsert":
                return None
                
            data = webhook_data.data
            key = data.get("key", {})
            message_data = data.get("message", {})
            
            # Extrai o número do WhatsApp
            user_id = key.get("remoteJid", "").split("@")[0]
            if not user_id:
                return None
                
            # Extrai o conteúdo da mensagem
            content = message_data.get("conversation")
            if not content:
                # Tenta outros tipos de mensagem possíveis
                if "extendedTextMessage" in message_data:
                    content = message_data["extendedTextMessage"].get("text", "")
                else:
                    return None
            
            # Cria o objeto Message
            return Message(
                user_id=user_id,
                user_name=data.get("pushName", "Usuário"),
                content=content,
                timestamp=datetime.now(),
                metadata={
                    "instance": webhook_data.instance,
                    "message_type": "text",
                    "from_me": key.get("fromMe", False)
                }
            )
            
        except Exception as e:
            # Log do erro e retorna None
            print(f"Erro ao processar mensagem: {str(e)}")
            return None

    async def validate_webhook(
        self, 
        webhook_data: WebhookData,
        headers: Dict[str, Any]
    ) -> bool:
        """
        Valida a autenticidade do webhook
        
        Args:
            webhook_data: Dados do webhook
            headers: Headers da requisição
            
        Returns:
            bool: True se webhook válido, False caso contrário
        """
        try:
            # Implementar validação do webhook aqui
            # Por exemplo, verificar signature nos headers
            # ou token de autenticação
            
            # Por enquanto retorna True para desenvolvimento
            return True
            
        except Exception as e:
            print(f"Erro na validação do webhook: {str(e)}")
            return False

    async def process_message(
        self, 
        webhook_data: WebhookData,
        headers: Dict[str, Any]
    ) -> Optional[Message]:
        """
        Processa uma mensagem recebida via webhook
        
        Args:
            webhook_data: Dados do webhook
            headers: Headers da requisição
            
        Returns:
            Message: Mensagem processada ou None se inválida
        """
        # Valida o webhook
        if not await self.validate_webhook(webhook_data, headers):
            return None
            
        # Extrai e retorna os dados da mensagem
        return await self.extract_message_data(webhook_data)