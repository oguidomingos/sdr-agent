# 🚀 Setup Produção - Branch `prod`

## ✅ O que foi configurado:

### 📁 **Estrutura da Branch `prod`:**
- ✅ API reestruturada para Vercel Serverless Functions
- ✅ Configurações específicas de produção
- ✅ Separação entre desenvolvimento e produção
- ✅ CORS configurado para domínio da Vercel

### 🔗 **Nova URL de Produção:**
- **Frontend**: https://sdr-agent-dgxvtu11s-oguidomingos-projects.vercel.app
- **API**: https://sdr-agent-dgxvtu11s-oguidomingos-projects.vercel.app/api

## ⚙️ **Environment Variables para atualizar na Vercel:**

```env
# Database
DATABASE_URL=postgres://neondb_owner:npg_dQgaVF8jOxb0@ep-fancy-dawn-adbs8562-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require

# Evolution API
EVOLUTION_API_URL=https://evolutionapi.centralsupernova.com.br
EVOLUTION_API_KEY=509dbd54-c20c-4a5b-b889-a0494a861f5a

# Gemini AI
GOOGLE_API_KEY=AIzaSyASsQw-arw3Mqp7q01qy37Wxkrj-Lo0oHk

# JWT Security
JWT_SECRET=KTdudt/oY/pMnhiHFKNRJJg7HgAezTpNTf/37rrCBno=

# CORS (ATUALIZADO para nova URL)
CORS_ORIGINS=https://sdr-agent-dgxvtu11s-oguidomingos-projects.vercel.app

# Application
ENVIRONMENT=production
DEBUG=false
SEED_DATABASE=true
```

## 🔄 **Para aplicar as mudanças:**

1. **Atualize as Environment Variables** no painel da Vercel:
   - Acesse: https://vercel.com/oguidomingos-projects/sdr-agent/settings/environment-variables
   - **IMPORTANTE**: Atualize `CORS_ORIGINS` com a nova URL!

2. **Conecte a branch `prod` na Vercel**:
   - Vá em Settings > Git
   - Mude para Production Branch: `prod`

3. **Redeploy**:
   ```bash
   vercel --prod
   ```

## 🛠️ **Nova Estrutura da API:**

### **Endpoints Serverless Functions:**
- `/api/` - Health check e info geral
- `/api/auth` - Autenticação (login, register, me)
- `/api/clients` - Gerenciamento de clientes
- `/api/webhook` - Webhooks do WhatsApp

### **Frontend Build:**
- ✅ Vite otimizado para produção
- ✅ Variáveis de ambiente específicas para prod
- ✅ CORS configurado corretamente

## 🔍 **Para debuggar problemas:**

1. **Logs da Vercel**:
   ```bash
   vercel logs --scope functions
   ```

2. **Testar endpoints**:
   - Health: https://sdr-agent-dgxvtu11s-oguidomingos-projects.vercel.app/api/
   - Auth: https://sdr-agent-dgxvtu11s-oguidomingos-projects.vercel.app/api/auth/

3. **Browser Developer Tools**:
   - Verifique Network tab para erros de CORS
   - Console para erros JavaScript

## 📋 **Checklist Final:**

- [ ] Atualizar `CORS_ORIGINS` com nova URL
- [ ] Configurar Production Branch como `prod`
- [ ] Testar login/registro
- [ ] Verificar webhook do WhatsApp
- [ ] Confirmar conexão com banco Neon

A branch `prod` está isolada e otimizada para produção! 🎉