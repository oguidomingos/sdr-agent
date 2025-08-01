import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  QrCode, 
  Smartphone, 
  CheckCircle, 
  XCircle, 
  RefreshCw, 
  AlertCircle,
  Loader2
} from 'lucide-react';
import { Client } from '@/types/api';
import { api } from '@/lib/api';

interface WhatsAppConnectionProps {
  client: Client;
  onConnectionChange?: (connected: boolean) => void;
}

interface QRCodeData {
  client_id: string;
  client_name: string;
  whatsapp_number: string;
  instance_name: string;
  qr_code?: string;
  qr_code_url?: string;
  status?: string;
  connection_state?: string;
}

interface ConnectionStatus {
  client_id: string;
  client_name: string;
  whatsapp_number: string;
  instance_name: string;
  status: any;
  is_connected: boolean;
}

export default function WhatsAppConnection({ client, onConnectionChange }: WhatsAppConnectionProps) {
  const [qrData, setQrData] = useState<QRCodeData | null>(null);
  const [status, setStatus] = useState<ConnectionStatus | null>(null);
  const [pairingCode, setPairingCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('qr');

  // Polling para atualizar status
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await api.get(`/clients/${client.id}/status`);
        setStatus(response.data);
        onConnectionChange?.(response.data.is_connected);
      } catch (err) {
        console.error('Error checking status:', err);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 5000); // Check every 5 seconds

    return () => clearInterval(interval);
  }, [client.id, onConnectionChange]);

  const loadQRCode = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/clients/${client.id}/qr-code`);
      setQrData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao carregar QR Code');
    } finally {
      setLoading(false);
    }
  };

  const connectWithPairingCode = async () => {
    if (!pairingCode.trim()) {
      setError('Código de pareamento é obrigatório');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.post(`/clients/${client.id}/connect-pairing`, {
        pairing_code: pairingCode
      });
      
      // Success feedback
      setError(null);
      setPairingCode('');
      
      // Refresh status
      setTimeout(async () => {
        try {
          const statusResponse = await api.get(`/clients/${client.id}/status`);
          setStatus(statusResponse.data);
          onConnectionChange?.(statusResponse.data.is_connected);
        } catch (err) {
          console.error('Error refreshing status:', err);
        }
      }, 2000);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao conectar com código de pareamento');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = () => {
    if (!status) return <Badge variant="secondary">Carregando...</Badge>;
    
    if (status.is_connected) {
      return <Badge variant="default" className="bg-green-500"><CheckCircle className="w-3 h-3 mr-1" />Conectado</Badge>;
    }
    
    const state = status.status?.state;
    switch (state) {
      case 'close':
        return <Badge variant="destructive"><XCircle className="w-3 h-3 mr-1" />Desconectado</Badge>;
      case 'connecting':
        return <Badge variant="secondary"><Loader2 className="w-3 h-3 mr-1 animate-spin" />Conectando</Badge>;
      default:
        return <Badge variant="outline"><AlertCircle className="w-3 h-3 mr-1" />Aguardando</Badge>;
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Smartphone className="w-5 h-5" />
            Conexão WhatsApp
          </CardTitle>
          {getStatusBadge()}
        </div>
        <div className="text-sm text-muted-foreground">
          <p><strong>Cliente:</strong> {client.name}</p>
          <p><strong>Número:</strong> {client.whatsapp_number}</p>
          <p><strong>Instância:</strong> {client.evolution_instance}</p>
        </div>
      </CardHeader>
      
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {status?.is_connected ? (
          <Alert className="mb-4">
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>
              ✅ WhatsApp conectado com sucesso! A instância está pronta para receber mensagens.
            </AlertDescription>
          </Alert>
        ) : (
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="qr">QR Code</TabsTrigger>
              <TabsTrigger value="pairing">Código de Pareamento</TabsTrigger>
            </TabsList>

            <TabsContent value="qr" className="space-y-4">
              <div className="text-center space-y-4">
                <p className="text-sm text-muted-foreground">
                  Escaneie o QR Code com o WhatsApp do número <strong>{client.whatsapp_number}</strong>
                </p>
                
                {qrData?.qr_code ? (
                  <div className="flex justify-center">
                    <img 
                      src={`data:image/png;base64,${qrData.qr_code}`}
                      alt="QR Code WhatsApp"
                      className="border rounded-lg"
                      style={{ maxWidth: '256px', maxHeight: '256px' }}
                    />
                  </div>
                ) : (
                  <div className="flex justify-center">
                    <Button onClick={loadQRCode} disabled={loading}>
                      {loading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Carregando...
                        </>
                      ) : (
                        <>
                          <QrCode className="mr-2 h-4 w-4" />
                          Gerar QR Code
                        </>
                      )}
                    </Button>
                  </div>
                )}
                
                {qrData && (
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={loadQRCode}
                    disabled={loading}
                  >
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Atualizar QR Code
                  </Button>
                )}
              </div>
            </TabsContent>

            <TabsContent value="pairing" className="space-y-4">
              <div className="space-y-4">
                <div className="text-sm text-muted-foreground">
                  <p>1. Abra o WhatsApp no número <strong>{client.whatsapp_number}</strong></p>
                  <p>2. Vá em <strong>Configurações → Aparelhos conectados → Conectar um aparelho</strong></p>
                  <p>3. Toque em <strong>"Conectar com número de telefone"</strong></p>
                  <p>4. Digite o código que aparecer abaixo:</p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="pairing_code">Código de Pareamento</Label>
                  <div className="flex gap-2">
                    <Input
                      id="pairing_code"
                      value={pairingCode}
                      onChange={(e) => setPairingCode(e.target.value)}
                      placeholder="Digite o código do WhatsApp"
                      disabled={loading}
                    />
                    <Button 
                      onClick={connectWithPairingCode}
                      disabled={loading || !pairingCode.trim()}
                    >
                      {loading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        'Conectar'
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
}