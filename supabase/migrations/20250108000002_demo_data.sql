-- Insert demo data for SDR Agent

-- Insert demo user
INSERT INTO users (
    id,
    email,
    hashed_password,
    first_name,
    last_name,
    status,
    plan
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'demo@sdr-agent.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvQSG', -- password: demo123
    'Demo',
    'User',
    'active',
    'free'
);

-- Insert demo client
INSERT INTO clients (
    id,
    owner_id,
    name,
    description,
    domain,
    status,
    agent_name,
    agent_persona,
    welcome_message,
    contact_email,
    business_hours,
    evolution_api_url,
    evolution_api_key,
    evolution_instance,
    gemini_model
) VALUES (
    '660e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440000',
    'Demo Medical Clinic',
    'Demo client for testing Supabase migration',
    'demo-supabase.sdr-agent.com',
    'active',
    'Dr. Assistant',
    'Sou um assistente médico especializado em atendimento via WhatsApp, usando a metodologia SPIN Selling para qualificar leads interessados em consultas.',
    'Olá! Sou o Dr. Assistant. Como posso ajudá-lo hoje?',
    'demo@sdr-agent.com',
    '{"monday": {"open": "08:00", "close": "18:00"}, "tuesday": {"open": "08:00", "close": "18:00"}, "wednesday": {"open": "08:00", "close": "18:00"}, "thursday": {"open": "08:00", "close": "18:00"}, "friday": {"open": "08:00", "close": "17:00"}, "saturday": {"open": "09:00", "close": "13:00"}, "sunday": {"closed": true}}',
    'https://evolutionapi.centralsupernova.com.br',
    '509dbd54-c20c-4a5b-b889-a0494a861f5a',
    'client_660e8400-e29b-41d4-a716-446655440000',
    'gemini-2.0-flash'
);

-- Insert demo playbook
INSERT INTO playbooks (
    id,
    client_id,
    name,
    description,
    status,
    is_default,
    steps,
    situation_prompts,
    problem_prompts,
    implication_prompts,
    need_payoff_prompts
) VALUES (
    '770e8400-e29b-41d4-a716-446655440000',
    '660e8400-e29b-41d4-a716-446655440000',
    'Medical SPIN Selling Playbook',
    'Demo playbook for Supabase testing using SPIN methodology',
    'active',
    true,
    '[
        {"stage": "welcome", "message": "Olá! Como posso ajudá-lo?", "next": "situation"},
        {"stage": "situation", "prompt": "Descubra a situação atual do paciente", "next": "problem"},
        {"stage": "problem", "prompt": "Identifique os problemas específicos", "next": "implication"},
        {"stage": "implication", "prompt": "Explore as implicações dos problemas", "next": "need_payoff"},
        {"stage": "need_payoff", "prompt": "Apresente os benefícios da solução", "next": "close"}
    ]',
    '[
        "Há quanto tempo sente esses sintomas?",
        "Já consultou algum médico sobre isso?",
        "Como isso está afetando seu dia a dia?"
    ]',
    '[
        "Quais são os principais desconfortos?",
        "Em que momentos os sintomas pioram?",
        "O que mais te preocupa sobre essa situação?"
    ]',
    '[
        "Como isso pode evoluir se não for tratado?",
        "Que impacto isso pode ter na sua qualidade de vida?",
        "Quais riscos você vê se adiar o tratamento?"
    ]',
    '[
        "Como seria sua vida sem esses sintomas?",
        "Qual a importância de resolver isso agora?",
        "O que significaria ter um diagnóstico preciso?"
    ]'
);

-- Insert demo agent config
INSERT INTO agent_configs (
    id,
    client_id,
    name,
    is_active,
    system_prompt,
    welcome_prompt,
    fallback_prompt,
    situation_prompts,
    problem_prompts,
    implication_prompts,
    need_payoff_prompts
) VALUES (
    '880e8400-e29b-41d4-a716-446655440000',
    '660e8400-e29b-41d4-a716-446655440000',
    'Default Medical Agent Config',
    true,
    'Você é um assistente médico especializado em atendimento via WhatsApp. Use a metodologia SPIN Selling para qualificar leads interessados em consultas médicas.',
    'Olá! Sou o Dr. Assistant da Demo Medical Clinic. Como posso ajudá-lo hoje?',
    'Desculpe, não entendi sua mensagem. Pode reformular sua pergunta?',
    '[
        "Há quanto tempo sente esses sintomas?",
        "Já consultou algum médico sobre isso?",
        "Como isso está afetando seu dia a dia?"
    ]',
    '[
        "Quais são os principais desconfortos?",
        "Em que momentos os sintomas pioram?",
        "O que mais te preocupa sobre essa situação?"
    ]',
    '[
        "Como isso pode evoluir se não for tratado?",
        "Que impacto isso pode ter na sua qualidade de vida?",
        "Quais riscos você vê se adiar o tratamento?"
    ]',
    '[
        "Como seria sua vida sem esses sintomas?",
        "Qual a importância de resolver isso agora?",
        "O que significaria ter um diagnóstico preciso?"
    ]'
);

-- Insert demo messages
INSERT INTO messages (
    id,
    client_id,
    user_id,
    user_name,
    message_direction,
    content,
    timestamp,
    message_metadata,
    status,
    conversation_stage,
    lead_score
) VALUES 
(
    '990e8400-e29b-41d4-a716-446655440001',
    '660e8400-e29b-41d4-a716-446655440000',
    '5511999999999',
    'João Silva',
    'inbound',
    'Olá, estou com dores de cabeça frequentes',
    NOW() - INTERVAL '1 hour',
    '{"from_me": false, "message_id": "msg_001"}',
    'none',
    'situation',
    20
),
(
    '990e8400-e29b-41d4-a716-446655440002',
    '660e8400-e29b-41d4-a716-446655440000',
    '5511999999999',
    'Dr. Assistant',
    'outbound',
    'Olá João! Entendo sua preocupação com as dores de cabeça. Há quanto tempo você tem sentido esses sintomas?',
    NOW() - INTERVAL '59 minutes',
    '{"from_me": true, "ai_generated": true}',
    'none',
    'situation',
    20
),
(
    '990e8400-e29b-41d4-a716-446655440003',
    '660e8400-e29b-41d4-a716-446655440000',
    '5511999999999',
    'João Silva',
    'inbound',
    'Já faz umas 2 semanas, e está piorando',
    NOW() - INTERVAL '58 minutes',
    '{"from_me": false, "message_id": "msg_002"}',
    'none',
    'problem',
    40
),
(
    '990e8400-e29b-41d4-a716-446655440004',
    '660e8400-e29b-41d4-a716-446655440000',
    '5511888888888',
    'Maria Santos',
    'inbound',
    'Preciso marcar uma consulta',
    NOW() - INTERVAL '30 minutes',
    '{"from_me": false, "message_id": "msg_003"}',
    'qualified',
    'need_payoff',
    80
);