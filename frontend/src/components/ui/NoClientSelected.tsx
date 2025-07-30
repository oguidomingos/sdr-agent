import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Building2, Plus } from 'lucide-react';

interface NoClientSelectedProps {
  title?: string;
  description?: string;
  feature?: string;
  showCreateButton?: boolean;
  onCreateClick?: () => void;
}

export function NoClientSelected({
  title = 'Nenhum cliente selecionado',
  description = 'Para continuar, você precisa selecionar um cliente primeiro.',
  feature = 'esta funcionalidade',
  showCreateButton = false,
  onCreateClick,
}: NoClientSelectedProps) {
  return (
    <div className="flex items-center justify-center min-h-[500px] p-6">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <div className="mx-auto mb-4 w-16 h-16 bg-muted rounded-full flex items-center justify-center">
            <Building2 className="h-8 w-8 text-muted-foreground" />
          </div>
          <CardTitle className="text-xl font-semibold">{title}</CardTitle>
          <CardDescription className="text-base">
            {description}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Use o seletor de cliente no cabeçalho para escolher um cliente e acessar {feature}.
          </p>
          {showCreateButton && (
            <div className="pt-4 border-t">
              <p className="text-sm text-muted-foreground mb-3">
                Ou crie um novo cliente para começar:
              </p>
              <Button onClick={onCreateClick} className="w-full">
                <Plus className="mr-2 h-4 w-4" />
                Criar Novo Cliente
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}