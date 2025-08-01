# 🚀 Deploy na Vercel - SDR Agent

## 📋 Pré-requisitos

1. **Conta na Vercel** - [vercel.com](https://vercel.com)
2. **Vercel CLI** instalado globalmente:
   ```bash
   npm i -g vercel
   ```
3. **Banco de dados PostgreSQL** (Recomendado: Neon ou Vercel Postgres)

## 🗄️ Configuração do Banco de Dados

### Opção 1: Neon (Recomendado)
1. Acesse [neon.tech](https://neon.tech)
2. Crie uma conta gratuita
3. Crie um novo projeto
4. Copie a connection string PostgreSQL

### Opção 2: Vercel Postgres
1. No painel da Vercel, vá em Storage
2. Crie um novo Postgres Database
3. Copie a connection string

## ⚙️ Configuração das Variáveis de Ambiente

No painel da Vercel, vá em Settings > Environment Variables e adicione:

```env
# Banco de Dados
DATABASE_URL=postgresql://username:password@hostname:port/database

# Evolution API (Já configurado)
EVOLUTION_API_URL=https://evolutionapi.centralsupernova.com.br
EVOLUTION_API_KEY=509dbd54-c20c-4a5b-b889-a0494a861f5a

# Gemini AI
GOOGLE_API_KEY=sua_api_key_gemini_aqui

# JWT Secret (Gere uma chave forte)
JWT_SECRET=sua_chave_jwt_super_secreta_aqui

# CORS (Substitua pelo seu domínio Vercel)
CORS_ORIGINS=https://seu-app.vercel.app

# Outras configurações
ENVIRONMENT=production
DEBUG=false
SEED_DATABASE=true
```

## 🚀 Deploy

### 1. Via Vercel CLI (Recomendado)

```bash
# Login na Vercel
vercel login

# No diretório do projeto
vercel

# Siga as instruções:
# ? Set up and deploy "~/sdr-agent"? Y
# ? Which scope do you want to deploy to? (escolha sua conta)
# ? Link to existing project? N
# ? What's your project's name? sdr-agent
# ? In which directory is your code located? ./
```

### 2. Via GitHub Integration

1. Push o código para um repositório GitHub
2. Na Vercel, conecte com GitHub
3. Importe o repositório
4. A Vercel detectará automaticamente as configurações

## 🔧 Configurações Automáticas

O arquivo `vercel.json` já está configurado com:

- ✅ Build do frontend React/Vite
- ✅ Serverless Functions para backend Python
- ✅ Rewrites para SPA
- ✅ Headers CORS
- ✅ Roteamento API

## 🌐 URLs de Acesso

Após o deploy:

- **Frontend**: `https://seu-app.vercel.app`
- **API**: `https://seu-app.vercel.app/api`
- **Health**: `https://seu-app.vercel.app/api/health`
- **Docs**: `https://seu-app.vercel.app/api/docs`

## 🔍 Troubleshooting

### Frontend não carrega:
```bash
# Verifique se o build passou
vercel logs

# Teste local
cd frontend && npm run build
```

### API não responde:
```bash
# Verifique os logs das functions
vercel logs --scope functions

# Teste local
python -m uvicorn api.index:app --reload
```

### Erro de CORS:
1. Verifique a variável `CORS_ORIGINS`
2. Deve incluir o domínio exato da Vercel

### Erro de Banco:
1. Verifique a `DATABASE_URL`
2. Execute as migrações se necessário

## 📊 Monitoramento

No painel da Vercel você pode:
- Ver logs em tempo real
- Monitorar performance
- Configurar alertas
- Ver métricas de uso

## 🔄 Atualizações

Para atualizar:
```bash
# Via CLI
vercel --prod

# Via Git (se conectado ao GitHub)
git push origin main
```

## 💡 Dicas Importantes

1. **Variáveis de Ambiente**: Configure todas antes do primeiro deploy
2. **Banco de Dados**: Use connection pooling para melhor performance
3. **CORS**: Sempre especifique domínios exatos em produção
4. **Logs**: Monitore regularmente para detectar problemas
5. **SSL**: A Vercel fornece HTTPS automático