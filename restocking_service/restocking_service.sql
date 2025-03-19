CREATE DATABASE restocking;
USE restocking;

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
('Global Spices', '35 Marina Bay, Singapore', 'support@globalspices.com');

-- Insert mock data into Ingredients
INSERT INTO Ingredients (IngredientName) VALUES
('Tomatoes'),
('Onions'),
('Garlic');

-- Insert mock data into SupplierIngredient
INSERT INTO SupplierIngredient (IngredientID, SupplierID, Priority) VALUES
(1, 1, 1),
(1, 2, 2),
(2, 2, 1),
(2, 3, 2),
(3, 1, 1);
