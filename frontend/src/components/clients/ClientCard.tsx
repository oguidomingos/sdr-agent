import { useState } from 'react';
import { Client } from '@/types/api';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Edit, Trash2, Smartphone, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useClientContext } from '@/contexts/ClientContext';
import WhatsAppConnection from './WhatsAppConnection';

interface ClientCardProps {
  client: Client;
}

export function ClientCard({ client }: ClientCardProps) {
  const { setCurrentClient, setMode, deleteClient } = useClientContext();
  const { toast } = useToast();
  const [isConnected, setIsConnected] = useState(false);
  const [whatsappDialogOpen, setWhatsappDialogOpen] = useState(false);

  const handleEdit = () => {
    setCurrentClient(client);
    setMode('edit');
  };

  const handleDelete = async () => {
    try {
      await deleteClient(client.id);
    } catch (error) {
      toast({
        title: 'Erro ao remover cliente',
        description: 'Não foi possível remover o cliente. Tente novamente.',
        variant: 'destructive',
      });
    }
  };

  const handleConnectionChange = (connected: boolean) => {
    setIsConnected(connected);
  };

  const handleResetSessions = async () => {
    if (!confirm('Tem certeza que deseja resetar todas as sessões/mensagens deste cliente? Esta ação não pode ser desfeita.')) {
      return;
    }

    try {
      const response = await fetch(`/api/clients/${client.id}/reset-sessions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        toast({
          title: 'Sessões resetadas',
          description: `${result.messages_deleted} mensagens foram removidas. O agente começará do zero.`,
        });
      } else {
        throw new Error('Erro ao resetar sessões');
      }
    } catch (error) {
      toast({
        title: 'Erro ao resetar sessões',
        description: 'Não foi possível resetar as sessões. Tente novamente.',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="border-border hover:shadow-md transition-shadow p-6">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4 flex-1">
          <Avatar className="h-12 w-12">
            <AvatarImage src={client.logo_url} />
            <AvatarFallback className="text-sm font-medium">
              {client.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
            </AvatarFallback>
          </Avatar>
          
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold">{client.name}</h3>
              <Badge variant={client.status === 'active' ? 'default' : 'outline'}>
                {client.status}
              </Badge>
              {isConnected ? (
                <Badge variant="default" className="bg-green-500">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  WhatsApp
                </Badge>
              ) : (
                <Badge variant="outline">
                  <XCircle className="w-3 h-3 mr-1" />
                  Desconectado
                </Badge>
              )}
            </div>
            
            {client.description && (
              <p className="text-muted-foreground text-sm">{client.description}</p>
            )}
            
            {client.whatsapp_number && (
              <p className="text-muted-foreground text-sm">
                <strong>WhatsApp:</strong> {client.whatsapp_number}
              </p>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-2 ml-4">
          <Dialog open={whatsappDialogOpen} onOpenChange={setWhatsappDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Smartphone className="mr-2 h-4 w-4" />
                WhatsApp
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Conexão WhatsApp</DialogTitle>
              </DialogHeader>
              <WhatsAppConnection 
                client={client} 
                onConnectionChange={handleConnectionChange}
              />
            </DialogContent>
          </Dialog>
          
          <Button variant="outline" size="sm" onClick={handleResetSessions}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Reset
          </Button>
          
          <Button variant="outline" size="sm" onClick={handleEdit}>
            <Edit className="mr-2 h-4 w-4" />
            Editar
          </Button>
          <Button variant="outline" size="sm" onClick={handleDelete}>
            <Trash2 className="mr-2 h-4 w-4" />
            Remover
          </Button>
        </div>
      </div>
    </div>
  );
}