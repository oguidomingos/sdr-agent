import { useClientContext } from '@/contexts/ClientContext';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi, conversationsApi } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Skeleton } from '@/components/ui/skeleton';
import {
  MessageSquare,
  Users,
  Calendar,
  TrendingUp,
  Phone,
  Clock,
  CheckCircle,
  AlertCircle,
  User,
  RefreshCw,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

const MetricCard = ({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  color,
  isLoading = false 
}: {
  title: string;
  value: string | number;
  change?: string;
  icon: any;
  color: string;
  isLoading?: boolean;
}) => (
  <Card className="border-border">
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium text-muted-foreground">
        {title}
      </CardTitle>
      <Icon className={`h-4 w-4 ${color}`} />
    </CardHeader>
    <CardContent>
      {isLoading ? (
        <div className="space-y-2">
          <Skeleton className="h-8 w-16" />
          <Skeleton className="h-4 w-24" />
        </div>
      ) : (
        <>
          <div className="text-2xl font-bold text-foreground">{value}</div>
          {change && (
            <p className="text-xs text-success font-medium">
              {change} em relação ao mês passado
            </p>
          )}
        </>
      )}
    </CardContent>
  </Card>
);

const getStatusBadge = (status?: string) => {
  switch (status) {
    case 'qualified':
      return <Badge variant="secondary" className="bg-green-100 text-green-800">Qualificado</Badge>;
    case 'in_qualification':
      return <Badge variant="outline" className="border-yellow-500 text-yellow-700">Em qualificação</Badge>;
    case 'scheduled':
      return <Badge variant="default" className="bg-blue-500 text-white">Agendado</Badge>;
    default:
      return <Badge variant="outline">Novo</Badge>;
  }
};

export default function Dashboard() {
  const { selectedClient } = useClientContext();

  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading, refetch: refetchStats } = useQuery({
    queryKey: ['dashboard', 'stats', selectedClient?.id],
    queryFn: () => dashboardApi.getStats(selectedClient?.id),
    enabled: !!selectedClient,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  // Fetch recent conversations
  const { data: conversationsData, isLoading: conversationsLoading } = useQuery({
    queryKey: ['conversations', selectedClient?.id],
    queryFn: () => conversationsApi.getAll(selectedClient?.id, 0, 5),
    enabled: !!selectedClient,
    staleTime: 1 * 60 * 1000, // 1 minute
  });

  const recentConversations = conversationsData?.conversations || [];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">
            {selectedClient
              ? `Métricas de ${selectedClient.name} em tempo real`
              : 'Acompanhe suas métricas em tempo real'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => refetchStats()}
            disabled={statsLoading}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${statsLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
            <Phone className="mr-2 h-4 w-4" />
            Iniciar Atendimento
          </Button>
        </div>
      </div>

      {!selectedClient ? (
        <Card className="border-border">
          <CardContent className="p-6 text-center">
            <div className="mx-auto mb-4 w-16 h-16 bg-muted rounded-full flex items-center justify-center">
              <Users className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Selecione um cliente</h3>
            <p className="text-muted-foreground">
              Para visualizar as métricas do dashboard, selecione um cliente no cabeçalho.
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Conversas Ativas"
              value={stats?.active_conversations || 0}
              change="+12%"
              icon={MessageSquare}
              color="text-primary"
              isLoading={statsLoading}
            />
            <MetricCard
              title="Leads Qualificados"
              value={stats?.leads_qualified || 0}
              change="+8%"
              icon={Users}
              color="text-secondary"
              isLoading={statsLoading}
            />
            <MetricCard
              title="Total de Mensagens"
              value={stats?.total_messages || 0}
              change="+22%"
              icon={Calendar}
              color="text-success"
              isLoading={statsLoading}
            />
            <MetricCard
              title="Taxa de Conversão"
              value={`${Math.round((stats?.conversion_rate || 0) * 100)}%`}
              change="+3%"
              icon={TrendingUp}
              color="text-accent"
              isLoading={statsLoading}
            />
          </div>

          {/* Recent Conversations and Quick Actions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Conversations */}
            <Card className="border-border">
              <CardHeader>
                <CardTitle className="text-foreground">Conversas Recentes</CardTitle>
                <CardDescription>Últimas interações com leads</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {conversationsLoading ? (
                  Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="flex items-center space-x-3 p-3 border border-border rounded-lg">
                      <Skeleton className="w-10 h-10 rounded-full" />
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-3 w-24" />
                      </div>
                      <div className="space-y-2">
                        <Skeleton className="h-5 w-16" />
                        <Skeleton className="h-3 w-12" />
                      </div>
                    </div>
                  ))
                ) : recentConversations.length > 0 ? (
                  recentConversations.map((conversation) => (
                    <div
                      key={conversation.user_id}
                      className="flex items-center justify-between p-3 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-muted rounded-full flex items-center justify-center">
                          <User className="h-5 w-5 text-muted-foreground" />
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-foreground">
                            {conversation.user_name || conversation.user_id}
                          </h4>
                          <p className="text-xs text-muted-foreground">
                            {conversation.message_count} mensagens
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Score: {conversation.lead_score}/100
                          </p>
                        </div>
                      </div>
                      <div className="text-right space-y-1">
                        {getStatusBadge(conversation.status)}
                        <p className="text-xs text-muted-foreground flex items-center">
                          <Clock className="mr-1 h-3 w-3" />
                          {formatDistanceToNow(new Date(conversation.last_interaction), {
                            addSuffix: true,
                            locale: ptBR,
                          })}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <MessageSquare className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">
                      Nenhuma conversa encontrada para {selectedClient.name}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="border-border">
              <CardHeader>
                <CardTitle className="text-foreground">Ações Rápidas</CardTitle>
                <CardDescription>Acesso rápido às principais funcionalidades</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-start" asChild>
                  <a href="/conversations">
                    <MessageSquare className="mr-2 h-4 w-4" />
                    Ver todas as conversas
                  </a>
                </Button>
                <Button variant="outline" className="w-full justify-start" asChild>
                  <a href="/clients">
                    <Users className="mr-2 h-4 w-4" />
                    Gerenciar clientes
                  </a>
                </Button>
                <Button variant="outline" className="w-full justify-start" asChild>
                  <a href="/playbooks">
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Editar playbooks
                  </a>
                </Button>
                <Button variant="outline" className="w-full justify-start" asChild>
                  <a href="/reports">
                    <AlertCircle className="mr-2 h-4 w-4" />
                    Relatórios
                  </a>
                </Button>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}