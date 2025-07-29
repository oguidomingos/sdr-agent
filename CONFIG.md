# Guia de Configuração do SDR Agent

## 1. Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

### Configurações Essenciais:

1. **Google Gemini API**
   - Acesse: https://makersuite.google.com/app/apikey
   - Crie uma chave API
   - Configure em: `GEMINI_API_KEY`

2. **Evolution API**
   - URL da sua instância (exemplo: http://localhost:8080)
   - Configure em: `EVOLUTION_API_URL`
   - Se tiver autenticação, adicione em: `EVOLUTION_API_KEY`

3. **Webhook Secret**
   - Gere um secret único usando:
   ```bash
   openssl rand -hex 32
   ```
   - Configure em: `WEBHOOK_SECRET`
   - Use este mesmo secret ao configurar o webhook na Evolution API

4. **Redis**
   - Abra o arquivo `docker-compose.yml`
   - Localize a seção `redis:`
   - A senha é definida na linha `command: redis-server --requirepass ${REDIS_PASSWORD}`
   - No arquivo `.env`, defina:
   ```
   REDIS_PASSWORD=sua_senha_segura_aqui
   ```
   - Use a mesma senha que você definiu no .env

## 2. Configurando o Webhook na Evolution API

### Para acesso local:
1. URL do webhook: `http://localhost:8000/webhook/whatsapp`

### Para acesso externo:
1. Se estiver usando em produção, você precisa:
   - Ter um domínio configurado (exemplo: seudominio.com)
   - Configurar SSL (recomendado usar Nginx + Let's Encrypt)
   - URL do webhook será: `https://seudominio.com/webhook/whatsapp`

2. Se estiver testando localmente e precisar de acesso externo:
   - Use ngrok para criar um túnel:
   ```bash
   # Instale o ngrok
   # Execute:
   ngrok http 8000
   ```
   - Copie a URL https gerada (exemplo: https://a1b2c3d4.ngrok.io)
   - Use esta URL + /webhook/whatsapp na Evolution API

3. Na Evolution API:
   - Acesse sua instância
   - Vá em "Configurações" > "Webhooks"
   - Adicione novo webhook:
     - URL: sua URL completa + /webhook/whatsapp
     - Eventos: selecione `Message_Upsert`
     - Secret: use o mesmo valor de `WEBHOOK_SECRET` do seu .env

## 3. Iniciando o Sistema

### Usando Docker (Recomendado):
```bash
# Inicia todos os serviços (API e Redis)
docker-compose up -d

# Verificar logs
docker-compose logs -f
```

### Manual:
1. Inicie o Redis:
```bash
# Instale o Redis no seu sistema
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS com Homebrew:
brew install redis

# Configure a senha no redis.conf
# Ubuntu: /etc/redis/redis.conf
# Mac: /usr/local/etc/redis.conf
# Adicione/modifique a linha:
requirepass sua_senha_segura_aqui

# Inicie o serviço:
redis-server
```

2. Inicie a aplicação:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

pip install -r requirements.txt
python main.py
```

## 4. Verificando a Instalação

1. Teste o healthcheck:
```bash
curl http://localhost:8000/health
```

2. Teste o Redis:
```bash
# Com Docker:
docker exec -it sdr-agent-redis redis-cli
auth sua_senha_segura_aqui  # Use a senha do .env
ping  # Deve responder "PONG"

# Manual:
redis-cli
auth sua_senha_segura_aqui
ping
```

## 5. Troubleshooting

1. **Erro de conexão com Redis**:
   - Verifique se REDIS_PASSWORD no .env coincide com a senha no docker-compose.yml
   - Teste a conexão: `redis-cli -a sua_senha_segura_aqui ping`

2. **Webhook não recebe mensagens**:
   - Se usando ngrok: verifique se o túnel está ativo
   - Se usando domínio: verifique SSL e firewall
   - Confirme se a URL completa do webhook está correta
   - Verifique logs: `docker-compose logs -f app`

3. **Erros do Gemini**:
   - Valide a API key
   - Verifique os logs para mensagens de erro
