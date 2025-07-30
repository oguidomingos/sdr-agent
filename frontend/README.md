# SDR Agent Frontend

Frontend moderno e responsivo para o SDR Agent Multi-Tenant SaaS, construído com React, TypeScript, e Tailwind CSS.

## ✨ Funcionalidades

### 🏢 Multi-Tenancy Completo
- **Seletor de Cliente** - Interface intuitiva para alternar entre diferentes clientes
- **Isolamento de Dados** - Cada cliente vê apenas seus próprios dados
- **Gestão Centralizada** - Administração de múltiplos clientes em uma única interface

### 📊 Dashboard Inteligente
- **Métricas em Tempo Real** - Conversas ativas, leads qualificados, taxa de conversão
- **Conversas Recentes** - Lista das últimas interações com leads
- **Ações Rápidas** - Acesso direto às principais funcionalidades

### 👥 Gestão de Clientes
- **CRUD Completo** - Criar, visualizar, editar e remover clientes
- **Configurações Detalhadas** - API Keys, modelos IA, configurações de sessão
- **Status e Métricas** - Acompanhamento do status e estatísticas de cada cliente

### 📝 Gestão de Playbooks
- **Editor de Playbooks** - Interface para criar e editar roteiros de conversação
- **Metodologia SPIN** - Suporte completo à metodologia SPIN Selling
- **Versionamento** - Controle de versões dos playbooks
- **Ativação/Desativação** - Gerenciamento do status dos playbooks

### 💬 Gestão de Conversas
- **Lista de Conversas** - Visualização de todas as conversas por cliente
- **Histórico Completo** - Acesso ao histórico completo de mensagens
- **Score de Leads** - Sistema de pontuação para qualificação de leads
- **Filtros e Busca** - Ferramentas para encontrar conversas específicas

### 📈 Relatórios e Analytics
- **Métricas de Performance** - Taxa de conversão, tempo de resposta, etc.
- **Gráficos Interativos** - Visualização de dados em tempo real
- **Insights Automáticos** - Recomendações baseadas nos dados
- **Exportação** - Possibilidade de exportar relatórios

### 👤 Gestão de Usuários
- **Controle de Acesso** - Sistema de permissões por usuário
- **Diferentes Níveis** - Admin, Gerente, Usuário
- **Auditoria** - Logs de atividades dos usuários

### ⚙️ Configurações
- **Configurações Globais** - Parâmetros do sistema
- **Integrações** - Configuração de APIs externas
- **Segurança** - Configurações de autenticação e autorização

## 🛠️ Tecnologias

- **React 18** - Biblioteca principal
- **TypeScript** - Tipagem estática
- **Vite** - Build tool e dev server
- **Tailwind CSS** - Framework de CSS
- **Shadcn/UI** - Componentes de interface
- **React Query** - Gerenciamento de estado servidor
- **React Router** - Roteamento
- **Axios** - Cliente HTTP
- **Lucide React** - Ícones
- **Date-fns** - Manipulação de datas

## 🚀 Instalação e Configuração

### Pré-requisitos
- Node.js 18+
- npm ou yarn

### Instalação Local

```bash
# Navegar para o diretório do frontend
cd frontend

# Instalar dependências
npm install

# Copiar arquivo de ambiente
cp .env.example .env

# Iniciar em modo desenvolvimento
npm run dev
```

### Usando Docker

```bash
# Construir e executar com docker-compose
docker-compose up frontend

# Ou construir manualmente
cd frontend
docker build -t sdr-frontend .
docker run -p 3000:80 sdr-frontend
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# API Base URL
VITE_API_URL=http://localhost:8000

# Environment
VITE_NODE_ENV=development

# Application Info
VITE_APP_NAME=SDR Agent SaaS
VITE_APP_VERSION=1.0.0

# Feature Flags
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=true
```

### Configuração do Proxy

O frontend está configurado para fazer proxy das requisições `/api/*` para o backend automaticamente.

## 📱 Interface

### Layout Responsivo
- **Desktop First** - Otimizado para desktop com suporte mobile
- **Sidebar Colapsável** - Navegação que se adapta ao tamanho da tela
- **Dark/Light Mode** - Suporte a temas (planejado)

### Componentes Principais

#### Seletor de Cliente
```typescript
// Usado em páginas que precisam de contexto de cliente
import { ClientSelector } from '@/components/ui/ClientSelector';

// Automaticamente aparece no header quando necessário
```

#### Context API
```typescript
// Gerenciamento global do cliente selecionado
import { useClient } from '@/contexts/ClientContext';

const { selectedClient, setSelectedClient, clients } = useClient();
```

### Páginas Principais

1. **Dashboard** (`/`) - Visão geral com métricas
2. **Conversas** (`/conversations`) - Lista de conversas do cliente
3. **Clientes** (`/clients`) - Gestão de clientes
4. **Playbooks** (`/playbooks`) - Gestão de roteiros
5. **Relatórios** (`/reports`) - Analytics e relatórios
6. **Usuários** (`/users`) - Gestão de usuários
7. **Configurações** (`/settings`) - Configurações do sistema

## 🔗 Integração com Backend

### API Endpoints Utilizados

```bash
# Clientes
GET /clients - Lista clientes
POST /clients - Cria cliente
PUT /clients/{id} - Atualiza cliente
DELETE /clients/{id} - Remove cliente

# Playbooks
GET /playbooks?client_id={id} - Lista playbooks
POST /playbooks - Cria playbook
PUT /playbooks/{id} - Atualiza playbook

# Conversas
GET /conversations?client_id={id} - Lista conversas
GET /conversations/{user_id}/messages - Histórico

# Dashboard
GET /dashboard/stats?client_id={id} - Estatísticas
```

### Tratamento de Erros

O frontend possui tratamento robusto de erros com:
- **Toast Notifications** - Para feedback ao usuário
- **Loading States** - Para operações assíncronas
- **Error Boundaries** - Para captura de erros React
- **Retry Logic** - Para requisições falhadas

## 🎨 Customização

### Temas
O sistema usa CSS Custom Properties para facilitar customização:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  /* ... */
}
```

### Componentes
Todos os componentes seguem o padrão Shadcn/UI e podem ser customizados editando os arquivos em `src/components/ui/`.

## 🚀 Deployment

### Produção
```bash
# Build para produção
npm run build

# Preview do build
npm run preview
```

### Docker
```bash
# Build e deploy com Docker
docker build -t sdr-frontend .
docker run -p 80:80 sdr-frontend
```

### Nginx
O frontend inclui configuração Nginx otimizada com:
- **Compressão Gzip**
- **Cache de Assets**
- **Proxy para API**
- **Security Headers**
- **SPA Routing**

## 📈 Performance

### Otimizações Implementadas
- **Code Splitting** - Carregamento sob demanda
- **Tree Shaking** - Remoção de código não usado
- **Asset Optimization** - Compressão de imagens e CSS
- **Lazy Loading** - Componentes carregados quando necessário
- **React Query** - Cache inteligente de dados

### Métricas Alvo
- **First Contentful Paint** < 2s
- **Time to Interactive** < 3s
- **Lighthouse Score** > 90

## 🛡️ Segurança

### Implementações
- **Content Security Policy** - Headers de segurança
- **XSS Protection** - Prevenção de ataques XSS
- **CORS Configuration** - Configuração adequada de CORS
- **Input Validation** - Validação de entrada com Zod

## 🤝 Contribuição

### Estrutura do Projeto
```
frontend/
├── src/
│   ├── components/     # Componentes reutilizáveis
│   ├── pages/         # Páginas da aplicação
│   ├── contexts/      # Context providers
│   ├── hooks/         # Custom hooks
│   ├── lib/          # Utilitários e configurações
│   └── types/        # Definições de tipos TypeScript
├── public/           # Assets estáticos
└── docker/          # Configurações Docker
```

### Padrões de Código
- **TypeScript** - Tipagem forte obrigatória
- **ESLint** - Linting automático
- **Prettier** - Formatação consistente
- **Conventional Commits** - Padrão de commits

## 📝 Roadmap

### Próximas Funcionalidades
- [ ] **Editor Visual de Playbooks** - Interface drag-and-drop
- [ ] **Chat em Tempo Real** - Conversas ao vivo
- [ ] **Automações** - Regras de negócio automatizadas
- [ ] **Integrações** - CRM, WhatsApp Business, etc.
- [ ] **Mobile App** - Aplicativo nativo
- [ ] **Dark Mode** - Tema escuro
- [ ] **Multi-idioma** - Suporte a múltiplos idiomas

### Melhorias Técnicas
- [ ] **PWA** - Progressive Web App
- [ ] **WebSockets** - Comunicação em tempo real
- [ ] **Service Workers** - Cache offline
- [ ] **Performance Monitoring** - Métricas de performance
- [ ] **A/B Testing** - Testes de funcionalidades

---

**Desenvolvido com ❤️ para transformar o atendimento digital**