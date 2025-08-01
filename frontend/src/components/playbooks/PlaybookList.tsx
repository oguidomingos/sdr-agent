import { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import {
  Plus,
  Play,
  Pause,
  Edit,
  Copy,
  Trash2,
  FileText,
  Search,
  MoreHorizontal,
} from 'lucide-react';

import { Playbook } from '@/types/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface PlaybookListProps {
  playbooks: Playbook[];
  isLoading: boolean;
  onCreateNew: () => void;
  onEdit: (playbook: Playbook) => void;
  onActivate: (playbook: Playbook) => void;
  onDeactivate: (playbook: Playbook) => void;
  onDuplicate: (playbook: Playbook) => void;
  onDelete: (playbook: Playbook) => void;
  isActivating?: boolean;
  isDeactivating?: boolean;
  isDuplicating?: boolean;
  isDeleting?: boolean;
}

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'active':
      return <Badge variant="default" className="bg-green-500 text-white">Ativo</Badge>;
    case 'draft':
      return <Badge variant="outline" className="border-yellow-500 text-yellow-700">Rascunho</Badge>;
    case 'archived':
      return <Badge variant="outline" className="border-gray-500 text-gray-700">Arquivado</Badge>;
    default:
      return <Badge variant="outline">Desconhecido</Badge>;
  }
};

export function PlaybookList({
  playbooks,
  isLoading,
  onCreateNew,
  onEdit,
  onActivate,
  onDeactivate,
  onDuplicate,
  onDelete,
  isActivating = false,
  isDeactivating = false,
  isDuplicating = false,
  isDeleting = false,
}: PlaybookListProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredPlaybooks = playbooks.filter(playbook =>
    playbook.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    playbook.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="space-y-4">
        {/* Header Skeleton */}
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-64" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>

        {/* Search Skeleton */}
        <Skeleton className="h-10 w-full max-w-sm" />

        {/* Table Skeleton */}
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-2">
                    <Skeleton className="h-5 w-48" />
                    <Skeleton className="h-4 w-64" />
                    <Skeleton className="h-4 w-32" />
                  </div>
                  <div className="space-y-2">
                    <Skeleton className="h-6 w-16" />
                    <Skeleton className="h-8 w-24" />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Playbooks</h2>
          <p className="text-muted-foreground">
            Gerencie os roteiros de conversação para qualificação de leads
          </p>
        </div>
        <Button onClick={onCreateNew} className="bg-primary text-primary-foreground hover:bg-primary/90">
          <Plus className="mr-2 h-4 w-4" />
          Novo Playbook
        </Button>
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

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total de Playbooks
            </CardTitle>
            <FileText className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{playbooks.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Playbooks Ativos
            </CardTitle>
            <Play className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {playbooks.filter(p => p.status === 'active').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Em Desenvolvimento
            </CardTitle>
            <Edit className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {playbooks.filter(p => p.status === 'draft').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Playbook Padrão
            </CardTitle>
            <FileText className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {playbooks.filter(p => p.is_default).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Playbooks Table */}
      <Card>
        <CardHeader>
          <CardTitle>Playbooks ({filteredPlaybooks.length})</CardTitle>
          <CardDescription>
            Lista de todos os playbooks disponíveis
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredPlaybooks.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground mb-4">
                {searchTerm
                  ? `Nenhum playbook encontrado para "${searchTerm}"`
                  : 'Nenhum playbook encontrado'}
              </p>
              {!searchTerm && (
                <Button onClick={onCreateNew}>
                  <Plus className="mr-2 h-4 w-4" />
                  Criar primeiro playbook
                </Button>
              )}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Versão</TableHead>
                  <TableHead>Etapas</TableHead>
                  <TableHead>Atualizado</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredPlaybooks.map((playbook) => (
                  <TableRow key={playbook.id}>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{playbook.name}</span>
                          {playbook.is_default && (
                            <Badge variant="outline" className="border-blue-500 text-blue-700 text-xs">
                              Padrão
                            </Badge>
                          )}
                        </div>
                        {playbook.description && (
                          <p className="text-sm text-muted-foreground">
                            {playbook.description}
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(playbook.status)}
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">v{playbook.version}</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">{playbook.steps?.length || 0} etapas</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm text-muted-foreground">
                        {formatDistanceToNow(new Date(playbook.updated_at), {
                          addSuffix: true,
                          locale: ptBR,
                        })}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        {playbook.status === 'active' ? (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onDeactivate(playbook)}
                            disabled={isDeactivating}
                          >
                            <Pause className="mr-1 h-3 w-3" />
                            Pausar
                          </Button>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onActivate(playbook)}
                            disabled={isActivating}
                          >
                            <Play className="mr-1 h-3 w-3" />
                            Ativar
                          </Button>
                        )}

                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => onEdit(playbook)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Editar
                            </DropdownMenuItem>
                            <DropdownMenuItem 
                              onClick={() => onDuplicate(playbook)}
                              disabled={isDuplicating}
                            >
                              <Copy className="mr-2 h-4 w-4" />
                              Duplicar
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              onClick={() => onDelete(playbook)}
                              disabled={isDeleting || playbook.is_default}
                              className="text-destructive"
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Excluir
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}