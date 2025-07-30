import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { clientsApi } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import {
  Plus,
  Edit,
  Trash2,
  Building2,
  Globe,
  Mail,
  Phone,
  Clock,
  Activity,
  Search,
  MoreHorizontal,
} from 'lucide-react';
import { Client, ClientCreateData } from '@/types/api';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'active':
      return <Badge variant="default" className="bg-green-500 text-white">Ativo</Badge>;
    case 'trial':
      return <Badge variant="secondary">Trial</Badge>;
    case 'inactive':
      return <Badge variant="outline">Inativo</Badge>;
    case 'suspended':
      return <Badge variant="destructive">Suspenso</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
};

const ClientCard = ({ client }: { client: Client }) => {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: clientsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      toast({
        title: 'Cliente removido',
        description: `${client.name} foi removido com sucesso.`,
      });
    },
    onError: () => {
      toast({
        title: 'Erro ao remover cliente',
        description: 'Não foi possível remover o cliente. Tente novamente.',
        variant: 'destructive',
      });
    },
  });

  return (
    <Card className="border-border hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4 flex-1">
            <Avatar className="h-12 w-12">
              <AvatarImage src={client.logo_url} />
              <AvatarFallback className="text-sm font-medium">
                {client.name
                  .split(' ')
                  .map((n) => n[0])
                  .join('')
                  .toUpperCase()
                  .slice(0, 2)}
              </AvatarFallback>
            </Avatar>
            
            <div className="flex-1 space-y-2">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold text-foreground">{client.name}</h3>
                {getStatusBadge(client.status)}
              </div>
              
              {client.description && (
                <p className="text-muted-foreground text-sm">{client.description}</p>
              )}
              
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Globe className="h-4 w-4" />
                  <span>{client.domain}</span>
                </div>
                {client.contact_email && (
                  <div className="flex items-center gap-1">
                    <Mail className="h-4 w-4" />
                    <span>{client.contact_email}</span>
                  </div>
                )}
                {client.contact_phone && (
                  <div className="flex items-center gap-1">
                    <Phone className="h-4 w-4" />
                    <span>{client.contact_phone}</span>
                  </div>
                )}
              </div>
              
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  <span>
                    Criado {formatDistanceToNow(new Date(client.created_at), {
                      addSuffix: true,
                      locale: ptBR,
                    })}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <Activity className="h-3 w-3" />
                  <span>
                    Atualizado {formatDistanceToNow(new Date(client.updated_at), {
                      addSuffix: true,
                      locale: ptBR,
                    })}
                  </span>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-2 text-xs">
                <span className="bg-muted px-2 py-1 rounded">
                  Modelo: {client.gemini_model || 'Padrão'}
                </span>
                <span className="bg-muted px-2 py-1 rounded">
                  Timeout: {client.session_timeout}s
                </span>
                <span className="bg-muted px-2 py-1 rounded">
                  Histórico: {client.max_history}
                </span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2 ml-4">
            <Button variant="outline" size="sm">
              <Edit className="mr-2 h-4 w-4" />
              Editar
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => deleteMutation.mutate(client.id)}
              disabled={deleteMutation.isPending}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              {deleteMutation.isPending ? 'Removendo...' : 'Remover'}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const CreateClientDialog = () => {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState<Partial<ClientCreateData>>({
    name: '',
    description: '',
    domain: '',
    agent_name: 'SDR Assistant',
    gemini_model: 'gemini-2.0-flash',
    session_timeout: 3600,
    max_history: 50,
    context_window_size: 20,
    ai_temperature: 70,
    rate_limit_enabled: true,
    rate_limit_calls: 100,
    rate_limit_period: 3600,
    create_default_playbook: true,
  });
  
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: clientsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      setOpen(false);
      setFormData({
        name: '',
        description: '',
        domain: '',
        agent_name: 'SDR Assistant',
        gemini_model: 'gemini-2.0-flash',
        session_timeout: 3600,
        max_history: 50,
        context_window_size: 20,
        ai_temperature: 70,
        rate_limit_enabled: true,
        rate_limit_calls: 100,
        rate_limit_period: 3600,
        create_default_playbook: true,
      });
      toast({
        title: 'Cliente criado',
        description: `${formData.name} foi criado com sucesso.`,
      });
    },
    onError: () => {
      toast({
        title: 'Erro ao criar cliente',
        description: 'Não foi possível criar o cliente. Verifique os dados e tente novamente.',
        variant: 'destructive',
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.domain) {
      toast({
        title: 'Campos obrigatórios',
        description: 'Nome e domínio são obrigatórios.',
        variant: 'destructive',
      });
      return;
    }
    createMutation.mutate(formData as ClientCreateData);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
          <Plus className="mr-2 h-4 w-4" />
          Novo Cliente
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Criar Novo Cliente</DialogTitle>
          <DialogDescription>
            Preencha as informações do cliente. Um playbook padrão será criado automaticamente.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nome *</Label>
              <Input
                id="name"
                value={formData.name || ''}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Nome do cliente"
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="domain">Domínio *</Label>
              <Input
                id="domain"
                value={formData.domain || ''}
                onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                placeholder="exemplo.com"
                required
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="description">Descrição</Label>
            <Textarea
              id="description"
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Descrição do cliente e seu negócio"
              rows={3}
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="agent_name">Nome do Agente</Label>
              <Input
                id="agent_name"
                value={formData.agent_name || ''}
                onChange={(e) => setFormData({ ...formData, agent_name: e.target.value })}
                placeholder="SDR Assistant"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="gemini_model">Modelo Gemini</Label>
              <Select
                value={formData.gemini_model || ''}
                onValueChange={(value) => setFormData({ ...formData, gemini_model: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecionar modelo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gemini-2.0-flash">Gemini 2.0 Flash</SelectItem>
                  <SelectItem value="gemini-1.5-pro">Gemini 1.5 Pro</SelectItem>
                  <SelectItem value="gemini-1.5-flash">Gemini 1.5 Flash</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="session_timeout">Timeout da Sessão (s)</Label>
              <Input
                id="session_timeout"
                type="number"
                value={formData.session_timeout || ''}
                onChange={(e) => setFormData({ ...formData, session_timeout: parseInt(e.target.value) || 3600 })}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="max_history">Máx Histórico</Label>
              <Input
                id="max_history"
                type="number"
                value={formData.max_history || ''}
                onChange={(e) => setFormData({ ...formData, max_history: parseInt(e.target.value) || 50 })}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="ai_temperature">Temperatura IA (%)</Label>
              <Input
                id="ai_temperature"
                type="number"
                min="0"
                max="100"
                value={formData.ai_temperature || ''}
                onChange={(e) => setFormData({ ...formData, ai_temperature: parseInt(e.target.value) || 70 })}
              />
            </div>
          </div>
          
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Criando...' : 'Criar Cliente'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default function Clients() {
  const [searchTerm, setSearchTerm] = useState('');
  
  const { data: clientsResponse, isLoading, error } = useQuery({
    queryKey: ['clients'],
    queryFn: () => clientsApi.getAll(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const clients = clientsResponse?.clients || [];
  const filteredClients = clients.filter(client =>
    client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    client.domain.toLowerCase().includes(searchTerm.toLowerCase()) ||
    client.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (error) {
    return (
      <div className="p-6">
        <Card className="border-destructive">
          <CardContent className="p-6 text-center">
            <h3 className="text-lg font-semibold text-destructive mb-2">Erro ao carregar clientes</h3>
            <p className="text-muted-foreground">
              Não foi possível carregar a lista de clientes. Verifique sua conexão e tente novamente.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Clientes</h1>
          <p className="text-muted-foreground">
            Gerencie todos os clientes do sistema multi-tenant
          </p>
        </div>
        <CreateClientDialog />
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total de Clientes
            </CardTitle>
            <Building2 className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold text-foreground">{clients.length}</div>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Clientes Ativos
            </CardTitle>
            <Activity className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold text-foreground">
                {clients.filter(c => c.status === 'active').length}
              </div>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Em Trial
            </CardTitle>
            <Clock className="h-4 w-4 text-warning" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold text-foreground">
                {clients.filter(c => c.status === 'trial').length}
              </div>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Suspensos
            </CardTitle>
            <AlertCircle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold text-foreground">
                {clients.filter(c => c.status === 'suspended').length}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar clientes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Clients List */}
      <div className="space-y-4">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="border-border">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <Skeleton className="h-12 w-12 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-96" />
                    <Skeleton className="h-4 w-64" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : filteredClients.length > 0 ? (
          filteredClients.map((client) => (
            <ClientCard key={client.id} client={client} />
          ))
        ) : (
          <Card className="border-border">
            <CardContent className="p-6 text-center">
              <Building2 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">
                {searchTerm
                  ? `Nenhum cliente encontrado para "${searchTerm}"`
                  : 'Nenhum cliente encontrado'}
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}