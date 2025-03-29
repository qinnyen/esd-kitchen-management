CREATE DATABASE is213_menu;
use is213_menu;
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
('Garlic Bread', 'Toasted bread with garlic butter', 5.00, TRUE),
(6, 'Chicken Wings', 'Crispy fried chicken wings with dipping sauce', 12, TRUE),
(7, 'Caesar Salad', 'Romaine lettuce with Caesar dressing and croutons', 9.5, TRUE),
(8, 'BBQ Ribs', 'Tender ribs with smoky barbecue sauce', 18, TRUE),
(9, 'Fish and Chips', 'Golden fried fish with crispy chips', 14, TRUE),
(10, 'Chocolate Cake', 'Rich chocolate cake with ganache topping', 6.5, TRUE);




INSERT INTO MenuIngredient (MenuItemID, IngredientID, QuantityRequired)
VALUES 
(1, 1, 0.5), -- Tomato for Margherita Pizza: 0.5 kg 
(1, 2, 0.3), -- Cheese for Margherita Pizza: 0.3 kg 
(1, 3, 0.4) -- Dough for Margherita Pizza: 0.4 kg 

(2, 1, 0.4), -- Tomato for Pepperoni Pizza: 0.4 kg 
(2, 2, 0.4), -- Cheese for Pepperoni Pizza: 0.4 kg 
(2, 3, 0.6); -- Dough for Pepperoni Pizza: 0.6 kg 

(6, 7, 0.5),   -- BBQ Sauce for Chicken Wings
(6, 1, 1.0),   -- Chicken for Chicken Wings
(6, 2, 0.5),   -- Flour for Chicken Wings

(7, 9, 0.5),   -- Romaine Lettuce for Caesar Salad
(7, 8, 0.2),   -- Croutons for Caesar Salad
(7, 3, 0.3),   -- Caesar Dressing for Caesar Salad

(8, 10, 1.5),   -- Pork Ribs for BBQ Ribs
(8, 7, 0.4),    -- BBQ Sauce for BBQ Ribs

(9, 11, 1.0),   -- Fish Fillet for Fish and Chips
(9, 12, 1.0),   -- Potatoes for Fish and Chips
(9, 13, 0.3),   -- Batter Mix for Fish and Chips

(10,14 ,0.5);   -- Chocolate Ganache For Chocolate Cake
