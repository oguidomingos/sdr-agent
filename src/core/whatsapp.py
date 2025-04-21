import httpx
from typing import Optional, Dict, Any
import json

from src.types.schemas import WhatsAppMessage
from src.config.settings import settings


class WhatsAppSender:
    """
    Gerencia o envio de mensagens via Evolution API
    """
    
    def __init__(self):
        self._validate_settings()
        self.base_url = settings.EVOLUTION_API_URL.rstrip('/')
        self.headers = self._get_headers()
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0
        )

    def _validate_settings(self) -> None:
        """
        Valida configurações necessárias
        """
        if not settings.EVOLUTION_API_URL:
            raise ValueError("EVOLUTION_API_URL não configurada")
            
        if settings.EVOLUTION_API_KEY:
            if not settings.EVOLUTION_API_KEY:
                raise ValueError("EVOLUTION_API_KEY não configurada")

    def _get_headers(self) -> Dict[str, str]:
        """
        Prepara os headers para requisições
        """
        headers = {
            'Content-Type': 'application/json'
        }
        
        if settings.EVOLUTION_API_KEY:
            headers['apikey'] = settings.EVOLUTION_API_KEY
            
        return headers

    def _format_number(self, number: str) -> str:
        """
        Formata o número para o padrão do WhatsApp
        
        Args:
            number: Número de telefone
            
        Returns:
            str: Número formatado
        """
        # Remove caracteres não numéricos
        clean_number = ''.join(filter(str.isdigit, number))
        
        # Adiciona @s.whatsapp.net se não existir
        if '@' not in clean_number:
            clean_number = f"{clean_number}@s.whatsapp.net"
            
        return clean_number

    async def send_message(
        self,
        message: WhatsAppMessage
    ) -> Optional[Dict[str, Any]]:
        """
        Envia uma mensagem via Evolution API
        
        Args:
            message: Dados da mensagem
            
        Returns:
            dict: Resposta da API ou None em caso de erro
        """
        try:
            # Formata o número
            formatted_number = self._format_number(message.number)
            
            # Prepara o payload
            payload = {
                "number": formatted_number,
                "text": message.message
            }
            
            # Adiciona metadados se existirem
            if message.metadata:
                payload["metadata"] = message.metadata
            
            # Envia a requisição
            instance_name = "teste"  # TODO: pegar o nome da instância da configuração
            response = await self.client.post(
                f"/message/sendText/{instance_name}",
                json=payload
            )
            
            # Verifica o status
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            print(f"Erro HTTP ao enviar mensagem: {str(e)}")
            return None
            
        except Exception as e:
            print(f"Erro ao enviar mensagem: {str(e)}")
            return None

    async def send_typing_status(
        self,
        number: str,
        duration: int = 3
    ) -> bool:
        """
        Envia status de "digitando" para o contato
        
        Args:
            number: Número do contato
            duration: Duração em segundos
            
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            formatted_number = self._format_number(number)
            
            payload = {
                "number": formatted_number,
                "duration": duration
            }
            
            response = await self.client.post(
                "/chat/typing",
                json=payload
            )
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"Erro ao enviar status de digitação: {str(e)}")
            return False

    async def mark_as_read(self, number: str) -> bool:
        """
        Marca a conversa como lida
        
        Args:
            number: Número do contato
            
        Returns:
            bool: True se marcado com sucesso
        """
        try:
            formatted_number = self._format_number(number)
            
            payload = {
                "number": formatted_number
            }
            
            response = await self.client.post(
                "/chat/markAsRead",
                json=payload
            )
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"Erro ao marcar como lido: {str(e)}")
            return False

    async def send_reaction(
        self,
        number: str,
        message_id: str,
        emoji: str
    ) -> bool:
        """
        Envia uma reação a uma mensagem
        
        Args:
            number: Número do contato
            message_id: ID da mensagem
            emoji: Emoji da reação
            
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            formatted_number = self._format_number(number)
            
            payload = {
                "number": formatted_number,
                "messageId": message_id,
                "reaction": emoji
            }
            
            response = await self.client.post(
                "/message/reaction",
                json=payload
            )
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"Erro ao enviar reação: {str(e)}")
            return False