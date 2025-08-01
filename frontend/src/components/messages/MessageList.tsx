import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Message } from '@/types/api';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { MessageSquare, Bot, User, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  className?: string;
}

const getStatusColor = (status: string | undefined) => {
  switch (status) {
    case 'qualified':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'scheduled':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'lost':
      return 'bg-red-100 text-red-800 border-red-200';
    case 'archived':
      return 'bg-gray-100 text-gray-800 border-gray-200';
    default:
      return 'bg-gray-100 text-gray-600 border-gray-200';
  }
};

const getStatusLabel = (status: string | undefined) => {
  switch (status) {
    case 'qualified':
      return 'Qualificado';
    case 'scheduled':
      return 'Agendado';
    case 'lost':
      return 'Perdido';
    case 'archived':
      return 'Arquivado';
    case 'none':
      return 'Sem Status';
    default:
      return status || 'Sem Status';
  }
};

export function MessageList({ messages, isLoading, className }: MessageListProps) {
  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Histórico de Mensagens
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="flex gap-3">
                  <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                    <div className="h-16 bg-gray-200 rounded"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (messages.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Histórico de Mensagens
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-muted-foreground mb-2">
              Nenhuma mensagem encontrada
            </h3>
            <p className="text-sm text-muted-foreground">
              Ajuste os filtros para encontrar mensagens específicas.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          Histórico de Mensagens ({messages.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {messages.map((message) => {
            const isInbound = message.message_direction === 'inbound';
            const timestamp = new Date(message.timestamp);

            return (
              <div
                key={message.id}
                className={cn(
                  'flex gap-3',
                  !isInbound && 'flex-row-reverse'
                )}
              >
                {/* Avatar */}
                <Avatar className="w-10 h-10 flex-shrink-0">
                  <AvatarFallback className={cn(
                    'text-sm font-medium',
                    isInbound 
                      ? 'bg-blue-100 text-blue-700' 
                      : 'bg-green-100 text-green-700'
                  )}>
                    {isInbound ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
                  </AvatarFallback>
                </Avatar>

                {/* Message Content */}
                <div className={cn(
                  'flex-1 max-w-[70%] space-y-2',
                  !isInbound && 'items-end'
                )}>
                  {/* Header */}
                  <div className={cn(
                    'flex items-center gap-2 text-sm text-muted-foreground',
                    !isInbound && 'flex-row-reverse'
                  )}>
                    <span className="font-medium">
                      {isInbound 
                        ? (message.user_name || `User ${message.user_id}`)
                        : 'Assistente'
                      }
                    </span>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>
                        {format(timestamp, "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                      </span>
                    </div>
                  </div>

                  {/* Message Bubble */}
                  <div className={cn(
                    'p-3 rounded-lg text-sm',
                    isInbound
                      ? 'bg-muted text-muted-foreground'
                      : 'bg-primary text-primary-foreground'
                  )}>
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>

                  {/* Message Metadata */}
                  <div className={cn(
                    'flex flex-wrap gap-2 text-xs',
                    !isInbound && 'justify-end'
                  )}>
                    {message.status && (
                      <Badge variant="outline" className={getStatusColor(message.status)}>
                        {getStatusLabel(message.status)}
                      </Badge>
                    )}
                    {message.conversation_stage && (
                      <Badge variant="outline">
                        {message.conversation_stage}
                      </Badge>
                    )}
                    {message.lead_score > 0 && (
                      <Badge variant="outline" className="bg-yellow-100 text-yellow-800 border-yellow-200">
                        Score: {message.lead_score}
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}