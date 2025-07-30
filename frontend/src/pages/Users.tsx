import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Input } from '@/components/ui/input';
import {
  Plus,
  Edit,
  Trash2,
  Users as UsersIcon,
  Crown,
  User,
  Mail,
  Calendar,
  Search,
  RefreshCw,
  Shield,
  ShieldCheck,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useState } from 'react';

const mockUsers = [
  {
    id: '1',
    name: 'Admin Principal',
    email: 'admin@sdr-agent.com',
    role: 'admin',
    status: 'active',
    last_login: '2024-01-20T10:30:00Z',
    created_at: '2024-01-01T00:00:00Z',
    avatar: null,
  },
  {
    id: '2',
    name: 'João Silva',
    email: 'joao@empresa.com',
    role: 'manager',
    status: 'active',
    last_login: '2024-01-19T15:45:00Z',
    created_at: '2024-01-05T00:00:00Z',
    avatar: null,
  },
  {
    id: '3',
    name: 'Maria Santos',
    email: 'maria@empresa.com',
    role: 'user',
    status: 'active',
    last_login: '2024-01-18T09:15:00Z',
    created_at: '2024-01-10T00:00:00Z',
    avatar: null,
  },
  {
    id: '4',
    name: 'Pedro Costa',
    email: 'pedro@empresa.com',
    role: 'user',
    status: 'inactive',
    last_login: '2024-01-10T14:20:00Z',
    created_at: '2024-01-12T00:00:00Z',
    avatar: null,
  },
];

const getRoleBadge = (role: string) => {
  switch (role) {
    case 'admin':
      return <Badge variant="default" className="bg-red-500 text-white"><Crown className="mr-1 h-3 w-3" />Admin</Badge>;
    case 'manager':
      return <Badge variant="secondary"><ShieldCheck className="mr-1 h-3 w-3" />Gerente</Badge>;
    case 'user':
      return <Badge variant="outline"><User className="mr-1 h-3 w-3" />Usuário</Badge>;
    default:
      return <Badge variant="outline">{role}</Badge>;
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'active':
      return <Badge variant="default" className="bg-green-500 text-white">Ativo</Badge>;
    case 'inactive':
      return <Badge variant="outline">Inativo</Badge>;
    case 'suspended':
      return <Badge variant="destructive">Suspenso</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
};

export default function Users() {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredUsers = mockUsers.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.role.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Usuários</h1>
          <p className="text-muted-foreground">
            Gerencie os usuários e permissões do sistema
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Atualizar
          </Button>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
            <Plus className="mr-2 h-4 w-4" />
            Novo Usuário
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total de Usuários
            </CardTitle>
            <UsersIcon className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{mockUsers.length}</div>
            <p className="text-xs text-success">+2 este mês</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Usuários Ativos
            </CardTitle>
            <Shield className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {mockUsers.filter(u => u.status === 'active').length}
            </div>
            <p className="text-xs text-muted-foreground">
              {Math.round((mockUsers.filter(u => u.status === 'active').length / mockUsers.length) * 100)}% do total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Administradores
            </CardTitle>
            <Crown className="h-4 w-4 text-warning" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {mockUsers.filter(u => u.role === 'admin').length}
            </div>
            <p className="text-xs text-muted-foreground">Controle total</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Gerentes
            </CardTitle>
            <ShieldCheck className="h-4 w-4 text-accent" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {mockUsers.filter(u => u.role === 'manager').length}
            </div>
            <p className="text-xs text-muted-foreground">Acesso gerencial</p>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar usuários..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Users List */}
      <div className="space-y-4">
        {filteredUsers.length > 0 ? (
          filteredUsers.map((user) => (
            <Card key={user.id} className="border-border hover:bg-muted/50 transition-colors">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={user.avatar || undefined} />
                      <AvatarFallback className="text-sm font-medium">
                        {user.name
                          .split(' ')
                          .map((n) => n[0])
                          .join('')
                          .toUpperCase()
                          .slice(0, 2)}
                      </AvatarFallback>
                    </Avatar>

                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-semibold text-foreground">{user.name}</h3>
                        {getRoleBadge(user.role)}
                        {getStatusBadge(user.status)}
                      </div>

                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Mail className="h-4 w-4" />
                          <span>{user.email}</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          <span>
                            Último login: {formatDistanceToNow(new Date(user.last_login), {
                              addSuffix: true,
                              locale: ptBR,
                            })}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          <span>
                            Criado: {formatDistanceToNow(new Date(user.created_at), {
                              addSuffix: true,
                              locale: ptBR,
                            })}
                          </span>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2 text-xs">
                        <span className="bg-muted px-2 py-1 rounded">
                          Permissões: {user.role === 'admin' ? 'Total' : user.role === 'manager' ? 'Gerencial' : 'Limitada'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    <Button variant="outline" size="sm">
                      <Edit className="mr-2 h-4 w-4" />
                      Editar
                    </Button>
                    {user.role !== 'admin' && (
                      <Button variant="outline" size="sm">
                        <Trash2 className="mr-2 h-4 w-4" />
                        Remover
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <Card className="border-border">
            <CardContent className="p-6 text-center">
              <UsersIcon className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">
                {searchTerm
                  ? `Nenhum usuário encontrado para "${searchTerm}"`
                  : 'Nenhum usuário encontrado'}
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Permissions Info */}
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Níveis de Permissão</CardTitle>
          <CardDescription>Entenda os diferentes níveis de acesso</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <Crown className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-red-900">Administrador</h4>
                <p className="text-sm text-red-700">
                  Acesso total ao sistema, incluindo gerenciamento de usuários, clientes e configurações globais.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <ShieldCheck className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-900">Gerente</h4>
                <p className="text-sm text-blue-700">
                  Pode gerenciar clientes, playbooks e visualizar relatórios. Não pode alterar configurações do sistema.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <User className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-green-900">Usuário</h4>
                <p className="text-sm text-green-700">
                  Acesso limitado para visualizar conversas e relatórios. Não pode fazer alterações no sistema.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}