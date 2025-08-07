-- Add message cooldown system for database-based cooldown management
-- This replaces the threading.Timer approach for serverless compatibility

CREATE TABLE message_cooldown (
    user_phone VARCHAR(50) PRIMARY KEY,
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE NOT NULL,
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_processed_at TIMESTAMP WITH TIME ZONE,
    pending_messages JSONB DEFAULT '[]'::jsonb,
    cooldown_seconds INTEGER DEFAULT 90,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_message_cooldown_client ON message_cooldown(client_id);
CREATE INDEX idx_message_cooldown_last_message ON message_cooldown(last_message_at);
CREATE INDEX idx_message_cooldown_last_processed ON message_cooldown(last_processed_at);

-- Enable RLS
ALTER TABLE message_cooldown ENABLE ROW LEVEL SECURITY;

-- RLS Policy for message cooldown (accessible by webhook - no auth required for API calls)
CREATE POLICY "Message cooldown accessible by all" ON message_cooldown
    FOR ALL USING (true);

-- Add updated_at trigger
CREATE TRIGGER update_message_cooldown_updated_at BEFORE UPDATE ON message_cooldown
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add helpful functions for cooldown management
CREATE OR REPLACE FUNCTION should_process_message(
    p_user_phone VARCHAR(50),
    p_cooldown_seconds INTEGER DEFAULT 90
) RETURNS BOOLEAN AS $$
DECLARE
    last_msg_time TIMESTAMP WITH TIME ZONE;
    time_diff_seconds INTEGER;
BEGIN
    -- Get the last message timestamp
    SELECT last_message_at INTO last_msg_time
    FROM message_cooldown
    WHERE user_phone = p_user_phone;
    
    -- If no record exists, should process (first message)
    IF last_msg_time IS NULL THEN
        RETURN TRUE;
    END IF;
    
    -- Calculate time difference in seconds
    time_diff_seconds := EXTRACT(EPOCH FROM (NOW() - last_msg_time));
    
    -- Return true if cooldown period has passed
    RETURN time_diff_seconds >= p_cooldown_seconds;
END;
$$ LANGUAGE plpgsql;