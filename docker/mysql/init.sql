-- Ensure proper charset
ALTER DATABASE hooshafza CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant permissions
GRANT ALL PRIVILEGES ON hooshafza.* TO 'hooshafza_user'@'%';
FLUSH PRIVILEGES;
