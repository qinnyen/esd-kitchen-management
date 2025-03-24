DROP DATABASE IF EXISTS is213_restocking;
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
    PRIMARY KEY (IngredientID, SupplierID),
    FOREIGN KEY (IngredientID) REFERENCES Ingredients(IngredientID) ON DELETE CASCADE,
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE CASCADE
);

INSERT INTO Suppliers (SupplierName, Address, ContactInfo) VALUES
('Fresh Farms', '10 Orchard Rd, Singapore', 'contact@freshfarms.com'),
('Organic Goods', '22 Raffles Ave, Singapore', 'info@organicgoods.com'),
('Global Spices', '35 Marina Bay, Singapore', 'support@globalspices.com'),
('Dairy Delight', '45 Bukit Timah Rd, Singapore', 'sales@dairydelight.com'),
('Bakery Bliss', '12 Clementi Ave, Singapore', 'orders@bakerybliss.com'),
('Poultry Palace', '30 Jurong West St, Singapore', 'info@poultrypalace.com'),
('Cheese Haven', '18 Dairy Lane, Singapore', 'orders@cheesehaven.com'),
('Lettuce Land', '5 Greenway Ave, Singapore', 'contact@lettuceland.com'),
('Tomato Express', '7 Redhill Rd, Singapore', 'sales@tomatoexpress.com');

INSERT INTO Ingredients (IngredientName) VALUES
('Tomato'), ('Cheese'), ('Dough'), ('Lettuce'), ('Chicken'), ('Garlic Butter');

INSERT INTO SupplierIngredient (IngredientID, SupplierID) VALUES
(1,1), (1,2), (1,9),  -- Tomato
(2,4), (2,7), (2,2),  -- Cheese
(4,1), (4,8), (4,2),  -- Lettuce
(3,5), (5,6), (6,3);  -- Others