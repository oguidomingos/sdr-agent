import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import {
  Settings as SettingsIcon,
  Database,
  MessageSquare,
  Bot,
  Shield,
  Webhook,
  Save,
  RefreshCw,
  AlertTriangle,
} from 'lucide-react';

export default function Settings() {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Configurações</h1>
          <p className="text-muted-foreground">
            Gerencie as configurações globais do sistema
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Restaurar Padrões
          </Button>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
            <Save className="mr-2 h-4 w-4" />
            Salvar Alterações
          </Button>
        </div>
      </div>

      <Tabs defaultValue="general" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="general">Geral</TabsTrigger>
          <TabsTrigger value="ai">IA & Modelos</TabsTrigger>
          <TabsTrigger value="integrations">Integrações</TabsTrigger>
          <TabsTrigger value="security">Segurança</TabsTrigger>
          <TabsTrigger value="system">Sistema</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <SettingsIcon className="h-5 w-5" />
                Configurações Gerais
              </CardTitle>
              <CardDescription>
                Configurações básicas da aplicação
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="app_name">Nome da Aplicação</Label>
                  <Input id="app_name" defaultValue="SDR Agent SaaS" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="company_name">Nome da Empresa</Label>
                  <Input id="company_name" defaultValue="Tech Solutions Inc." />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="app_description">Descrição</Label>
                <Textarea 
                  id="app_description" 
                  defaultValue="Sistema multi-tenant para automação de vendas com IA"
                  rows={3}
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="default_timezone">Fuso Horário Padrão</Label>
                  <Select defaultValue="America/Sao_Paulo">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="America/Sao_Paulo">São Paulo (GMT-3)</SelectItem>
                      <SelectItem value="America/New_York">New York (GMT-5)</SelectItem>
                      <SelectItem value="Europe/London">London (GMT+0)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="default_language">Idioma Padrão</Label>
                  <Select defaultValue="pt-BR">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pt-BR">Português (Brasil)</SelectItem>
                      <SelectItem value="en-US">English (US)</SelectItem>
                      <SelectItem value="es-ES">Español</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Configurações de Sessão
              </CardTitle>
              <CardDescription>
                Configurações padrão para sessões de conversa
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="session_timeout">Timeout da Sessão (segundos)</Label>
                  <Input id="session_timeout" type="number" defaultValue="3600" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="max_history">Máximo de Histórico</Label>
                  <Input id="max_history" type="number" defaultValue="50" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="context_window">Janela de Contexto</Label>
                  <Input id="context_window" type="number" defaultValue="20" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ai" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                Configurações de IA
              </CardTitle>
              <CardDescription>
                Configurações dos modelos de inteligência artificial
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="default_gemini_model">Modelo Gemini Padrão</Label>
                  <Select defaultValue="gemini-2.0-flash">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gemini-2.0-flash">Gemini 2.0 Flash</SelectItem>
                      <SelectItem value="gemini-1.5-pro">Gemini 1.5 Pro</SelectItem>
                      <SelectItem value="gemini-1.5-flash">Gemini 1.5 Flash</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="default_temperature">Temperatura Padrão (%)</Label>
                  <Input id="default_temperature" type="number" min="0" max="100" defaultValue="70" />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="default_persona">Persona Padrão do Agente</Label>
                <Textarea 
                  id="default_persona" 
                  defaultValue="Sou um assistente especializado em atendimento, usando a metodologia SPIN Selling para qualificar leads interessados em nossos serviços."
                  rows={4}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="default_welcome">Mensagem de Boas-vindas Padrão</Label>
                <Textarea 
                  id="default_welcome" 
                  defaultValue="Olá! Sou seu assistente virtual. Como posso ajudá-lo hoje?"
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Rate Limiting</CardTitle>
              <CardDescription>
                Configurações de limite de requisições para IA
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="rate_limit_calls">Chamadas por Período</Label>
                  <Input id="rate_limit_calls" type="number" defaultValue="100" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="rate_limit_period">Período (segundos)</Label>
                  <Input id="rate_limit_period" type="number" defaultValue="3600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="integrations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Webhook className="h-5 w-5" />
                Evolution API
              </CardTitle>
              <CardDescription>
                Configurações da integração com WhatsApp
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="evolution_url">URL da API</Label>
                  <Input id="evolution_url" defaultValue="http://localhost:8888" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="evolution_key">Chave da API</Label>
                  <Input id="evolution_key" type="password" defaultValue="••••••••••••••••" />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="default_instance">Instância Padrão</Label>
                <Input id="default_instance" defaultValue="sdr-agent" />
              </div>

              <div className="flex items-center gap-2">
                <Badge variant="default" className="bg-green-500 text-white">Conectado</Badge>
                <span className="text-sm text-muted-foreground">Última verificação: há 2 minutos</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Banco de Dados
              </CardTitle>
              <CardDescription>
                Configurações de conexão com o banco de dados
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="db_host">Host</Label>
                  <Input id="db_host" defaultValue="postgres_sdr" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="db_port">Porta</Label>
                  <Input id="db_port" type="number" defaultValue="5432" />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="db_name">Nome do Banco</Label>
                  <Input id="db_name" defaultValue="sdr_agent" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="db_user">Usuário</Label>
                  <Input id="db_user" defaultValue="sdr_user" />
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Badge variant="default" className="bg-green-500 text-white">Conectado</Badge>
                <span className="text-sm text-muted-foreground">Pool: 10 conexões ativas</span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Configurações de Segurança
              </CardTitle>
              <CardDescription>
                Configurações de autenticação e autorização
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="jwt_expiration">Expiração JWT (horas)</Label>
                  <Input id="jwt_expiration" type="number" defaultValue="24" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="session_duration">Duração da Sessão (horas)</Label>
                  <Input id="session_duration" type="number" defaultValue="8" />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="cors_origins">Origens CORS Permitidas</Label>
                <Textarea 
                  id="cors_origins" 
                  defaultValue="http://localhost:3000,http://127.0.0.1:3000"
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="webhook_secret">Webhook Secret</Label>
                <Input id="webhook_secret" type="password" defaultValue="••••••••••••••••" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Rate Limiting Global</CardTitle>
              <CardDescription>
                Configurações de limite de requisições por IP
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="global_rate_limit">Requisições por Minuto</Label>
                  <Input id="global_rate_limit" type="number" defaultValue="100" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="burst_limit">Limite de Burst</Label>
                  <Input id="burst_limit" type="number" defaultValue="200" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Informações do Sistema</CardTitle>
              <CardDescription>
                Status e informações da aplicação
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <Label className="text-sm font-medium">Versão da Aplicação</Label>
                  <p className="text-sm text-muted-foreground">v1.0.0</p>
                </div>
                <div className="space-y-1">
                  <Label className="text-sm font-medium">Ambiente</Label>
                  <Badge variant="outline">Desenvolvimento</Badge>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <Label className="text-sm font-medium">Tempo de Atividade</Label>
                  <p className="text-sm text-muted-foreground">2 dias, 14 horas</p>
                </div>
                <div className="space-y-1">
                  <Label className="text-sm font-medium">Última Atualização</Label>
                  <p className="text-sm text-muted-foreground">20/01/2024 às 15:30</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-warning" />
                Ações do Sistema
              </CardTitle>
              <CardDescription>
                Ações perigosas que afetam todo o sistema
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border border-orange-200 bg-orange-50 rounded-lg">
                  <div>
                    <h4 className="font-medium text-orange-900">Limpar Cache do Sistema</h4>
                    <p className="text-sm text-orange-700">Remove todos os dados em cache</p>
                  </div>
                  <Button variant="outline" className="border-orange-300 text-orange-700">
                    Limpar Cache
                  </Button>
                </div>

                <div className="flex items-center justify-between p-4 border border-red-200 bg-red-50 rounded-lg">
                  <div>
                    <h4 className="font-medium text-red-900">Reiniciar Aplicação</h4>
                    <p className="text-sm text-red-700">Reinicia todos os serviços</p>
                  </div>
                  <Button variant="outline" className="border-red-300 text-red-700">
                    Reiniciar
                  </Button>
                </div>

                <div className="flex items-center justify-between p-4 border border-red-200 bg-red-50 rounded-lg">
                  <div>
                    <h4 className="font-medium text-red-900">Reset de Configurações</h4>
                    <p className="text-sm text-red-700">Restaura todas as configurações padrão</p>
                  </div>
                  <Button variant="destructive">
                    Reset Total
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}