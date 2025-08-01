import { ClientResponse } from '../../types/api/clients';
import WebhookButton from './WebhookButton';

interface ClientRowProps {
  client: ClientResponse;
  onSelect: (clientId: string) => void;
  onEdit: (clientId: string) => void;
}

export default function ClientRow({ client, onSelect, onEdit }: ClientRowProps) {
  return (
    <tr>
      <td>
        <button onClick={() => onSelect(client.id)}>
          {client.name}
        </button>
      </td>
      <td>{client.status}</td>
      <td>
        <WebhookButton 
          clientId={client.id}
          isConfigured={client.has_webhook_configured}
        />
      </td>
      <td>
        <button onClick={() => onEdit(client.id)}>
          Editar
        </button>
      </td>
    </tr>
  );
}