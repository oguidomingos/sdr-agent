import { useClientContext } from '@/contexts/ClientContext';
import { useStats } from '@/hooks/useStats';
import { NoClientSelected } from '@/components/ui/NoClientSelected';
import { StatsOverview } from '@/components/reports/StatsOverview';
import { DateRangeFilter } from '@/components/reports/DateRangeFilter';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';
import { useState } from 'react';

export default function Reports() {
  const { selectedClient } = useClientContext();
  const [dateFilters, setDateFilters] = useState<{
    date_from?: string;
    date_to?: string;
  }>({});

  const { data: statsData, isLoading, refetch } = useStats(
    selectedClient?.id || '',
    dateFilters
  );

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
        <Button 
          variant="outline" 
          onClick={() => refetch()}
          disabled={isLoading}
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {/* Date Range Filter */}
      <DateRangeFilter 
        onDateRangeChange={setDateFilters}
        initialFilters={dateFilters}
      />

      {/* Stats Overview */}
      {statsData && (
        <StatsOverview 
          stats={statsData}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}