import { useClientContext } from '@/contexts/ClientContext';
import { useMessages } from '@/hooks/useMessages';
import { NoClientSelected } from '@/components/ui/NoClientSelected';
import { MessageFilters } from '@/components/messages/MessageFilters';
import { MessageList } from '@/components/messages/MessageList';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';
import { useState } from 'react';

export default function Conversations() {
  const { selectedClient } = useClientContext();
  const [filters, setFilters] = useState<{
    date_from?: string;
    date_to?: string;
    status?: string;
    keyword?: string;
  }>({});

  const { data: messagesData, isLoading, refetch } = useMessages(
    selectedClient?.id || '',
    filters
  );

  if (!selectedClient) {
    return (
      <NoClientSelected
        title="Nenhum cliente selecionado"
        description="Para visualizar o histórico de mensagens, você precisa selecionar um cliente primeiro."
        feature="as mensagens"
      />
    );
  }

  const messages = messagesData?.messages || [];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Histórico de Mensagens</h1>
          <p className="text-muted-foreground">
            Consulte todas as mensagens e conversas de {selectedClient.name}
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

      {/* Filters */}
      <MessageFilters 
        onFiltersChange={setFilters}
        initialFilters={filters}
      />

      {/* Messages List */}
      <MessageList 
        messages={messages}
        isLoading={isLoading}
      />
    </div>
  );
}