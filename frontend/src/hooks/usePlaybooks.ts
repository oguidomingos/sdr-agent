import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { playbooksApi } from '@/lib/api';
import { PlaybookCreateData, PlaybookUpdateData, Playbook } from '@/types/api';
import { useToast } from '@/hooks/use-toast';

export function usePlaybooks(clientId: string) {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Query for getting all playbooks
  const query = useQuery({
    queryKey: ['playbooks', clientId],
    queryFn: () => playbooksApi.getAll(clientId),
    enabled: !!clientId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Mutation for creating a playbook
  const createMutation = useMutation({
    mutationFn: (data: PlaybookCreateData) => playbooksApi.create(clientId, data),
    onSuccess: (newPlaybook) => {
      queryClient.invalidateQueries({ queryKey: ['playbooks', clientId] });
      toast({
        title: 'Playbook criado',
        description: `O playbook "${newPlaybook.name}" foi criado com sucesso.`,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Erro ao criar playbook',
        description: error.response?.data?.detail || 'Ocorreu um erro inesperado.',
        variant: 'destructive',
      });
    },
  });

  // Mutation for updating a playbook
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: PlaybookUpdateData }) =>
      playbooksApi.update(clientId, id, data),
    onSuccess: (updatedPlaybook) => {
      queryClient.invalidateQueries({ queryKey: ['playbooks', clientId] });
      toast({
        title: 'Playbook atualizado',
        description: `O playbook "${updatedPlaybook.name}" foi atualizado com sucesso.`,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Erro ao atualizar playbook',
        description: error.response?.data?.detail || 'Ocorreu um erro inesperado.',
        variant: 'destructive',
      });
    },
  });

  // Mutation for deleting a playbook
  const deleteMutation = useMutation({
    mutationFn: (id: string) => playbooksApi.delete(clientId, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playbooks', clientId] });
      toast({
        title: 'Playbook excluído',
        description: 'O playbook foi excluído com sucesso.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Erro ao excluir playbook',
        description: error.response?.data?.detail || 'Ocorreu um erro inesperado.',
        variant: 'destructive',
      });
    },
  });

  // Mutation for activating a playbook
  const activateMutation = useMutation({
    mutationFn: (id: string) => playbooksApi.activate(clientId, id),
    onSuccess: (activatedPlaybook) => {
      queryClient.invalidateQueries({ queryKey: ['playbooks', clientId] });
      toast({
        title: 'Playbook ativado',
        description: `O playbook "${activatedPlaybook.name}" foi ativado com sucesso.`,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Erro ao ativar playbook',
        description: error.response?.data?.detail || 'Ocorreu um erro inesperado.',
        variant: 'destructive',
      });
    },
  });

  // Mutation for deactivating a playbook
  const deactivateMutation = useMutation({
    mutationFn: (id: string) => playbooksApi.deactivate(clientId, id),
    onSuccess: (deactivatedPlaybook) => {
      queryClient.invalidateQueries({ queryKey: ['playbooks', clientId] });
      toast({
        title: 'Playbook pausado',
        description: `O playbook "${deactivatedPlaybook.name}" foi pausado com sucesso.`,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Erro ao pausar playbook',
        description: error.response?.data?.detail || 'Ocorreu um erro inesperado.',
        variant: 'destructive',
      });
    },
  });

  // Mutation for duplicating a playbook
  const duplicateMutation = useMutation({
    mutationFn: (id: string) => playbooksApi.duplicate(clientId, id),
    onSuccess: (duplicatedPlaybook) => {
      queryClient.invalidateQueries({ queryKey: ['playbooks', clientId] });
      toast({
        title: 'Playbook duplicado',
        description: `O playbook "${duplicatedPlaybook.name}" foi criado com sucesso.`,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Erro ao duplicar playbook',
        description: error.response?.data?.detail || 'Ocorreu um erro inesperado.',
        variant: 'destructive',
      });
    },
  });

  return {
    // Query data
    playbooks: query.data?.playbooks || [],
    total: query.data?.total || 0,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    
    // Actions
    createPlaybook: createMutation.mutateAsync,
    updatePlaybook: updateMutation.mutateAsync,
    deletePlaybook: deleteMutation.mutateAsync,
    activatePlaybook: activateMutation.mutateAsync,
    deactivatePlaybook: deactivateMutation.mutateAsync,
    duplicatePlaybook: duplicateMutation.mutateAsync,
    
    // Mutation states
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isActivating: activateMutation.isPending,
    isDeactivating: deactivateMutation.isPending,
    isDuplicating: duplicateMutation.isPending,
    
    // Refresh function
    refetch: query.refetch,
  };
}

export function usePlaybook(clientId: string, playbookId: string) {
  return useQuery({
    queryKey: ['playbook', clientId, playbookId],
    queryFn: () => playbooksApi.getById(clientId, playbookId),
    enabled: !!clientId && !!playbookId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}