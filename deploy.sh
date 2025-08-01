#!/bin/bash

echo "🚀 Iniciando deploy do SDR Agent na Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI não encontrado. Instalando..."
    npm install -g vercel
fi

# Check if logged in to Vercel
echo "🔑 Verificando login na Vercel..."
if ! vercel whoami &> /dev/null; then
    echo "🔐 Fazendo login na Vercel..."
    vercel login
fi

# Build frontend to check for errors
echo "🏗️  Fazendo build do frontend..."
cd frontend
npm install
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Erro no build do frontend. Corrija os erros antes de continuar."
    exit 1
fi

cd ..

echo "✅ Build do frontend OK!"

# Check Python requirements
echo "🐍 Verificando dependências Python..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erro nas dependências Python. Verifique o requirements.txt"
    exit 1
fi

echo "✅ Dependências Python OK!"

# Deploy to Vercel
echo "🚀 Fazendo deploy na Vercel..."
vercel --prod

if [ $? -eq 0 ]; then
    echo "✅ Deploy realizado com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Configure as variáveis de ambiente no painel da Vercel"
    echo "2. Configure o banco de dados (Neon ou Vercel Postgres)"
    echo "3. Atualize a VITE_API_URL no frontend"
    echo "4. Teste a aplicação"
    echo ""
    echo "📖 Consulte DEPLOY.md para instruções detalhadas"
else
    echo "❌ Erro no deploy. Verifique os logs acima."
    exit 1
fi