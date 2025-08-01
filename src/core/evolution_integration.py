import httpx
import asyncio
from typing import Optional, Dict, Any, List
import json
import uuid
from urllib.parse import urljoin

from src.config.settings import settings
from src.types.auth_schemas import EvolutionInstanceCreate, EvolutionInstanceResponse


class EvolutionAPIClient:
    """
    Cliente para integração automática com Evolution API
    """
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'apikey': api_key
        }
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0
        )
    
    async def create_instance(
        self, 
        instance_name: str,
        webhook_url: Optional[str] = None,
        webhook_events: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Cria uma nova instância no Evolution API
        
        Args:
            instance_name: Nome da instância
            webhook_url: URL do webhook
            webhook_events: Lista de eventos para o webhook
            
        Returns:
            dict: Resposta da API com dados da instância
        """
        try:
            # Dados para criar instância
            instance_data = {
                "instanceName": instance_name,
                "qrcode": True,
                "integration": "WHATSAPP-BAILEYS"
            }
            
            # Criar instância
            response = await self.client.post("/instance/create", json=instance_data)
            response.raise_for_status()
            instance_result = response.json()
            
            print(f"✅ Instância '{instance_name}' criada com sucesso")
            
            # Configurar webhook se fornecido (não falha se webhook der erro)
            webhook_configured = False
            if webhook_url:
                try:
                    webhook_result = await self.configure_webhook(
                        instance_name, 
                        webhook_url, 
                        webhook_events or ["MESSAGES_UPSERT", "CONNECTION_UPDATE"]
                    )
                    instance_result["webhook"] = webhook_result
                    webhook_configured = True
                    print(f"✅ Webhook configurado com sucesso para '{instance_name}'")
                except Exception as webhook_error:
                    print(f"⚠️  Falha ao configurar webhook para '{instance_name}': {webhook_error}")
                    print(f"📝 Instância criada com sucesso, mas webhook deve ser configurado manualmente")
                    instance_result["webhook"] = {"error": str(webhook_error), "configured": False}
            
            instance_result["webhook_configured"] = webhook_configured
            return instance_result
            
        except httpx.HTTPError as e:
            print(f"❌ Erro HTTP ao criar instância: {e}")
            raise Exception(f"Erro ao criar instância Evolution: {e}")
        except Exception as e:
            print(f"❌ Erro ao criar instância: {e}")
            raise
    
    async def configure_webhook(
        self, 
        instance_name: str, 
        webhook_url: str,
        events: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Configura webhook para uma instância usando Evolution API v2
        
        Args:
            instance_name: Nome da instância
            webhook_url: URL do webhook
            events: Lista de eventos
            
        Returns:
            dict: Resposta da configuração do webhook
        """
        try:
            # Payload correto para Evolution API
            webhook_data = {
                "enabled": True,
                "url": webhook_url,
                "webhook_by_events": False,  # Usar um webhook para todos os eventos
                "events": events or [
                    "MESSAGES_UPSERT", 
                    "CONNECTION_UPDATE",
                    "QRCODE_UPDATED"
                ],
                "webhook": {
                    "enabled": True,
                    "url": webhook_url,
                    "by_events": False,
                    "events": events or [
                        "MESSAGES_UPSERT", 
                        "CONNECTION_UPDATE",
                        "QRCODE_UPDATED"
                    ]
                }
            }
            
            # Endpoint correto: /webhook/set/{instance_name}
            response = await self.client.post(
                f"/webhook/set/{instance_name}",
                json=webhook_data
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Webhook configurado para instância '{instance_name}' na URL: {webhook_url}")
            
            return result
            
        except httpx.HTTPError as e:
            print(f"❌ Erro HTTP ao configurar webhook: {e}")
            # Log mais detalhes para debug
            try:
                error_detail = await e.response.aread() if hasattr(e, 'response') else str(e)
                print(f"❌ Detalhes do erro: {error_detail}")
            except:
                pass
            raise Exception(f"Erro ao configurar webhook: {e}")
        except Exception as e:
            print(f"❌ Erro ao configurar webhook: {e}")
            raise
    
    async def get_instance_status(self, instance_name: str) -> Dict[str, Any]:
        """
        Verifica status de uma instância
        
        Args:
            instance_name: Nome da instância
            
        Returns:
            dict: Status da instância
        """
        try:
            response = await self.client.get(f"/instance/connectionState/{instance_name}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"❌ Erro ao verificar status da instância: {e}")
            raise Exception(f"Erro ao verificar status: {e}")
    
    async def get_qr_code(self, instance_name: str) -> Dict[str, Any]:
        """
        Obtém QR Code de uma instância
        
        Args:
            instance_name: Nome da instância
            
        Returns:
            dict: Dados do QR Code
        """
        try:
            response = await self.client.get(f"/instance/connect/{instance_name}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"❌ Erro ao obter QR Code: {e}")
            raise Exception(f"Erro ao obter QR Code: {e}")
    
    async def delete_instance(self, instance_name: str) -> bool:
        """
        Deleta uma instância
        
        Args:
            instance_name: Nome da instância
            
        Returns:
            bool: True se deletada com sucesso
        """
        try:
            response = await self.client.delete(f"/instance/delete/{instance_name}")
            response.raise_for_status()
            print(f"✅ Instância '{instance_name}' deletada com sucesso")
            return True
        except httpx.HTTPError as e:
            print(f"❌ Erro ao deletar instância: {e}")
            return False
    
    async def list_instances(self) -> List[Dict[str, Any]]:
        """
        Lista todas as instâncias
        
        Returns:
            List[dict]: Lista de instâncias
        """
        try:
            response = await self.client.get("/instance/fetchInstances")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"❌ Erro ao listar instâncias: {e}")
            return []
    
    async def connect_with_pairing_code(
        self, 
        instance_name: str, 
        pairing_code: str
    ) -> Dict[str, Any]:
        """
        Conecta instância usando código de pareamento
        
        Args:
            instance_name: Nome da instância
            pairing_code: Código de pareamento do WhatsApp
            
        Returns:
            dict: Resposta da conexão
        """
        try:
            pairing_data = {
                "number": pairing_code
            }
            
            response = await self.client.post(
                f"/instance/connect/{instance_name}",
                json=pairing_data
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            print(f"❌ Erro ao conectar com código de pareamento: {e}")
            raise Exception(f"Erro ao conectar com código de pareamento: {e}")

    async def send_message(
        self, 
        instance_name: str, 
        number: str, 
        message: str
    ) -> Dict[str, Any]:
        """
        Envia mensagem através da instância
        
        Args:
            instance_name: Nome da instância
            number: Número do destinatário
            message: Mensagem a enviar
            
        Returns:
            dict: Resposta do envio
        """
        try:
            message_data = {
                "number": number,
                "text": message
            }
            
            response = await self.client.post(
                f"/message/sendText/{instance_name}",
                json=message_data
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            raise Exception(f"Erro ao enviar mensagem: {e}")
    
    async def close(self):
        """Fecha o cliente HTTP"""
        await self.client.aclose()


class EvolutionIntegrationService:
    """
    Serviço de integração completa com Evolution API para multi-tenancy
    """
    
    def __init__(self):
        # Usa as configurações globais por padrão
        self.default_evolution_url = settings.EVOLUTION_API_URL
        self.default_evolution_key = settings.EVOLUTION_API_KEY
    
    def get_client(self, evolution_url: str, evolution_key: str) -> EvolutionAPIClient:
        """
        Cria cliente Evolution API com credenciais específicas
        
        Args:
            evolution_url: URL da Evolution API
            evolution_key: Chave da API
            
        Returns:
            EvolutionAPIClient: Cliente configurado
        """
        return EvolutionAPIClient(evolution_url, evolution_key)
    
    async def setup_client_instance(
        self,
        client_id: str,
        client_name: str,
        whatsapp_number: str,
        evolution_url: str,
        evolution_key: str,
        webhook_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Configura uma instância completa para um cliente
        
        Args:
            client_id: ID do cliente
            client_name: Nome do cliente
            whatsapp_number: Número do WhatsApp que será conectado
            evolution_url: URL da Evolution API
            evolution_key: Chave da API
            webhook_base_url: URL base para webhooks
            
        Returns:
            dict: Dados da instância criada
        """
        # Gera nome único da instância baseado no número do WhatsApp
        # Remove caracteres especiais do número (mantém apenas dígitos)
        import re
        clean_number = re.sub(r'[^0-9]', '', whatsapp_number)
        
        # Sanitiza o nome do cliente
        sanitized_name = client_name.lower().replace(' ', '_').replace('-', '_')
        sanitized_name = re.sub(r'[^a-z0-9_]', '', sanitized_name)
        
        # Se client_id é "temp", gera um UUID temporário
        if client_id == "temp":
            import uuid
            temp_id = str(uuid.uuid4())[:8]  # Primeiros 8 caracteres do UUID
            instance_name = f"whatsapp_{clean_number}_{temp_id}_{sanitized_name}"
        else:
            instance_name = f"whatsapp_{clean_number}_{client_id}_{sanitized_name}"
        
        # URL do webhook específica para este cliente
        if not webhook_base_url:
            webhook_base_url = settings.WEBHOOK_BASE_URL or "https://seu-sdr-agent.com"
        
        webhook_url = f"{webhook_base_url}/webhook/whatsapp/{client_id}"
        
        # Cria cliente Evolution
        evolution_client = self.get_client(evolution_url, evolution_key)
        
        try:
            # Cria instância
            result = await evolution_client.create_instance(
                instance_name=instance_name,
                webhook_url=webhook_url,
                webhook_events=["MESSAGES_UPSERT", "CONNECTION_UPDATE", "QRCODE_UPDATED"]
            )
            
            # Gera secret para webhook
            webhook_secret = str(uuid.uuid4())
            
            return {
                "instance_name": instance_name,
                "instance_id": result.get("instance", {}).get("instanceId"),
                "instance_token": result.get("hash"),
                "webhook_url": webhook_url,
                "webhook_secret": webhook_secret,
                "qr_code": result.get("qrcode"),
                "status": result.get("instance", {}).get("status"),
                "full_response": result
            }
            
        finally:
            await evolution_client.close()
    
    async def delete_client_instance(
        self,
        instance_name: str,
        evolution_url: str,
        evolution_key: str
    ) -> bool:
        """
        Deleta instância de um cliente
        
        Args:
            instance_name: Nome da instância
            evolution_url: URL da Evolution API
            evolution_key: Chave da API
            
        Returns:
            bool: True se deletada com sucesso
        """
        evolution_client = self.get_client(evolution_url, evolution_key)
        
        try:
            return await evolution_client.delete_instance(instance_name)
        finally:
            await evolution_client.close()
    
    async def get_client_qr_code(
        self,
        instance_name: str,
        evolution_url: str,
        evolution_key: str
    ) -> Dict[str, Any]:
        """
        Obtém QR Code de um cliente
        
        Args:
            instance_name: Nome da instância
            evolution_url: URL da Evolution API
            evolution_key: Chave da API
            
        Returns:
            dict: Dados do QR Code
        """
        evolution_client = self.get_client(evolution_url, evolution_key)
        
        try:
            return await evolution_client.get_qr_code(instance_name)
        finally:
            await evolution_client.close()
    
    async def connect_with_pairing_code(
        self,
        instance_name: str,
        pairing_code: str,
        evolution_url: str,
        evolution_key: str
    ) -> Dict[str, Any]:
        """
        Conecta instância usando código de pareamento
        
        Args:
            instance_name: Nome da instância
            pairing_code: Código de pareamento
            evolution_url: URL da Evolution API
            evolution_key: Chave da API
            
        Returns:
            dict: Resposta da conexão
        """
        evolution_client = self.get_client(evolution_url, evolution_key)
        
        try:
            return await evolution_client.connect_with_pairing_code(instance_name, pairing_code)
        finally:
            await evolution_client.close()

    async def update_webhook_url(
        self,
        instance_name: str,
        webhook_url: str,
        evolution_url: str,
        evolution_key: str
    ) -> Dict[str, Any]:
        """
        Atualiza URL do webhook de uma instância
        
        Args:
            instance_name: Nome da instância
            webhook_url: Nova URL do webhook
            evolution_url: URL da Evolution API
            evolution_key: Chave da API
            
        Returns:
            dict: Resposta da atualização
        """
        evolution_client = self.get_client(evolution_url, evolution_key)
        
        try:
            return await evolution_client.configure_webhook(
                instance_name=instance_name,
                webhook_url=webhook_url,
                events=["MESSAGES_UPSERT", "CONNECTION_UPDATE", "QRCODE_UPDATED"]
            )
        finally:
            await evolution_client.close()

    async def check_instance_status(
        self,
        instance_name: str,
        evolution_url: str,
        evolution_key: str
    ) -> Dict[str, Any]:
        """
        Verifica status da instância de um cliente
        
        Args:
            instance_name: Nome da instância
            evolution_url: URL da Evolution API
            evolution_key: Chave da API
            
        Returns:
            dict: Status da instância
        """
        evolution_client = self.get_client(evolution_url, evolution_key)
        
        try:
            return await evolution_client.get_instance_status(instance_name)
        finally:
            await evolution_client.close()

# Instância global do serviço
evolution_service = EvolutionIntegrationService()