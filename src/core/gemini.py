import google.generativeai as genai
from typing import Optional, Dict, Any
import json

from src.types.schemas import GeminiRequest, GeminiResponse, SessionContext
from src.config.settings import settings
from src.config.prompts import BASE_PROMPT, RESPONSES


class GeminiClient:
    """
    Cliente para interação com a API do Google Gemini
    Agora suporta configurações específicas por cliente
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        # Usa configurações específicas ou fallback para globais
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model or settings.GEMINI_MODEL
        
        self._validate_settings()
        genai.configure(api_key=self.api_key)
        
        # Lista os modelos disponíveis apenas uma vez
        if not hasattr(GeminiClient, '_models_listed'):
            print("\n=== Modelos Gemini Disponíveis ===")
            for model in genai.list_models():
                print(f"- {model.name}")
            print("=== Fim da Lista de Modelos ===\n")
            GeminiClient._models_listed = True
        
        # Usa o modelo configurado
        self.model = genai.GenerativeModel(self.model_name)
        print(f"Modelo Gemini inicializado: {self.model_name}")

    def _validate_settings(self) -> None:
        """
        Valida se a API key do Gemini está configurada
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não configurada")

    def _format_context(self, session: SessionContext) -> str:
        """
        Formata o contexto da sessão para o prompt
        
        Args:
            session: Contexto da sessão atual
            
        Returns:
            str: Contexto formatado
        """
        context_messages = []
        
        # Adiciona metadados relevantes
        if session.metadata:
            context_messages.append("Contexto da conversa:")
            for key, value in session.metadata.items():
                context_messages.append(f"- {key}: {value}")
            context_messages.append("")
        
        # Adiciona histórico de mensagens
        context_messages.append("Histórico de mensagens:")
        for msg in session.messages:
            role = "SDR" if msg.metadata.get("from_me", False) else "Cliente"
            context_messages.append(f"{role}: {msg.content}")
        
        return "\n".join(context_messages)

    def _prepare_prompt(
        self,
        user_message: str,
        context: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Prepara o prompt completo para o Gemini
        
        Args:
            user_message: Mensagem do usuário
            context: Contexto opcional
            parameters: Parâmetros adicionais
            
        Returns:
            str: Prompt formatado
        """
        # Usa system_prompt dos parâmetros se fornecido, senão usa o BASE_PROMPT
        if parameters and parameters.get("system_prompt"):
            base_prompt = parameters["system_prompt"]
        else:
            from src.config.prompts import BASE_PROMPT
            base_prompt = BASE_PROMPT
        
        # Adiciona o contexto se disponível
        if context:
            base_prompt += f"\n\nContexto da conversa:\n{context}"
        
        # Adiciona a mensagem do usuário
        base_prompt += f"\n\nMensagem do cliente: {user_message}"
        base_prompt += "\n\nSua resposta:"
        
        return base_prompt

    async def generate_response(
        self,
        request: GeminiRequest
    ) -> Optional[GeminiResponse]:
        """
        Gera uma resposta usando o Gemini
        
        Args:
            request: Dados da requisição
            
        Returns:
            GeminiResponse: Resposta gerada ou None em caso de erro
        """
        try:
            # Prepara o prompt
            prompt = self._prepare_prompt(
                request.prompt,
                request.context,
                request.parameters
            )
            
            # Gera a resposta
            response = self.model.generate_content(prompt)
            
            # Processa e retorna a resposta
            return GeminiResponse(
                content=response.text,
                metadata={
                    "prompt_tokens": len(prompt.split()),
                    "response_tokens": len(response.text.split()),
                    "parameters_used": request.parameters
                }
            )
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ Erro ao gerar resposta:")
            print(f"- Tipo de erro: {type(e).__name__}")
            print(f"- Mensagem: {error_msg}")
            print(f"- Prompt usado: {request.prompt}")
            print(f"- Contexto: {request.context[:100]}...")  # Primeiros 100 caracteres do contexto
            return None

    async def process_session(
        self,
        session: SessionContext,
        user_message: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[GeminiResponse]:
        """
        Processa uma sessão completa
        
        Args:
            session: Contexto da sessão
            user_message: Mensagem do usuário
            parameters: Parâmetros adicionais
            
        Returns:
            GeminiResponse: Resposta processada
        """
        # Verifica se é a primeira mensagem para usar o greeting
        is_first_message = len(session.messages) == 1
        
        # Formata o contexto da sessão
        context = self._format_context(session)
        
        # Se for primeira mensagem, usa o welcome_prompt personalizado ou padrão
        if is_first_message and user_message.lower() in ['oi', 'olá', 'ola', 'hey', 'hello', 'hi']:
            name = session.metadata.get('name', '')
            
            # Usa welcome_prompt dos parâmetros se fornecido
            if parameters and parameters.get('welcome_prompt'):
                welcome_message = parameters['welcome_prompt']
                if name:
                    welcome_message = welcome_message.replace('[nome]', name).replace('[Nome]', name)
            else:
                # Fallback para mensagem padrão
                welcome_message = f"Olá{f' {name}' if name else ''}! Como posso ajudá-lo hoje?"
            
            # Retorna mensagem de boas-vindas como texto simples
            return GeminiResponse(
                content=welcome_message,
                metadata={
                    'is_greeting': True,
                    'personalized': bool(name)
                }
            )
        else:
            # Cria a requisição normal
            request = GeminiRequest(
                prompt=user_message,
                context=context,
                parameters=parameters
            )
        
        # Gera e retorna a resposta
        return await self.generate_response(request)