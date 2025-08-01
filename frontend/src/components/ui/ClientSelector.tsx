import { useClientContext } from '@/contexts/ClientContext';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Building2, Loader2 } from 'lucide-react';

export function ClientSelector() {
  const { selectedClient, setSelectedClient, clients, isLoading } = useClientContext();

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 min-w-[200px]">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm text-muted-foreground">Carregando clientes...</span>
      </div>
    );
  }

  if (clients.length === 0) {
    return (
      <div className="flex items-center gap-2 min-w-[200px]">
        <Building2 className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">Nenhum cliente encontrado</span>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="default" className="bg-green-500 text-white">Ativo</Badge>;
      case 'trial':
        return <Badge variant="secondary">Trial</Badge>;
      case 'inactive':
        return <Badge variant="outline">Inativo</Badge>;
      case 'suspended':
        return <Badge variant="destructive">Suspenso</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm font-medium text-muted-foreground">Cliente:</span>
      <Select
        value={selectedClient?.id || ''}
        onValueChange={(value) => {
          const client = clients.find((c) => c.id === value);
          setSelectedClient(client || null);
        }}
      >
        <SelectTrigger className="min-w-[250px]">
          <SelectValue placeholder="Selecione um cliente">
            {selectedClient && (
              <div className="flex items-center gap-2">
                <Avatar className="h-6 w-6">
                  <AvatarImage src={selectedClient.logo_url} />
                  <AvatarFallback className="text-xs">
                    {selectedClient.name
                      .split(' ')
                      .map((n) => n[0])
                      .join('')
                      .toUpperCase()
                      .slice(0, 2)}
                  </AvatarFallback>
                </Avatar>
                <span className="font-medium">{selectedClient.name}</span>
                {getStatusBadge(selectedClient.status)}
              </div>
            )}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {clients.map((client) => (
            <SelectItem key={client.id} value={client.id}>
              <div className="flex items-center gap-2 w-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={client.logo_url} />
                  <AvatarFallback className="text-xs">
                    {client.name
                      .split(' ')
                      .map((n) => n[0])
                      .join('')
                      .toUpperCase()
                      .slice(0, 2)}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{client.name}</span>
                    {getStatusBadge(client.status)}
                  </div>
                  {client.description && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {client.description}
                    </p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {client.domain}
                  </p>
                </div>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}