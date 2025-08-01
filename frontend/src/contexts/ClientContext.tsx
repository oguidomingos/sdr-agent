import { createContext, useContext, useState, ReactNode } from 'react';
import { Client, ClientCreateData, ClientUpdateData } from '@/types/api';
import { clientsApi } from '@/lib/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';

interface ClientContextType {
  clients: Client[];
  selectedClient: Client | null;
  isLoading: boolean;
  error: string | null;
  setSelectedClient: (client: Client | null) => void;
  deleteClient: (id: string) => Promise<void>;
  refetchClients: () => void;
}

const ClientContext = createContext<ClientContextType | undefined>(undefined);

export function ClientProvider({ children }: { children: ReactNode }) {
  const [selectedClient, setSelectedClient] = useState<Client | null>(() => {
    // Try to load selected client from localStorage
    const savedClient = localStorage.getItem('selectedClient');
    return savedClient ? JSON.parse(savedClient) : null;
  });
  
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const {
    data: clients = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['clients'],
    queryFn: () => clientsApi.getAll().then(res => res.clients),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const deleteMutation = useMutation({
    mutationFn: clientsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      toast({
        title: 'Cliente removido',
        description: 'Cliente removido com sucesso.',
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

  const deleteClient = async (id: string) => {
    await deleteMutation.mutateAsync(id);
  };

  const refetchClients = () => {
    refetch();
  };

  const handleSetSelectedClient = (client: Client | null) => {
    setSelectedClient(client);
    if (client) {
      localStorage.setItem('selectedClient', JSON.stringify(client));
    } else {
      localStorage.removeItem('selectedClient');
    }
  };

  const value = {
    clients,
    selectedClient,
    isLoading,
    error: error ? 'Erro ao carregar clientes' : null,
    setSelectedClient: handleSetSelectedClient,
    deleteClient,
    refetchClients,
  };

  return (
    <ClientContext.Provider value={value}>
      {children}
    </ClientContext.Provider>
  );
}

export function useClientContext() {
  const context = useContext(ClientContext);
  if (context === undefined) {
    throw new Error('useClientContext must be used within a ClientProvider');
  }
  return context;
}