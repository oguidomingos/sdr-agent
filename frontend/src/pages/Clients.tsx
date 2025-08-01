import { useState } from 'react';
import { useClientContext } from '@/contexts/ClientContext';
import ClientForm from '@/components/clients/ClientForm';
import ClientList from '@/components/clients/ClientList';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { Client, ClientCreateData, ClientUpdateData } from '@/types/api';
import { clientsApi } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export default function Clients() {
  const [viewMode, setViewMode] = useState<'list' | 'create' | 'edit'>('list');
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const { refetchClients } = useClientContext();
  const { toast } = useToast();

  const handleCreateClient = () => {
    setEditingClient(null);
    setViewMode('create');
  };

  const handleEditClient = (client: Client) => {
    setEditingClient(client);
    setViewMode('edit');
  };

  const handleBackToList = () => {
    setViewMode('list');
    setEditingClient(null);
  };

  const handleSubmitCreate = async (data: ClientCreateData) => {
    try {
      const newClient = await clientsApi.create(data);
      
      toast({
        title: 'Cliente criado',
        description: 'Cliente criado com sucesso.',
      });
      
      // If register webhook is enabled, register it after creation
      if (data.register_webhook && newClient?.id) {
        try {
          await clientsApi.registerWebhook(newClient.id);
          toast({
            title: 'Webhook configurado',
            description: 'Webhook foi registrado com sucesso.',
          });
        } catch (webhookError) {
          console.error('Webhook registration failed:', webhookError);
          toast({
            title: 'Aviso',
            description: 'Cliente criado, mas falha ao configurar webhook.',
            variant: 'default',
          });
        }
      }
      
      refetchClients();
      handleBackToList();
    } catch (error) {
      console.error('Error creating client:', error);
      toast({
        title: 'Erro ao criar cliente',
        description: 'Não foi possível criar o cliente. Tente novamente.',
        variant: 'destructive',
      });
    }
  };

  const handleSubmitEdit = async (data: ClientUpdateData) => {
    if (!editingClient) return;
    
    try {
      await clientsApi.update(editingClient.id, data);
      
      toast({
        title: 'Cliente atualizado',
        description: 'Cliente atualizado com sucesso.',
      });
      
      // If register webhook is enabled, register it after update
      if (data.register_webhook) {
        try {
          await clientsApi.registerWebhook(editingClient.id);
          toast({
            title: 'Webhook configurado',
            description: 'Webhook foi registrado com sucesso.',
          });
        } catch (webhookError) {
          console.error('Webhook registration failed:', webhookError);
          toast({
            title: 'Aviso',
            description: 'Cliente atualizado, mas falha ao configurar webhook.',
            variant: 'default',
          });
        }
      }
      
      refetchClients();
      handleBackToList();
    } catch (error) {
      console.error('Error updating client:', error);
      toast({
        title: 'Erro ao atualizar cliente',
        description: 'Não foi possível atualizar o cliente. Tente novamente.',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {viewMode !== 'list' && (
            <Button
              variant="outline"
              size="icon"
              onClick={handleBackToList}
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
          )}
          <div>
            <h1 className="text-3xl font-bold">
              {viewMode === 'list' && 'Clientes'}
              {viewMode === 'create' && 'Criar Novo Cliente'}
              {viewMode === 'edit' && `Editar ${editingClient?.name}`}
            </h1>
            <p className="text-muted-foreground">
              {viewMode === 'list' && 'Gerencie todos os clientes do sistema'}
              {viewMode === 'create' && 'Preencha os dados para criar um novo cliente'}
              {viewMode === 'edit' && 'Atualize as informações do cliente'}
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      {viewMode === 'list' && (
        <ClientList
          onCreateClient={handleCreateClient}
          onEditClient={handleEditClient}
        />
      )}

      {(viewMode === 'create' || viewMode === 'edit') && (
        <Card>
          <CardContent className="p-6">
            <ClientForm
              client={editingClient || undefined}
              onSubmit={viewMode === 'create' ? handleSubmitCreate : handleSubmitEdit}
              onCancel={handleBackToList}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}