-- Migration: Add token quota fields to users table
-- Run this script against your PostgreSQL database to add quota tracking

-- Add token quota columns with defaults
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS token_limit INTEGER NOT NULL DEFAULT 100000,
ADD COLUMN IF NOT EXISTS tokens_used INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS quota_reset_at TIMESTAMP;

-- Create index for efficient quota queries
CREATE INDEX IF NOT EXISTS idx_users_quota_reset ON users(quota_reset_at) 
WHERE quota_reset_at IS NOT NULL;

-- Add comment explaining the columns
COMMENT ON COLUMN users.token_limit IS 'Maximum tokens allowed per quota period (default from DEFAULT_USER_QUOTA env var)';
COMMENT ON COLUMN users.tokens_used IS 'Tokens consumed in current quota period';
COMMENT ON COLUMN users.quota_reset_at IS 'When the quota period resets and tokens_used goes back to 0';

-- Optional: Set default from environment variable using dynamic SQL
-- This requires you to run it with the env var substituted:
-- DO $$
-- BEGIN
--     EXECUTE format('ALTER TABLE users ALTER COLUMN token_limit SET DEFAULT %s', 
--                    coalesce(current_setting('app.default_user_quota', true)::int, 100000));
-- END $$;

-- Verify the changes
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('token_limit', 'tokens_used', 'quota_reset_at');
