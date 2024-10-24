CREATE DATABASE bot_database;

-- \c bot_database;
-- \dt
-- \d tables

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8)
);

CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    group_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
