import { useClient } from '@/contexts/ClientContext';
import { useQuery } from '@tanstack/react-query';
import { conversationsApi } from '@/lib/api';
import { NoClientSelected } from '@/components/ui/NoClientSelected';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { MessageSquare, User, Clock, Search, RefreshCw } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useState } from 'react';

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

export default function Conversations() {
  const { selectedClient } = useClient();
  const [searchTerm, setSearchTerm] = useState('');

  const { data: conversationsData, isLoading, refetch } = useQuery({
    queryKey: ['conversations', selectedClient?.id],
    queryFn: () => conversationsApi.getAll(selectedClient?.id, 0, 50),
    enabled: !!selectedClient,
    staleTime: 1 * 60 * 1000, // 1 minute
  });

  if (!selectedClient) {
    return (
      <NoClientSelected
        title="Nenhum cliente selecionado"
        description="Para visualizar as conversas, você precisa selecionar um cliente primeiro."
        feature="as conversas"
      />
    );
  }

  const conversations = conversationsData?.conversations || [];
  const filteredConversations = conversations.filter(conv =>
    (conv.user_name?.toLowerCase().includes(searchTerm.toLowerCase())) ||
    conv.user_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Conversas</h1>
          <p className="text-muted-foreground">
            Acompanhe todas as conversas de {selectedClient.name}
          </p>
        </div>
        <Button 
          variant="outline" 
          onClick={() => refetch()}
          disabled={isLoading}
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total de Conversas
            </CardTitle>
            <MessageSquare className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold text-foreground">{conversations.length}</div>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Leads Qualificados
            </CardTitle>
            <User className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold text-foreground">
                {conversations.filter(c => c.status === 'qualified').length}
              </div>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Em Qualificação
            </CardTitle>
            <Clock className="h-4 w-4 text-warning" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold text-foreground">
                {conversations.filter(c => c.status === 'in_qualification').length}
              </div>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Score Médio
            </CardTitle>
            <Clock className="h-4 w-4 text-accent" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold text-foreground">
                {conversations.length > 0 
                  ? Math.round(conversations.reduce((acc, c) => acc + c.lead_score, 0) / conversations.length)
                  : 0}
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
            placeholder="Buscar conversas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Conversations List */}
      <div className="space-y-4">
        {isLoading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <Card key={i} className="border-border">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <Skeleton className="h-12 w-12 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-5 w-48" />
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-4 w-24" />
                  </div>
                  <div className="space-y-2">
                    <Skeleton className="h-5 w-20" />
                    <Skeleton className="h-4 w-16" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : filteredConversations.length > 0 ? (
          filteredConversations.map((conversation) => (
            <Card key={conversation.user_id} className="border-border hover:bg-muted/50 transition-colors cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <Avatar className="h-12 w-12">
                      <AvatarFallback>
                        {(conversation.user_name || conversation.user_id).substring(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-semibold text-foreground">
                          {conversation.user_name || conversation.user_id}
                        </h3>
                        {getStatusBadge(conversation.status)}
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>ID: {conversation.user_id}</span>
                        <span>{conversation.message_count} mensagens</span>
                        <span>Score: {conversation.lead_score}/100</span>
                      </div>
                      
                      <p className="text-xs text-muted-foreground">
                        Última interação: {formatDistanceToNow(new Date(conversation.last_interaction), {
                          addSuffix: true,
                          locale: ptBR,
                        })}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                      Ver Conversa
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <Card className="border-border">
            <CardContent className="p-6 text-center">
              <MessageSquare className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">
                {searchTerm
                  ? `Nenhuma conversa encontrada para "${searchTerm}"`
                  : `Nenhuma conversa encontrada para ${selectedClient.name}`}
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}