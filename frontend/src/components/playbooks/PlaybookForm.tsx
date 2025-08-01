import { useState, useEffect } from 'react';
import { X, Plus, Trash2, Save, ArrowLeft } from 'lucide-react';

import { Playbook, PlaybookCreateData } from '@/types/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';

interface PlaybookFormProps {
  playbook?: Playbook;
  onSubmit: (data: PlaybookCreateData) => Promise<void>;
  onCancel: () => void;
  isSubmitting?: boolean;
}

interface PlaybookStep {
  id: string;
  stage: string;
  message?: string;
  prompt?: string;
  next?: string;
}

export function PlaybookForm({
  playbook,
  onSubmit,
  onCancel,
  isSubmitting = false,
}: PlaybookFormProps) {
  const [formData, setFormData] = useState<PlaybookCreateData>({
    client_id: playbook?.client_id || '',
    name: playbook?.name || '',
    description: playbook?.description || '',
    is_default: playbook?.is_default || false,
    steps: playbook?.steps || [],
    conditions: playbook?.conditions || {},
    fallback_messages: playbook?.fallback_messages || [],
    situation_prompts: playbook?.situation_prompts || [],
    problem_prompts: playbook?.problem_prompts || [],
    implication_prompts: playbook?.implication_prompts || [],
    need_payoff_prompts: playbook?.need_payoff_prompts || [],
  });

  const [steps, setSteps] = useState<PlaybookStep[]>([]);
  const [newFallbackMessage, setNewFallbackMessage] = useState('');
  const [newSituationPrompt, setNewSituationPrompt] = useState('');
  const [newProblemPrompt, setNewProblemPrompt] = useState('');
  const [newImplicationPrompt, setNewImplicationPrompt] = useState('');
  const [newNeedPayoffPrompt, setNewNeedPayoffPrompt] = useState('');

  useEffect(() => {
    if (playbook?.steps) {
      const stepsWithIds = playbook.steps.map((step, index) => ({
        id: step.id || `step-${index}`,
        stage: step.stage || '',
        message: step.message || '',
        prompt: step.prompt || '',
        next: step.next || '',
      }));
      setSteps(stepsWithIds);
    } else {
      // Default steps for a new playbook
      setSteps([
        { id: 'welcome', stage: 'welcome', message: 'Olá! Como posso ajudá-lo?', next: 'situation' },
        { id: 'situation', stage: 'situation', prompt: 'Descubra a situação atual do lead', next: 'problem' },
        { id: 'problem', stage: 'problem', prompt: 'Identifique os problemas específicos', next: 'implication' },
        { id: 'implication', stage: 'implication', prompt: 'Explore as implicações dos problemas', next: 'need_payoff' },
        { id: 'need_payoff', stage: 'need_payoff', prompt: 'Apresente os benefícios da solução', next: 'close' },
      ]);
    }
  }, [playbook]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const submitData = {
      ...formData,
      steps: steps.map(step => ({
        id: step.id,
        stage: step.stage,
        message: step.message,
        prompt: step.prompt,
        next: step.next,
      })),
    };

    await onSubmit(submitData);
  };

  const addStep = () => {
    const newStep: PlaybookStep = {
      id: `step-${Date.now()}`,
      stage: '',
      message: '',
      prompt: '',
      next: '',
    };
    setSteps([...steps, newStep]);
  };

  const removeStep = (id: string) => {
    setSteps(steps.filter(step => step.id !== id));
  };

  const updateStep = (id: string, field: keyof PlaybookStep, value: string) => {
    setSteps(steps.map(step =>
      step.id === id ? { ...step, [field]: value } : step
    ));
  };

  const addPrompt = (type: 'fallback_messages' | 'situation_prompts' | 'problem_prompts' | 'implication_prompts' | 'need_payoff_prompts', value: string) => {
    if (!value.trim()) return;
    
    const currentPrompts = formData[type] || [];
    setFormData({
      ...formData,
      [type]: [...currentPrompts, value.trim()],
    });

    // Clear the input
    switch (type) {
      case 'fallback_messages':
        setNewFallbackMessage('');
        break;
      case 'situation_prompts':
        setNewSituationPrompt('');
        break;
      case 'problem_prompts':
        setNewProblemPrompt('');
        break;
      case 'implication_prompts':
        setNewImplicationPrompt('');
        break;
      case 'need_payoff_prompts':
        setNewNeedPayoffPrompt('');
        break;
    }
  };

  const removePrompt = (type: 'fallback_messages' | 'situation_prompts' | 'problem_prompts' | 'implication_prompts' | 'need_payoff_prompts', index: number) => {
    const currentPrompts = formData[type] || [];
    setFormData({
      ...formData,
      [type]: currentPrompts.filter((_, i) => i !== index),
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={onCancel}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h2 className="text-2xl font-bold text-foreground">
              {playbook ? 'Editar Playbook' : 'Novo Playbook'}
            </h2>
            <p className="text-muted-foreground">
              Configure o roteiro de conversação para qualificação de leads
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Informações Básicas</CardTitle>
            <CardDescription>
              Configure as informações básicas do playbook
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nome do Playbook</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Ex: Qualificação Médica SPIN"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Descrição</Label>
              <Textarea
                id="description"
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Descreva o objetivo e contexto deste playbook..."
                rows={3}
              />
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_default"
                checked={formData.is_default}
                onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                className="rounded border-gray-300"
              />
              <Label htmlFor="is_default">Definir como playbook padrão</Label>
            </div>
          </CardContent>
        </Card>

        {/* Tabs for different sections */}
        <Tabs defaultValue="steps" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="steps">Etapas do Fluxo</TabsTrigger>
            <TabsTrigger value="prompts">Prompts SPIN</TabsTrigger>
            <TabsTrigger value="fallbacks">Mensagens Fallback</TabsTrigger>
          </TabsList>

          {/* Steps Tab */}
          <TabsContent value="steps">
            <Card>
              <CardHeader>
                <CardTitle>Etapas do Fluxo de Conversação</CardTitle>
                <CardDescription>
                  Configure as etapas que o agente seguirá durante a conversa
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {steps.map((step, index) => (
                  <div key={step.id} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">Etapa {index + 1}</h4>
                      {steps.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeStep(step.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>ID da Etapa</Label>
                        <Input
                          value={step.stage}
                          onChange={(e) => updateStep(step.id, 'stage', e.target.value)}
                          placeholder="Ex: situation, problem..."
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Próxima Etapa</Label>
                        <Input
                          value={step.next}
                          onChange={(e) => updateStep(step.id, 'next', e.target.value)}
                          placeholder="Ex: problem, close..."
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Mensagem (se aplicável)</Label>
                      <Input
                        value={step.message || ''}
                        onChange={(e) => updateStep(step.id, 'message', e.target.value)}
                        placeholder="Mensagem direta para o usuário..."
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Prompt de Instrução</Label>
                      <Textarea
                        value={step.prompt || ''}
                        onChange={(e) => updateStep(step.id, 'prompt', e.target.value)}
                        placeholder="Instrução para o agente sobre como conduzir esta etapa..."
                        rows={2}
                      />
                    </div>
                  </div>
                ))}

                <Button type="button" variant="outline" onClick={addStep}>
                  <Plus className="mr-2 h-4 w-4" />
                  Adicionar Etapa
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* SPIN Prompts Tab */}
          <TabsContent value="prompts">
            <div className="space-y-6">
              {/* Situation Prompts */}
              <Card>
                <CardHeader>
                  <CardTitle>Prompts de Situação (S)</CardTitle>
                  <CardDescription>
                    Perguntas para descobrir a situação atual do lead
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex gap-2">
                    <Input
                      value={newSituationPrompt}
                      onChange={(e) => setNewSituationPrompt(e.target.value)}
                      placeholder="Ex: Qual é a situação atual da sua empresa?"
                    />
                    <Button
                      type="button"
                      onClick={() => addPrompt('situation_prompts', newSituationPrompt)}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="space-y-2">
                    {(formData.situation_prompts || []).map((prompt, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <Badge variant="outline" className="flex-1 justify-start">
                          {prompt}
                        </Badge>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removePrompt('situation_prompts', index)}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Problem Prompts */}
              <Card>
                <CardHeader>
                  <CardTitle>Prompts de Problema (P)</CardTitle>
                  <CardDescription>
                    Perguntas para identificar problemas específicos
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex gap-2">
                    <Input
                      value={newProblemPrompt}
                      onChange={(e) => setNewProblemPrompt(e.target.value)}
                      placeholder="Ex: Quais são os principais problemas que isso causa?"
                    />
                    <Button
                      type="button"
                      onClick={() => addPrompt('problem_prompts', newProblemPrompt)}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="space-y-2">
                    {(formData.problem_prompts || []).map((prompt, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <Badge variant="outline" className="flex-1 justify-start">
                          {prompt}
                        </Badge>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removePrompt('problem_prompts', index)}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Implication Prompts */}
              <Card>
                <CardHeader>
                  <CardTitle>Prompts de Implicação (I)</CardTitle>
                  <CardDescription>
                    Perguntas para explorar as consequências dos problemas
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex gap-2">
                    <Input
                      value={newImplicationPrompt}
                      onChange={(e) => setNewImplicationPrompt(e.target.value)}
                      placeholder="Ex: O que pode acontecer se isso não for resolvido?"
                    />
                    <Button
                      type="button"
                      onClick={() => addPrompt('implication_prompts', newImplicationPrompt)}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="space-y-2">
                    {(formData.implication_prompts || []).map((prompt, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <Badge variant="outline" className="flex-1 justify-start">
                          {prompt}
                        </Badge>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removePrompt('implication_prompts', index)}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Need-Payoff Prompts */}
              <Card>
                <CardHeader>
                  <CardTitle>Prompts de Necessidade-Benefício (N)</CardTitle>
                  <CardDescription>
                    Perguntas para apresentar o valor da solução
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex gap-2">
                    <Input
                      value={newNeedPayoffPrompt}
                      onChange={(e) => setNewNeedPayoffPrompt(e.target.value)}
                      placeholder="Ex: Como seria se vocês resolvessem esse problema?"
                    />
                    <Button
                      type="button"
                      onClick={() => addPrompt('need_payoff_prompts', newNeedPayoffPrompt)}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="space-y-2">
                    {(formData.need_payoff_prompts || []).map((prompt, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <Badge variant="outline" className="flex-1 justify-start">
                          {prompt}
                        </Badge>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removePrompt('need_payoff_prompts', index)}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Fallback Messages Tab */}
          <TabsContent value="fallbacks">
            <Card>
              <CardHeader>
                <CardTitle>Mensagens Fallback</CardTitle>
                <CardDescription>
                  Mensagens para quando o agente não souber como responder
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex gap-2">
                  <Input
                    value={newFallbackMessage}
                    onChange={(e) => setNewFallbackMessage(e.target.value)}
                    placeholder="Ex: Desculpe, não entendi. Pode reformular sua pergunta?"
                  />
                  <Button
                    type="button"
                    onClick={() => addPrompt('fallback_messages', newFallbackMessage)}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <div className="space-y-2">
                  {(formData.fallback_messages || []).map((message, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <Badge variant="outline" className="flex-1 justify-start">
                        {message}
                      </Badge>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removePrompt('fallback_messages', index)}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Submit Buttons */}
        <div className="flex items-center justify-end gap-4">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? (
              <>Salvando...</>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                {playbook ? 'Atualizar Playbook' : 'Criar Playbook'}
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}