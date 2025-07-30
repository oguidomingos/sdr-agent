import httpx
import asyncio
from typing import Optional, Dict, Any, List
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

    def _split_message(self, text: str, max_length: int = 300) -> List[str]:
        """
        Divide uma mensagem em partes menores
        
        Args:
            text: Texto para dividir
            max_length: Tamanho máximo de cada parte
            
        Returns:
            List[str]: Lista com as partes da mensagem
        """
        # Força divisão se o texto for maior que o máximo
        if len(text) > max_length:
            parts = []
            # Divide o texto em parágrafos
            paragraphs = text.split('\n\n')
            
            current_text = ""
            for paragraph in paragraphs:
                # Se o parágrafo é maior que o limite, divide em partes
                if len(paragraph) > max_length:
                    # Primeiro adiciona o texto acumulado se existir
                    if current_text:
                        parts.append(current_text)
                        current_text = ""
                        
                    # Divide o parágrafo em partes fixas
                    while paragraph:
                        parts.append(paragraph[:max_length])
                        paragraph = paragraph[max_length:]
                
                # Se adicionar o parágrafo excede o limite
                elif len(current_text) + len(paragraph) + 2 > max_length:
                    parts.append(current_text)
                    current_text = paragraph
                else:
                    if current_text:
                        current_text += '\n\n'
                    current_text += paragraph
            
            # Adiciona o texto restante
            if current_text:
                parts.append(current_text)
                
            # Se ainda assim tiver partes muito grandes, divide novamente
            final_parts = []
            for part in parts:
                if len(part) > max_length:
                    final_parts.extend([part[i:i + max_length] for i in range(0, len(part), max_length)])
                else:
                    final_parts.append(part)
                    
            return final_parts
        
        return [text]

    async def send_message(
        self,
        message: WhatsAppMessage,
        typing_duration: Optional[int] = None,
        cooldown: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        Envia uma mensagem via Evolution API
        
        Args:
            message: Dados da mensagem
            
        Returns:
            dict: Resposta da API ou None em caso de erro
        """
        try:
            # Divide a mensagem em partes se necessário
            message_parts = self._split_message(message.message)
            last_response = None
            
            for part in message_parts:
                # Define duração do typing baseado no tamanho da mensagem
                if typing_duration is None:
                    msg_length = len(part)
                    if msg_length < 50:
                        typing_duration = 5  # short
                    elif msg_length < 200:
                        typing_duration = 7  # medium
                    else:
                        typing_duration = 10  # long
                
                # Obtém o nome da instância dos metadados ou usa o padrão
                instance_name = message.metadata.get('instance') if message.metadata else settings.DEFAULT_EVOLUTION_INSTANCE
                
                # Ativa o status de digitação antes de cada parte
                try:
                    await self.send_typing_status(
                        message.number,
                        typing_duration,
                        instance_name
                    )
                except Exception as e:
                    print(f"Erro ao enviar status de digitação: {str(e)}")
                
                # Formata o número e prepara o payload
                formatted_number = self._format_number(message.number)
                payload = {
                    "number": formatted_number,
                    "text": part
                }
                
                # Adiciona metadados se existirem
                if message.metadata:
                    payload["metadata"] = message.metadata
                
                # Envia a requisição
                response = await self.client.post(
                    f"/message/sendText/{instance_name}",
                    json=payload
                )
                
                # Verifica o status
                response.raise_for_status()
                last_response = response.json()
                
                # Aguarda um pequeno intervalo entre as partes das mensagens
                # para parecer mais natural
                if len(message_parts) > 1 and cooldown > 0:
                    await asyncio.sleep(cooldown)
            
            return last_response
            
        except httpx.HTTPError as e:
            print(f"Erro HTTP ao enviar mensagem: {str(e)}")
            return None
            
        except Exception as e:
            print(f"Erro ao enviar mensagem: {str(e)}")
            return None

    async def send_typing_status(
        self,
        number: str,
        duration: int = 3,
        instance: Optional[str] = None
    ) -> bool:
        """
        Envia status de "digitando" para o contato
        
        Args:
            number: Número do contato
            duration: Duração em segundos
            instance: Nome da instância WhatsApp
            
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            if not instance:
                instance = settings.DEFAULT_EVOLUTION_INSTANCE
            
            # Formata o número
            formatted_number = self._format_number(number)
            
            # Envia status "composing"
            await self.client.post(
                f"/chat/presence/{instance}",
                json={
                    "number": formatted_number,
                    "presence": "composing"
                }
            )
            
            # Aguarda a duração especificada
            if duration > 0:
                await asyncio.sleep(duration)
            
            # Envia status "paused" para parar de digitar
            await self.client.post(
                f"/chat/presence/{instance}",
                json={
                    "number": formatted_number,
                    "presence": "paused"
                }
            )
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar status de digitação: {str(e)}")
            return False
            
        try:
            if not instance:
                instance = settings.DEFAULT_EVOLUTION_INSTANCE
                
            # Formata o número
            formatted_number = self._format_number(number)
                
            payload = {
                "number": formatted_number,
                "presence": "composing"
            }
            
            response = await self.client.post(
                f"/chat/presence/{instance}",
                json=payload
            )
            
            response.raise_for_status()
            
            # Aguarda a duração especificada
            if duration > 0:
                await asyncio.sleep(duration)
                
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