import { useState, useEffect } from 'react';
import { Client, ClientCreateData, ClientUpdateData } from '@/types/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, Save, X, Zap } from 'lucide-react';

interface ClientFormProps {
  client?: Client;
  onSubmit: (data: ClientCreateData | ClientUpdateData) => Promise<void>;
  onCancel: () => void;
}

// Utility functions for auto-configuration
const generateEvolutionConfig = (clientName: string) => {
  const sanitizedName = clientName
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
    
  return {
    evolution_api_url: 'http://host.docker.internal:8888',
    evolution_api_key: 'B6D711FCDE4D4FD5936544120E713976',
    evolution_instance: sanitizedName || 'cliente',
    gemini_api_key: 'AIzaSyASsQw-arw3Mqp7q01qy37Wxkrj-Lo0oHk',
  };
};

const generateDomainFromName = (clientName: string) => {
  const sanitizedName = clientName
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')
    .replace(/\s+/g, '');
  return `${sanitizedName}.sdr-agent.com`;
};

export default function ClientForm({ client, onSubmit, onCancel }: ClientFormProps) {
  const isEditing = !!client;
  
  const [formData, setFormData] = useState<ClientCreateData>({
    name: client?.name || '',
    description: client?.description || '',
    domain: client?.domain || '',
    whatsapp_number: client?.whatsapp_number || '',
    evolution_api_url: client?.evolution_api_url || 'http://host.docker.internal:8888',
    evolution_api_key: client?.evolution_api_key || 'B6D711FCDE4D4FD5936544120E713976',
    evolution_instance: client?.evolution_instance || '',
    gemini_api_key: client?.gemini_api_key || 'AIzaSyASsQw-arw3Mqp7q01qy37Wxkrj-Lo0oHk',
    gemini_model: client?.gemini_model || 'gemini-2.0-flash',
    session_timeout: client?.session_timeout || 3600,
    max_history: client?.max_history || 50,
    context_window_size: client?.context_window_size || 20,
    agent_name: client?.agent_name || 'SDR Assistant',
    agent_persona: client?.agent_persona || '',
    welcome_message: client?.welcome_message || 'Olá! Como posso ajudá-lo hoje?',
    logo_url: client?.logo_url || '',
    contact_email: client?.contact_email || '',
    contact_phone: client?.contact_phone || '',
    business_hours: client?.business_hours || {},
    timezone: client?.timezone || 'America/Sao_Paulo',
    ai_temperature: client?.ai_temperature || 0.7,
    rate_limit_enabled: client?.rate_limit_enabled ?? true,
    rate_limit_calls: client?.rate_limit_calls || 100,
    rate_limit_period: client?.rate_limit_period || 3600,
    create_default_playbook: !isEditing,
    register_webhook: false,
    batch_enabled: true,
    batch_window_seconds: 180,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoConfigured, setAutoConfigured] = useState(false);

  // Auto-configure Evolution API settings when client name changes (for new clients only)
  useEffect(() => {
    if (!isEditing && formData.name && formData.name.length > 2) {
      const evolutionConfig = generateEvolutionConfig(formData.name);
      const domain = generateDomainFromName(formData.name);
      
      setFormData(prev => ({
        ...prev,
        domain: prev.domain || domain,
        ...evolutionConfig,
      }));
      
      setAutoConfigured(true);
      
      // Reset after a short delay
      setTimeout(() => setAutoConfigured(false), 2000);
    }
  }, [formData.name, isEditing]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Validate required fields
    if (!formData.name.trim()) {
      setError('Nome do cliente é obrigatório');
      setLoading(false);
      return;
    }

    if (!formData.whatsapp_number.trim()) {
      setError('Número do WhatsApp é obrigatório');
      setLoading(false);
      return;
    }

    try {
      if (isEditing && client) {
        const updateData: ClientUpdateData = { 
          ...formData,
          // Convert temperature from 0-1 range to 0-100 range
          ai_temperature: Math.round(formData.ai_temperature * 100)
        };
        delete updateData.create_default_playbook; // Not needed for updates
        await onSubmit(updateData);
      } else {
        const createData: ClientCreateData = {
          ...formData,
          // Convert temperature from 0-1 range to 0-100 range
          ai_temperature: Math.round(formData.ai_temperature * 100),
          // Ensure required fields are set
          batch_enabled: formData.batch_enabled,
          batch_window_seconds: formData.batch_window_seconds,
          // Add agent_prompt field that maps to agent_persona
          agent_prompt: formData.agent_persona || 'Você é um assistente comercial especializado.'
        };
        await onSubmit(createData);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Erro ao salvar cliente. Tente novamente.';
      setError(errorMessage);
      console.error('Client creation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (name: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAutoConfig = () => {
    if (formData.name) {
      const evolutionConfig = generateEvolutionConfig(formData.name);
      const domain = generateDomainFromName(formData.name);
      
      setFormData(prev => ({
        ...prev,
        domain,
        ...evolutionConfig,
      }));
      
      setAutoConfigured(true);
      setTimeout(() => setAutoConfigured(false), 2000);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {autoConfigured && (
        <Alert>
          <Zap className="h-4 w-4" />
          <AlertDescription>
            ✨ Configurações da Evolution API preenchidas automaticamente!
          </AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="basic">Básico</TabsTrigger>
          <TabsTrigger value="apis">APIs</TabsTrigger>
          <TabsTrigger value="agent">Agente</TabsTrigger>
          <TabsTrigger value="advanced">Avançado</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Informações Básicas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nome *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => handleChange('name', e.target.value)}
                    placeholder="Nome do cliente"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="domain">Domínio *</Label>
                  <Input
                    id="domain"
                    value={formData.domain}
                    onChange={(e) => handleChange('domain', e.target.value)}
                    placeholder="exemplo.com"
                    required
                    className={autoConfigured ? "border-green-300 bg-green-50" : ""}
                  />
                  {!isEditing && (
                    <p className="text-xs text-muted-foreground">
                      💡 O domínio será gerado automaticamente baseado no nome do cliente
                    </p>
                  )}
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Descrição</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  placeholder="Descrição do cliente"
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="whatsapp_number">Número do WhatsApp *</Label>
                <Input
                  id="whatsapp_number"
                  value={formData.whatsapp_number}
                  onChange={(e) => handleChange('whatsapp_number', e.target.value)}
                  placeholder="+5511999999999"
                  required
                />
                <p className="text-xs text-muted-foreground">
                  ⚠️ Este número deve ser exatamente o mesmo que será conectado no WhatsApp
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="contact_email">Email de Contato</Label>
                  <Input
                    id="contact_email"
                    type="email"
                    value={formData.contact_email}
                    onChange={(e) => handleChange('contact_email', e.target.value)}
                    placeholder="contato@empresa.com"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="contact_phone">Telefone de Contato</Label>
                  <Input
                    id="contact_phone"
                    value={formData.contact_phone}
                    onChange={(e) => handleChange('contact_phone', e.target.value)}
                    placeholder="+55 11 99999-9999"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="logo_url">URL do Logo</Label>
                <Input
                  id="logo_url"
                  value={formData.logo_url}
                  onChange={(e) => handleChange('logo_url', e.target.value)}
                  placeholder="https://exemplo.com/logo.png"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="apis" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle>Configurações de API</CardTitle>
              {!isEditing && formData.name && (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAutoConfig}
                  className="ml-auto"
                >
                  <Zap className="mr-2 h-4 w-4" />
                  Auto-configurar
                </Button>
              )}
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="evolution_api_url">Evolution API URL *</Label>
                <Input
                  id="evolution_api_url"
                  value={formData.evolution_api_url}
                  onChange={(e) => handleChange('evolution_api_url', e.target.value)}
                  placeholder="https://evolution-api.example.com"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="evolution_api_key">Evolution API Key *</Label>
                  <Input
                    id="evolution_api_key"
                    type="password"
                    value={formData.evolution_api_key}
                    onChange={(e) => handleChange('evolution_api_key', e.target.value)}
                    placeholder="sua-api-key"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="evolution_instance">Evolution Instance</Label>
                  <Input
                    id="evolution_instance"
                    value={formData.evolution_instance}
                    onChange={(e) => handleChange('evolution_instance', e.target.value)}
                    placeholder="instance-name"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="gemini_api_key">Gemini API Key *</Label>
                  <Input
                    id="gemini_api_key"
                    type="password"
                    value={formData.gemini_api_key}
                    onChange={(e) => handleChange('gemini_api_key', e.target.value)}
                    placeholder="sua-gemini-api-key"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="gemini_model">Modelo Gemini</Label>
                  <Select
                    value={formData.gemini_model}
                    onValueChange={(value) => handleChange('gemini_model', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gemini-2.0-flash">gemini-2.0-flash</SelectItem>
                      <SelectItem value="gemini-1.5-pro">gemini-1.5-pro</SelectItem>
                      <SelectItem value="gemini-1.5-flash">gemini-1.5-flash</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="agent" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configurações do Agente</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="agent_name">Nome do Agente</Label>
                <Input
                  id="agent_name"
                  value={formData.agent_name}
                  onChange={(e) => handleChange('agent_name', e.target.value)}
                  placeholder="SDR Assistant"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="agent_persona">Persona do Agente</Label>
                <Textarea
                  id="agent_persona"
                  value={formData.agent_persona}
                  onChange={(e) => handleChange('agent_persona', e.target.value)}
                  placeholder="Descreva a personalidade e comportamento do agente"
                  rows={4}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="welcome_message">Mensagem de Boas-vindas</Label>
                <Textarea
                  id="welcome_message"
                  value={formData.welcome_message}
                  onChange={(e) => handleChange('welcome_message', e.target.value)}
                  placeholder="Olá! Como posso ajudá-lo hoje?"
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="ai_temperature">Temperatura da IA ({Math.round(formData.ai_temperature * 100)}%)</Label>
                <Input
                  id="ai_temperature"
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={formData.ai_temperature}
                  onChange={(e) => handleChange('ai_temperature', parseFloat(e.target.value))}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configurações Avançadas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="session_timeout">Timeout da Sessão (s)</Label>
                  <Input
                    id="session_timeout"
                    type="number"
                    value={formData.session_timeout}
                    onChange={(e) => handleChange('session_timeout', parseInt(e.target.value))}
                    min="300"
                    max="86400"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="max_history">Máximo Histórico</Label>
                  <Input
                    id="max_history"
                    type="number"
                    value={formData.max_history}
                    onChange={(e) => handleChange('max_history', parseInt(e.target.value))}
                    min="10"
                    max="200"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="context_window_size">Janela de Contexto</Label>
                  <Input
                    id="context_window_size"
                    type="number"
                    value={formData.context_window_size}
                    onChange={(e) => handleChange('context_window_size', parseInt(e.target.value))}
                    min="5"
                    max="50"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Rate Limiting</Label>
                    <div className="text-sm text-muted-foreground">
                      Ativar limitação de taxa para este cliente
                    </div>
                  </div>
                  <Switch
                    checked={formData.rate_limit_enabled}
                    onCheckedChange={(checked) => handleChange('rate_limit_enabled', checked)}
                  />
                </div>

                {formData.rate_limit_enabled && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="rate_limit_calls">Limite de Chamadas</Label>
                      <Input
                        id="rate_limit_calls"
                        type="number"
                        value={formData.rate_limit_calls}
                        onChange={(e) => handleChange('rate_limit_calls', parseInt(e.target.value))}
                        min="1"
                        max="10000"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="rate_limit_period">Período (segundos)</Label>
                      <Input
                        id="rate_limit_period"
                        type="number"
                        value={formData.rate_limit_period}
                        onChange={(e) => handleChange('rate_limit_period', parseInt(e.target.value))}
                        min="60"
                        max="86400"
                      />
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="timezone">Fuso Horário</Label>
                <Select
                  value={formData.timezone}
                  onValueChange={(value) => handleChange('timezone', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="America/Sao_Paulo">América/São Paulo</SelectItem>
                    <SelectItem value="America/New_York">América/Nova York</SelectItem>
                    <SelectItem value="Europe/London">Europa/Londres</SelectItem>
                    <SelectItem value="UTC">UTC</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {!isEditing && (
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Criar Playbook Padrão</Label>
                    <div className="text-sm text-muted-foreground">
                      Criar automaticamente um playbook inicial para este cliente
                    </div>
                  </div>
                  <Switch
                    checked={formData.create_default_playbook}
                    onCheckedChange={(checked) => handleChange('create_default_playbook', checked)}
                  />
                </div>
              )}

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Registrar Webhook</Label>
                  <div className="text-sm text-muted-foreground">
                    Configurar webhook automaticamente após salvar
                  </div>
                </div>
                <Switch
                  checked={formData.register_webhook}
                  onCheckedChange={(checked) => handleChange('register_webhook', checked)}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="flex items-center justify-end gap-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          <X className="mr-2 h-4 w-4" />
          Cancelar
        </Button>
        <Button type="submit" disabled={loading}>
          <Save className="mr-2 h-4 w-4" />
          {loading ? 'Salvando...' : isEditing ? 'Atualizar' : 'Criar Cliente'}
        </Button>
      </div>
    </form>
  );
}