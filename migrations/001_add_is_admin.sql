-- Migration: Add is_admin column to users table
-- Date: 2025-10-12
-- Description: Adds is_admin boolean field for admin user management

-- Add is_admin column (PostgreSQL)
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE;

-- Create index for faster admin user lookups
CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin);

-- Optional: Set first user as admin (uncomment and replace 'your-username' if needed)
-- UPDATE users SET is_admin = TRUE WHERE username = 'your-username';
