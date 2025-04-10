-- Create a new database for the Feedback Service
CREATE DATABASE IF NOT EXISTS is213_feedback;

-- Use the database
USE is213_feedback;

-- Create the Feedback table
CREATE TABLE Feedback (
    id INT PRIMARY KEY AUTO_INCREMENT,
    menu_item_id VARCHAR(64) NOT NULL,
    order_id VARCHAR(64) NOT NULL,
    menu_item_name VARCHAR(256) NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    tags VARCHAR(256), -- comma-separated tags
    description TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
