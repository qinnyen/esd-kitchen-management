CREATE DATABASE is213_inventory;
use is213_inventory;
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
('Tomato', 5, 'kg', '2025-03-20', 10),
('Cheese', 2, 'kg', '2025-03-18', 5),
('Dough', 30, 'kg', '2025-03-22', 8),
('Lettuce', 1, 'kg', '2025-03-25', 5),
('Chicken', 10, 'kg', '2025-03-19', 3),
('Garlic Butter', 25, 'kg', '2025-03-21', 7),
('BBQ Sauce', 20, 'kg', '2025-04-01', 6),       
('Croutons', 12, 'kg', '2025-04-05', 4),        
('Romaine Lettuce', 8, 'kg', '2025-04-02', 3), 
('Pork Ribs', 15, 'kg', '2025-03-30', 5),       
('Fish Fillet', 10, 'kg', '2025-03-31', 4),     
('Potatoes', 25, 'kg', '2025-04-01', 8),      
('Batter Mix', 20, 'kg', '2025-03-30', 6),    
('Chocolate Ganache', 18, 'kg', '2025-04-05', 5), 
('Cake Base', 15, 'kg', '2025-03-29', 4);      
