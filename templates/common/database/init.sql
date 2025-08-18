-- Database initialization script
-- This file will be executed when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types if needed
-- CREATE TYPE user_role AS ENUM ('admin', 'user', 'guest');

-- Initial schema setup
-- Tables will be created by SQLAlchemy/Alembic migrations
-- This file can be used for initial data seeding or custom database objects

-- Example: Create a default admin user (commented out)
-- INSERT INTO users (email, username, full_name, hashed_password, is_active, is_superuser)
-- VALUES ('admin@example.com', 'admin', 'Administrator', 'hashed_password_here', true, true)
-- ON CONFLICT DO NOTHING;