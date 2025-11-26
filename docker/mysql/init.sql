-- Initialize MySQL database for multi-tenant SaaS platform
-- This script runs on first container startup

-- Set MySQL settings for optimal performance
SET GLOBAL max_connections = 200;
SET GLOBAL innodb_buffer_pool_size = 268435456; -- 256MB
SET GLOBAL innodb_log_file_size = 67108864; -- 64MB

-- Create database if not exists (already created by environment variables)
-- USE saas_platform;

-- Grant additional privileges if needed
-- GRANT ALL PRIVILEGES ON saas_platform.* TO 'saas_user'@'%';
-- FLUSH PRIVILEGES;

-- Log initialization
SELECT 'Database initialized successfully' AS status;
