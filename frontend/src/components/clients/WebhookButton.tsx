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
  // Webhook is always configured automatically when creating client
  return (
    <Badge variant="default" className="bg-green-100 text-green-800 border-green-300">
      <CheckCircle className="mr-1 h-3 w-3" />
      Webhook Automático
    </Badge>
  );
}