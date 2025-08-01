import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Calendar, X } from 'lucide-react';

interface DateRangeFilterProps {
  onDateRangeChange: (filters: {
    date_from?: string;
    date_to?: string;
  }) => void;
  initialFilters?: {
    date_from?: string;
    date_to?: string;
  };
}

export function DateRangeFilter({ onDateRangeChange, initialFilters = {} }: DateRangeFilterProps) {
  const [filters, setFilters] = useState(initialFilters);

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = {
      ...filters,
      [key]: value || undefined,
    };
    setFilters(newFilters);
  };

  const applyFilters = () => {
    onDateRangeChange(filters);
  };

  const clearFilters = () => {
    const emptyFilters = {
      date_from: undefined,
      date_to: undefined,
    };
    setFilters(emptyFilters);
    onDateRangeChange(emptyFilters);
  };

  const setPresetRange = (days: number) => {
    const today = new Date();
    const startDate = new Date(today);
    startDate.setDate(today.getDate() - days);

    const newFilters = {
      date_from: startDate.toISOString().split('T')[0],
      date_to: today.toISOString().split('T')[0],
    };
    setFilters(newFilters);
    onDateRangeChange(newFilters);
  };

  const hasActiveFilters = Object.values(filters).some(value => value && value !== '');

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Calendar className="h-5 w-5" />
          Período dos Relatórios
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Date From */}
          <div className="space-y-2">
            <Label htmlFor="date_from">Data Inicial</Label>
            <Input
              id="date_from"
              type="date"
              value={filters.date_from || ''}
              onChange={(e) => handleFilterChange('date_from', e.target.value)}
            />
          </div>

          {/* Date To */}
          <div className="space-y-2">
            <Label htmlFor="date_to">Data Final</Label>
            <Input
              id="date_to"
              type="date"
              value={filters.date_to || ''}
              onChange={(e) => handleFilterChange('date_to', e.target.value)}
            />
          </div>
        </div>

        {/* Preset Buttons */}
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={() => setPresetRange(7)}>
            Últimos 7 dias
          </Button>
          <Button variant="outline" size="sm" onClick={() => setPresetRange(30)}>
            Últimos 30 dias
          </Button>
          <Button variant="outline" size="sm" onClick={() => setPresetRange(90)}>
            Últimos 90 dias
          </Button>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 pt-2">
          <Button onClick={applyFilters}>
            Aplicar Período
          </Button>
          {hasActiveFilters && (
            <Button variant="outline" onClick={clearFilters} className="flex items-center gap-2">
              <X className="h-4 w-4" />
              Limpar
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}