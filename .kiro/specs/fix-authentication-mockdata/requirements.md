# Requirements Document - Fix Authentication Mock Data

## Introduction

O sistema atualmente possui um problema crítico onde a API de autenticação retorna dados mockados/hardcoded ao invés dos dados reais do usuário logado. Mesmo após um login bem-sucedido com credenciais válidas, o endpoint `/auth/me` retorna "Demo User" e "user@example.com" ao invés dos dados reais do usuário. Esta funcionalidade precisa ser corrigida para conectar corretamente com o banco de dados Supabase e fazer um novo deploy funcional.

## Requirements

### Requirement 1: Corrigir Endpoint de Autenticação

**User Story:** Como um usuário autenticado, eu quero que meus dados reais sejam exibidos no sistema, para que eu possa ver minha identidade correta ao invés de dados demo.

#### Acceptance Criteria

1. WHEN um usuário faz login com credenciais válidas THEN o sistema SHALL retornar um token JWT válido
2. WHEN o sistema recebe uma requisição para `/auth/me` com token válido THEN o sistema SHALL consultar o banco de dados Supabase para obter os dados reais do usuário
3. WHEN os dados do usuário são obtidos do banco THEN o sistema SHALL retornar o nome real, email real e informações corretas do usuário
4. WHEN o frontend recebe os dados reais do usuário THEN o sistema SHALL exibir o nome correto no header e sidebar ao invés de "Demo User"

### Requirement 2: Remover Implementações Mockadas

**User Story:** Como desenvolvedor, eu quero remover todas as implementações mockadas da API, para que o sistema use apenas dados reais do banco de dados.

#### Acceptance Criteria

1. WHEN a API é analisada THEN o sistema SHALL identificar todos os endpoints que retornam dados mockados
2. WHEN dados mockados são encontrados THEN o sistema SHALL substituí-los por consultas reais ao banco Supabase
3. WHEN o endpoint `/auth/me` é chamado THEN o sistema SHALL consultar a tabela `users` no Supabase usando o user_id do token JWT
4. WHEN outros endpoints são chamados THEN o sistema SHALL usar apenas dados reais do banco de dados

### Requirement 3: Validar Conexão com Supabase

**User Story:** Como administrador do sistema, eu quero garantir que a API está conectada corretamente ao Supabase, para que todos os dados sejam persistidos e recuperados corretamente.

#### Acceptance Criteria

1. WHEN a API inicia THEN o sistema SHALL validar a conexão com o Supabase usando as credenciais corretas
2. WHEN uma operação de banco é executada THEN o sistema SHALL usar as variáveis de ambiente SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY
3. WHEN há erro de conexão THEN o sistema SHALL retornar erro 500 com mensagem clara ao invés de dados mockados
4. WHEN a conexão está funcionando THEN o sistema SHALL executar operações CRUD reais no banco

### Requirement 4: Fazer Deploy Funcional

**User Story:** Como usuário final, eu quero acessar uma aplicação funcionando corretamente na Vercel, para que eu possa usar o sistema com meus dados reais.

#### Acceptance Criteria

1. WHEN o código é corrigido THEN o sistema SHALL fazer deploy na Vercel com todas as correções
2. WHEN o deploy é concluído THEN o sistema SHALL fornecer uma URL funcional para acesso
3. WHEN um usuário acessa a URL THEN o sistema SHALL permitir login e exibir dados reais
4. WHEN o usuário faz login THEN o sistema SHALL exibir "Guigo Domingos" e "oguigodomingos@gmail.com" ao invés de dados demo

### Requirement 5: Testar Funcionalidade Completa

**User Story:** Como usuário, eu quero que todas as funcionalidades do sistema funcionem corretamente após o login, para que eu possa gerenciar clientes e usar todas as features.

#### Acceptance Criteria

1. WHEN o usuário faz login THEN o sistema SHALL exibir o dashboard com dados reais do usuário
2. WHEN o usuário acessa a lista de clientes THEN o sistema SHALL mostrar apenas os clientes pertencentes ao usuário logado
3. WHEN o usuário cria um novo cliente THEN o sistema SHALL associar o cliente ao usuário correto no banco
4. WHEN o usuário faz logout THEN o sistema SHALL limpar a sessão e redirecionar para login

### Requirement 6: Configurar Variáveis de Ambiente

**User Story:** Como desenvolvedor, eu quero que todas as variáveis de ambiente estejam configuradas corretamente, para que a aplicação funcione em produção.

#### Acceptance Criteria

1. WHEN o deploy é feito THEN o sistema SHALL ter todas as variáveis do Supabase configuradas
2. WHEN a aplicação inicia THEN o sistema SHALL validar a presença de SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY e JWT_SECRET
3. WHEN variáveis estão ausentes THEN o sistema SHALL falhar com erro claro ao invés de usar dados mockados
4. WHEN CORS é configurado THEN o sistema SHALL permitir requisições do frontend para a API