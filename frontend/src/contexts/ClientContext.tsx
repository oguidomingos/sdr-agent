import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { clientsApi } from '@/lib/api';
import { Client } from '@/types/api';

interface ClientContextType {
  selectedClient: Client | null;
  setSelectedClient: (client: Client | null) => void;
  clients: Client[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

const ClientContext = createContext<ClientContextType | undefined>(undefined);

export function ClientProvider({ children }: { children: ReactNode }) {
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);

  // Fetch clients using React Query
  const {
    data: clientsResponse,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['clients'],
    queryFn: () => clientsApi.getAll(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  });

  const clients = clientsResponse?.clients || [];

  // Auto-select first client if none selected and clients are available
  useEffect(() => {
    if (!selectedClient && clients.length > 0) {
      // Try to get from localStorage first
      const savedClientId = localStorage.getItem('selectedClientId');
      if (savedClientId) {
        const savedClient = clients.find((c) => c.id === savedClientId);
        if (savedClient) {
          setSelectedClient(savedClient);
          return;
        }
      }
      // Otherwise select first client
      setSelectedClient(clients[0]);
    }
  }, [clients, selectedClient]);

  // Save selected client to localStorage
  const handleSetSelectedClient = (client: Client | null) => {
    setSelectedClient(client);
    if (client) {
      localStorage.setItem('selectedClientId', client.id);
    } else {
      localStorage.removeItem('selectedClientId');
    }
  };

  return (
    <ClientContext.Provider
      value={{
        selectedClient,
        setSelectedClient: handleSetSelectedClient,
        clients,
        isLoading,
        error: error as Error | null,
        refetch,
      }}
    >
      {children}
    </ClientContext.Provider>
  );
}

export function useClient() {
  const context = useContext(ClientContext);
  if (context === undefined) {
    throw new Error('useClient must be used within a ClientProvider');
  }
  return context;
}