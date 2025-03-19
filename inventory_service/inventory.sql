CREATE DATABASE is214_inventory;
use is214_inventory;
CREATE TABLE Inventory (
    IngredientID INT PRIMARY KEY AUTO_INCREMENT,
    IngredientName VARCHAR(100) NOT NULL,
    QuantityAvailable INT NOT NULL,
    UnitOfMeasure VARCHAR(50) NOT NULL,
    ExpiryDate DATE NOT NULL,
    ReorderThreshold INT NOT NULL
);

INSERT INTO Inventory (IngredientName, QuantityAvailable, UnitOfMeasure, ExpiryDate, ReorderThreshold)
VALUES 
('Tomato', 50, 'kg', '2025-03-20', 10),
('Cheese', 20, 'kg', '2025-03-18', 5),
('Dough', 30, 'kg', '2025-03-22', 8),
('Lettuce', 15, 'kg', '2025-03-25', 5),
('Chicken', 10, 'kg', '2025-03-19', 3),
('Garlic Butter', 25, 'kg', '2025-03-21', 7);
