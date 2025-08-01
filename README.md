# SDR Agent

Sistema inteligente de automação para SDR (Sales Development Representative) que integra WhatsApp com IA generativa para qualificação de leads e agendamento de reuniões.

## Características

- Integração com WhatsApp via Evolution API
- IA Generativa usando Google Gemini  
- Metodologia SPIN Selling
- Gerenciamento de contexto e sessões
- Processamento assíncrono com FastAPI
- Cache com Redis
- Frontend React com interface web completa
- Sistema multi-tenant com autenticação JWT
- Containerização com Docker

## Requisitos

- Python 3.11+
- Node.js 18+ (Para desenvolvimento do frontend)
- PostgreSQL
- Redis
- Evolution API configurada
- Chave de API do Google Gemini
- Docker e Docker Compose (Para execução em containers)

## Configuração

1. Clone o repositório
```bash
git clone <repository-url>
cd sdr-agent
```

2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## Execução

### Local

1. Inicie o Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

2. Execute a aplicação
```bash
python main.py
```

### Docker Compose

```bash
docker-compose up -d
```

## Uso

1. Configure o webhook na Evolution API para apontar para:
```
http://seu-servidor:8000/webhook/whatsapp
```

2. O sistema irá:
   - Receber mensagens do WhatsApp
   - Processar usando IA generativa
   - Manter contexto da conversa
   - Responder automaticamente
   - Tentar qualificar e agendar reuniões

## Estrutura do Projeto

```
sdr-agent/
├── src/
│   ├── api/
│   │   └── routes.py          # Endpoints da API
│   ├── config/
│   │   ├── settings.py        # Configurações
│   │   └── prompts.py         # Templates de prompts
│   ├── core/
│   │   ├── message.py         # Processamento de mensagens
│   │   ├── session.py         # Gerenciamento de sessões
│   │   ├── gemini.py          # Cliente Gemini
│   │   └── whatsapp.py        # Cliente WhatsApp
│   └── types/
│       └── schemas.py         # Modelos de dados
├── tests/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── main.py
├── README.md
└── requirements.txt
```

## Endpoints da API

- `POST /webhook/whatsapp` - Recebe webhooks da Evolution API
- `GET /health` - Healthcheck da aplicação
- `GET /sessions/{user_id}` - Consulta dados de uma sessão
- `DELETE /sessions/{user_id}` - Remove uma sessão

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a MIT License.