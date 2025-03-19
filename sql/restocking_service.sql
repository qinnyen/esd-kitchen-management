CREATE DATABASE is213_restocking;
USE is213_restocking;

CREATE TABLE Suppliers (
    SupplierID INT PRIMARY KEY AUTO_INCREMENT,
    SupplierName VARCHAR(255) NOT NULL,
    Address VARCHAR(255),
    ContactInfo VARCHAR(255)
);

CREATE TABLE Ingredients (
    IngredientID INT PRIMARY KEY AUTO_INCREMENT,
    IngredientName VARCHAR(255) NOT NULL
);

CREATE TABLE SupplierIngredient (
    IngredientID INT,
    SupplierID INT,
    Priority INT,
    PRIMARY KEY (IngredientID, SupplierID),
    FOREIGN KEY (IngredientID) REFERENCES Ingredients(IngredientID) ON DELETE CASCADE,
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE CASCADE
);

-- Insert mock data into Suppliers
INSERT INTO Suppliers (SupplierName, Address, ContactInfo) VALUES
('Fresh Farms', '10 Orchard Rd, Singapore', 'contact@freshfarms.com'),
('Organic Goods', '22 Raffles Ave, Singapore', 'info@organicgoods.com'),
('Global Spices', '35 Marina Bay, Singapore', 'support@globalspices.com'),
('Dairy Delight', '45 Bukit Timah Rd, Singapore', 'sales@dairydelight.com'),
('Bakery Bliss', '12 Clementi Ave, Singapore', 'orders@bakerybliss.com'),
('Poultry Palace', '30 Jurong West St, Singapore', 'info@poultrypalace.com');

-- Insert mock data into Ingredients
INSERT INTO Ingredients (IngredientName) VALUES
('Tomato'),
('Cheese'),
('Dough'),
('Lettuce'),
('Chicken'),
('Garlic Butter');

-- Insert mock data into SupplierIngredient
INSERT INTO SupplierIngredient (IngredientID, SupplierID, Priority) VALUES
-- Tomato: 2 suppliers
(1, 1, 1),  -- Fresh Farms (Priority 1)
(1, 2, 2),  -- Organic Goods (Priority 2)
-- Cheese: 1 supplier
(2, 4, 1),  -- Dairy Delight (Priority 1)
-- Dough: 1 supplier
(3, 5, 1),  -- Bakery Bliss (Priority 1)
-- Lettuce: 1 supplier
(4, 1, 1),  -- Fresh Farms (Priority 1)
-- Chicken: 1 supplier
(5, 6, 1),  -- Poultry Palace (Priority 1)
-- Garlic Butter: 1 supplier
(6, 3, 1);  -- Global Spices (Priority 1)