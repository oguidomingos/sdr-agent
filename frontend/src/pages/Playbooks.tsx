import { useState } from 'react';
import { useClientContext } from '@/contexts/ClientContext';
import { usePlaybooks } from '@/hooks/usePlaybooks';
import { NoClientSelected } from '@/components/ui/NoClientSelected';
import { PlaybookList } from '@/components/playbooks/PlaybookList';
import { PlaybookForm } from '@/components/playbooks/PlaybookForm';
import { Playbook, PlaybookCreateData, PlaybookUpdateData } from '@/types/api';

type ViewMode = 'list' | 'create' | 'edit';

export default function Playbooks() {
  const { selectedClient } = useClientContext();
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [editingPlaybook, setEditingPlaybook] = useState<Playbook | null>(null);

  const {
    playbooks,
    isLoading,
    createPlaybook,
    updatePlaybook,
    deletePlaybook,
    activatePlaybook,
    deactivatePlaybook,
    duplicatePlaybook,
    isCreating,
    isUpdating,
    isDeleting,
    isActivating,
    isDeactivating,
    isDuplicating,
  } = usePlaybooks(selectedClient?.id || '');

  if (!selectedClient) {
    return (
      <NoClientSelected
        title="Nenhum cliente selecionado"
        description="Para visualizar os playbooks, você precisa selecionar um cliente primeiro."
        feature="os playbooks"
      />
    );
  }

  const handleCreateNew = () => {
    setEditingPlaybook(null);
    setViewMode('create');
  };

  const handleEdit = (playbook: Playbook) => {
    setEditingPlaybook(playbook);
    setViewMode('edit');
  };

  const handleCancel = () => {
    setEditingPlaybook(null);
    setViewMode('list');
  };

  const handleSubmit = async (data: PlaybookCreateData) => {
    try {
      if (editingPlaybook) {
        // Update existing playbook
        const updateData: PlaybookUpdateData = {
          name: data.name,
          description: data.description,
          is_default: data.is_default,
          steps: data.steps,
          conditions: data.conditions,
          fallback_messages: data.fallback_messages,
          situation_prompts: data.situation_prompts,
          problem_prompts: data.problem_prompts,
          implication_prompts: data.implication_prompts,
          need_payoff_prompts: data.need_payoff_prompts,
        };
        await updatePlaybook({ id: editingPlaybook.id, data: updateData });
      } else {
        // Create new playbook
        const createData: PlaybookCreateData = {
          ...data,
          client_id: selectedClient.id,
        };
        await createPlaybook(createData);
      }
      setViewMode('list');
    } catch (error) {
      // Error handling is done in the hook
      console.error('Error submitting playbook:', error);
    }
  };

  const handleDelete = async (playbook: Playbook) => {
    if (playbook.is_default) {
      alert('Não é possível excluir o playbook padrão. Defina outro playbook como padrão primeiro.');
      return;
    }

    if (confirm(`Tem certeza que deseja excluir o playbook "${playbook.name}"?`)) {
      try {
        await deletePlaybook(playbook.id);
      } catch (error) {
        // Error handling is done in the hook
        console.error('Error deleting playbook:', error);
      }
    }
  };

  const handleActivate = async (playbook: Playbook) => {
    try {
      await activatePlaybook(playbook.id);
    } catch (error) {
      // Error handling is done in the hook
      console.error('Error activating playbook:', error);
    }
  };

  const handleDeactivate = async (playbook: Playbook) => {
    try {
      await deactivatePlaybook(playbook.id);
    } catch (error) {
      // Error handling is done in the hook
      console.error('Error deactivating playbook:', error);
    }
  };

  const handleDuplicate = async (playbook: Playbook) => {
    try {
      await duplicatePlaybook(playbook.id);
    } catch (error) {
      // Error handling is done in the hook
      console.error('Error duplicating playbook:', error);
    }
  };

  if (viewMode === 'create' || viewMode === 'edit') {
    return (
      <div className="p-6">
        <PlaybookForm
          playbook={editingPlaybook || undefined}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isSubmitting={isCreating || isUpdating}
        />
      </div>
    );
  }

  return (
    <div className="p-6">
      <PlaybookList
        playbooks={playbooks}
        isLoading={isLoading}
        onCreateNew={handleCreateNew}
        onEdit={handleEdit}
        onActivate={handleActivate}
        onDeactivate={handleDeactivate}
        onDuplicate={handleDuplicate}
        onDelete={handleDelete}
        isActivating={isActivating}
        isDeactivating={isDeactivating}
        isDuplicating={isDuplicating}
        isDeleting={isDeleting}
      />
    </div>
  );
}