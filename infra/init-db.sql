-- Initialize Octopus AI Second Brain Database
-- This script runs on first postgres container startup

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a sample admin user (password: 'admin123' - change in production!)
-- Note: This will be created by the application migration
-- Included here as reference

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE secondbrain TO secondbrain;
