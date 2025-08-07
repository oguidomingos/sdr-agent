-- Ensure message_cooldown timestamp columns are stored with timezone
ALTER TABLE message_cooldown
  ALTER COLUMN last_message_at TYPE timestamptz USING last_message_at AT TIME ZONE 'UTC',
  ALTER COLUMN last_processed_at TYPE timestamptz USING last_processed_at AT TIME ZONE 'UTC';
