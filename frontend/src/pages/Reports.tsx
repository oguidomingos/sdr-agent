import { useClient } from '@/contexts/ClientContext';
import { NoClientSelected } from '@/components/ui/NoClientSelected';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  BarChart3,
  TrendingUp,
  Users,
  MessageSquare,
  Calendar,
  Download,
  Filter,
  RefreshCw,
} from 'lucide-react';

export default function Reports() {
  const { selectedClient } = useClient();

  if (!selectedClient) {
    return (
      <NoClientSelected
        title="Nenhum cliente selecionado"
        description="Para visualizar os relatórios, você precisa selecionar um cliente primeiro."
        feature="os relatórios"
      />
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Relatórios</h1>
          <p className="text-muted-foreground">
            Análise de desempenho e métricas de {selectedClient.name}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Filter className="mr-2 h-4 w-4" />
            Filtrar
          </Button>
          <Button variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Atualizar
          </Button>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
            <Download className="mr-2 h-4 w-4" />
            Exportar
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total de Conversas
            </CardTitle>
            <MessageSquare className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">1,247</div>
            <p className="text-xs text-success">+18% vs mês anterior</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Taxa de Conversão
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">24.5%</div>
            <p className="text-xs text-success">+5.2% vs mês anterior</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Leads Qualificados
            </CardTitle>
            <Users className="h-4 w-4 text-warning" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">305</div>
            <p className="text-xs text-success">+12% vs mês anterior</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tempo Médio de Resposta
            </CardTitle>
            <Calendar className="h-4 w-4 text-accent" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">2.3min</div>
            <p className="text-xs text-destructive">+0.5min vs mês anterior</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="text-foreground">Conversas por Período</CardTitle>
            <CardDescription>Últimos 30 dias</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center bg-muted/20 rounded-lg">
              <div className="text-center">
                <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">Gráfico de conversas por período</p>
                <p className="text-sm text-muted-foreground mt-2">
                  Em desenvolvimento - integração com biblioteca de gráficos
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader>
            <CardTitle className="text-foreground">Taxa de Conversão</CardTitle>
            <CardDescription>Performance por semana</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center bg-muted/20 rounded-lg">
              <div className="text-center">
                <TrendingUp className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">Gráfico de taxa de conversão</p>
                <p className="text-sm text-muted-foreground mt-2">
                  Em desenvolvimento - integração com biblioteca de gráficos
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance by Playbook */}
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Performance por Playbook</CardTitle>
          <CardDescription>Análise de efetividade dos roteiros</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { name: 'Qualificação Cardiologia', conversions: 45, total: 127, rate: 35.4 },
              { name: 'Agendamento Pediatria', conversions: 32, total: 89, rate: 36.0 },
              { name: 'Follow-up Dermatologia', conversions: 18, total: 65, rate: 27.7 },
            ].map((playbook, index) => (
              <div key={index} className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div className="flex-1">
                  <h4 className="font-medium text-foreground">{playbook.name}</h4>
                  <p className="text-sm text-muted-foreground">
                    {playbook.conversions} conversões de {playbook.total} conversas
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-foreground">{playbook.rate}%</div>
                  <Badge 
                    variant={playbook.rate > 30 ? "default" : "outline"}
                    className={playbook.rate > 30 ? "bg-green-500 text-white" : ""}
                  >
                    {playbook.rate > 30 ? 'Excelente' : 'Regular'}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Insights */}
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Insights Rápidos</CardTitle>
          <CardDescription>Recomendações baseadas nos dados</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <TrendingUp className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-900">Melhoria na Taxa de Conversão</h4>
                <p className="text-sm text-blue-700">
                  Suas conversões aumentaram 5.2% este mês. Continue otimizando os playbooks de maior performance.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <Calendar className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-yellow-900">Tempo de Resposta</h4>
                <p className="text-sm text-yellow-700">
                  O tempo médio de resposta aumentou. Considere revisar os prompts para respostas mais rápidas.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <Users className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-green-900">Crescimento de Leads</h4>
                <p className="text-sm text-green-700">
                  O número de leads qualificados cresceu 12%. Excelente trabalho!
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}