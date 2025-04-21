import google.generativeai as genai
from typing import Optional, Dict, Any
import json

from src.types.schemas import GeminiRequest, GeminiResponse, SessionContext
from src.config.settings import settings
from src.config.prompts import BASE_PROMPT, RESPONSES


class GeminiClient:
    """
    Cliente para interação com a API do Google Gemini
    """
    
    def __init__(self):
        self._validate_settings()
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Lista os modelos disponíveis
        print("\n=== Modelos Gemini Disponíveis ===")
        for model in genai.list_models():
            print(f"- {model.name}")
        print("=== Fim da Lista de Modelos ===\n")
        
        # Usa o modelo configurado
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        print(f"Modelo Gemini inicializado: {settings.GEMINI_MODEL}")

    def _validate_settings(self) -> None:
        """
        Valida se a API key do Gemini está configurada
        """
        if not settings.GEMINI_API_KEY:
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
        # Importa e usa o prompt base configurado
        from src.config.prompts import BASE_PROMPT, RESPONSES
        base_prompt = BASE_PROMPT
        # Adiciona o contexto se disponível
        if context:
            base_prompt += f"\nContexto da conversa:\n{context}\n"
        
        # Adiciona parâmetros específicos se fornecidos
        if parameters:
            base_prompt += f"\nParâmetros adicionais:\n{json.dumps(parameters, indent=2)}\n"
        
        # Adiciona a mensagem do usuário
        base_prompt += f"\nMensagem do cliente: {user_message}\n"
        base_prompt += "\nSua resposta:"
        
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
        
        # Se for primeira mensagem, retorna as duas primeiras partes da saudação
        if is_first_message and user_message.lower() in ['oi', 'olá', 'ola', 'hey']:
            name = session.metadata.get('name', '')
            greeting_part1 = RESPONSES['greeting_part1'].format(name=name)
            greeting_part2 = RESPONSES['greeting_part2'].format(name=name)
            
            # Retorna imediatamente um objeto GeminiResponse com as duas partes
            return GeminiResponse(
                content=json.dumps({
                    'type': 'greeting',
                    'parts': [greeting_part1, greeting_part2]
                }),
                metadata={
                    'is_greeting': True,
                    'parts_count': 2
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