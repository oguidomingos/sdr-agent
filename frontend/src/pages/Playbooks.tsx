import { useClient } from '@/contexts/ClientContext';
import { useQuery } from '@tanstack/react-query';
import { playbooksApi } from '@/lib/api';
import { NoClientSelected } from '@/components/ui/NoClientSelected';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import {
  Plus,
  Play,
  Pause,
  Edit,
  Copy,
  FileText,
  Calendar,
  User,
  Search,
  RefreshCw,
  Layers,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useState } from 'react';

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'active':
      return <Badge variant="default" className="bg-green-500 text-white">Ativo</Badge>;
    case 'draft':
      return <Badge variant="outline" className="border-yellow-500 text-yellow-700">Rascunho</Badge>;
    case 'archived':
      return <Badge variant="outline" className="border-muted-foreground text-muted-foreground">Arquivado</Badge>;
    default:
      return <Badge variant="outline">Desconhecido</Badge>;
  }
};

export default function Playbooks() {
  const { selectedClient } = useClient();
  const [searchTerm, setSearchTerm] = useState('');

  const { data: playbooksData, isLoading, refetch } = useQuery({
    queryKey: ['playbooks', selectedClient?.id],
    queryFn: () => playbooksApi.getAll(selectedClient?.id, 0, 50),
    enabled: !!selectedClient,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (!selectedClient) {
    return (
      <NoClientSelected
        title="Nenhum cliente selecionado"
        description="Para visualizar os playbooks, você precisa selecionar um cliente primeiro."
        feature="os playbooks"
      />
    );
  }

  const playbooks = playbooksData?.playbooks || [];
  const filteredPlaybooks = playbooks.filter(playbook =>
    playbook.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    playbook.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Playbooks</h1>
          <p className="text-muted-foreground">
            Gerencie os roteiros de conversação de {selectedClient.name}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
            <Plus className="mr-2 h-4 w-4" />
            Novo Playbook
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total de Playbooks
            </CardTitle>
            <FileText className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold text-foreground">{playbooks.length}</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Playbooks Ativos
            </CardTitle>
            <Play className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold text-foreground">
                {playbooks.filter(p => p.status === 'active').length}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Em Desenvolvimento
            </CardTitle>
            <Calendar className="h-4 w-4 text-warning" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold text-foreground">
                {playbooks.filter(p => p.status === 'draft').length}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Playbook Padrão
            </CardTitle>
            <Layers className="h-4 w-4 text-accent" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold text-foreground">
                {playbooks.filter(p => p.is_default).length}
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
            placeholder="Buscar playbooks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Playbooks List */}
      <div className="space-y-4">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="border-border">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-6 w-64" />
                    <Skeleton className="h-4 w-96" />
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-4 w-32" />
                  </div>
                  <div className="flex gap-2">
                    <Skeleton className="h-9 w-20" />
                    <Skeleton className="h-9 w-24" />
                    <Skeleton className="h-9 w-20" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : filteredPlaybooks.length > 0 ? (
          filteredPlaybooks.map((playbook) => (
            <Card key={playbook.id} className="border-border">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-foreground">{playbook.name}</h3>
                      {getStatusBadge(playbook.status)}
                      {playbook.is_default && (
                        <Badge variant="outline" className="border-blue-500 text-blue-700">
                          Padrão
                        </Badge>
                      )}
                    </div>
                    
                    {playbook.description && (
                      <p className="text-muted-foreground">{playbook.description}</p>
                    )}

                    <div className="flex items-center gap-6 text-sm text-muted-foreground">
                      <span>{playbook.steps?.length || 0} etapas</span>
                      <span>Versão {playbook.version}</span>
                      <span>Cliente: {selectedClient.name}</span>
                    </div>

                    <div className="space-y-2">
                      {playbook.situation_prompts && playbook.situation_prompts.length > 0 && (
                        <div className="text-xs">
                          <span className="font-medium text-muted-foreground">Prompts SPIN:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            <Badge variant="outline" className="text-xs">
                              Situação ({playbook.situation_prompts.length})
                            </Badge>
                            {playbook.problem_prompts && (
                              <Badge variant="outline" className="text-xs">
                                Problema ({playbook.problem_prompts.length})
                              </Badge>
                            )}
                            {playbook.implication_prompts && (
                              <Badge variant="outline" className="text-xs">
                                Implicação ({playbook.implication_prompts.length})
                              </Badge>
                            )}
                            {playbook.need_payoff_prompts && (
                              <Badge variant="outline" className="text-xs">
                                Necessidade ({playbook.need_payoff_prompts.length})
                              </Badge>
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span>
                        Atualizado {formatDistanceToNow(new Date(playbook.updated_at), {
                          addSuffix: true,
                          locale: ptBR,
                        })}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {playbook.status === 'active' ? (
                      <Button variant="outline" size="sm">
                        <Pause className="mr-2 h-4 w-4" />
                        Pausar
                      </Button>
                    ) : (
                      <Button variant="outline" size="sm">
                        <Play className="mr-2 h-4 w-4" />
                        Ativar
                      </Button>
                    )}

                    <Button variant="outline" size="sm">
                      <Copy className="mr-2 h-4 w-4" />
                      Duplicar
                    </Button>

                    <Button size="sm" className="bg-primary text-primary-foreground hover:bg-primary/90">
                      <Edit className="mr-2 h-4 w-4" />
                      Editar
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <Card className="border-border">
            <CardContent className="p-6 text-center">
              <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">
                {searchTerm
                  ? `Nenhum playbook encontrado para "${searchTerm}"`
                  : `Nenhum playbook encontrado para ${selectedClient.name}`}
              </p>
              <Button className="mt-4 bg-primary text-primary-foreground hover:bg-primary/90">
                <Plus className="mr-2 h-4 w-4" />
                Criar primeiro playbook
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}