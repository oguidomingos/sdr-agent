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
            
            # Configurar webhook se fornecido
            if webhook_url:
                webhook_result = await self.configure_webhook(
                    instance_name, 
                    webhook_url, 
                    webhook_events or ["MESSAGE_UPSERT"]
                )
                instance_result["webhook"] = webhook_result
            
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
        Configura webhook para uma instância
        
        Args:
            instance_name: Nome da instância
            webhook_url: URL do webhook
            events: Lista de eventos
            
        Returns:
            dict: Resposta da configuração do webhook
        """
        try:
            webhook_data = {
                "url": webhook_url,
                "webhook_by_events": True,
                "events": events or ["MESSAGE_UPSERT"]
            }
            
            response = await self.client.post(
                f"/webhook/set/{instance_name}",
                json=webhook_data
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Webhook configurado para instância '{instance_name}'")
            
            return result
            
        except httpx.HTTPError as e:
            print(f"❌ Erro HTTP ao configurar webhook: {e}")
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
        evolution_url: str,
        evolution_key: str,
        webhook_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Configura uma instância completa para um cliente
        
        Args:
            client_id: ID do cliente
            client_name: Nome do cliente
            evolution_url: URL da Evolution API
            evolution_key: Chave da API
            webhook_base_url: URL base para webhooks
            
        Returns:
            dict: Dados da instância criada
        """
        # Gera nome único da instância
        instance_name = f"client_{client_id}_{client_name.lower().replace(' ', '_')}"
        
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
                webhook_events=["MESSAGE_UPSERT", "CONNECTION_UPDATE"]
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