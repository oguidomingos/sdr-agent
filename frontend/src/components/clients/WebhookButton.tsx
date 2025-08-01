import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { clientsApi } from '@/lib/api';
import { useClientContext } from '@/contexts/ClientContext';
import { useToast } from '@/hooks/use-toast';
import { Webhook, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

interface WebhookButtonProps {
  clientId: string;
  isConfigured: boolean;
}

export default function WebhookButton({ clientId, isConfigured }: WebhookButtonProps) {
  const [loading, setLoading] = useState(false);
  const { refetchClients } = useClientContext();
  const { toast } = useToast();

  const handleConfigureWebhook = async () => {
    setLoading(true);
    
    try {
      await clientsApi.registerWebhook(clientId);
      
      toast({
        title: 'Webhook configurado',
        description: 'Webhook foi registrado com sucesso.',
      });
      
      // Refresh the clients list to update the webhook status
      refetchClients();
    } catch (err) {
      toast({
        title: 'Erro ao configurar webhook',
        description: 'Não foi possível configurar o webhook. Tente novamente.',
        variant: 'destructive',
      });
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (isConfigured) {
    return (
      <Badge variant="default" className="bg-green-100 text-green-800 border-green-300">
        <CheckCircle className="mr-1 h-3 w-3" />
        Webhook Ativo
      </Badge>
    );
  }

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleConfigureWebhook}
      disabled={loading}
      className="text-orange-600 border-orange-300 hover:bg-orange-50"
    >
      {loading ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Configurando...
        </>
      ) : (
        <>
          <Webhook className="mr-2 h-4 w-4" />
          Configurar
        </>
      )}
    </Button>
  );
}