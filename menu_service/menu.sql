CREATE DATABASE is214_menu;

USE menu_db;

CREATE TABLE Menu (
    MenuItemID INT PRIMARY KEY AUTO_INCREMENT,
    ItemName VARCHAR(100) NOT NULL,
    Description TEXT,
    Price FLOAT NOT NULL,
    AvailabilityStatus BOOLEAN DEFAULT TRUE
);
CREATE TABLE MenuIngredient (
    MenuItemID INT NOT NULL,
    IngredientID INT NOT NULL,
    QuantityRequired FLOAT NOT NULL,
    PRIMARY KEY (MenuItemID, IngredientID)
);
INSERT INTO Menu (ItemName, Description, Price, AvailabilityStatus)
VALUES 
('Margherita Pizza', 'Classic cheese and tomato pizza', 10.00, TRUE),
('Pepperoni Pizza', 'Pepperoni and cheese pizza', 12.50, TRUE),
('Veggie Salad', 'Fresh garden vegetables with dressing', 8.00, TRUE),
('Spaghetti Bolognese', 'Pasta with rich meat sauce', 15.00, TRUE),
('Garlic Bread', 'Toasted bread with garlic butter', 5.00, TRUE);
INSERT INTO MenuIngredient (MenuItemID, IngredientID, QuantityRequired)
VALUES 
(1, 1, 0.5), -- Tomato for Margherita Pizza: 0.5 kg 
(1, 2, 0.3), -- Cheese for Margherita Pizza: 0.3 kg 
(1, 3, 0.4); -- Dough for Margherita Pizza: 0.4 kg 

INSERT INTO MenuIngredient (MenuItemID, IngredientID, QuantityRequired)
VALUES 
(2, 1, 0.4), -- Tomato for Pepperoni Pizza: 0.4 kg 
(2, 2, 0.4), -- Cheese for Pepperoni Pizza: 0.4 kg 
(2, 3, 0.6); -- Dough for Pepperoni Pizza: 0.6 kg 